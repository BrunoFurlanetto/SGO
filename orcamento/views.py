import datetime
import json
from itertools import chain

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from ceu.models import Atividades
from peraltas.models import ClienteColegio, RelacaoClienteResponsavel, Vendedor, ProdutosPeraltas, AtividadesEco, \
    AtividadePeraltas
from projetoCEU.envio_de_emails import EmailSender
from projetoCEU.utils import is_ajax
from .models import CadastroOrcamento, OrcamentoOpicional, Orcamento, StatusOrcamento
from .utils import verify_data, processar_formulario, verificar_gerencia
from .budget import Budget


@login_required(login_url='login')
def calc_budget(req):
    if is_ajax(req):
        if req.method == 'GET':
            if req.GET.get('check_in') and req.GET.get('check_out'):
                check_in = datetime.datetime.strptime(req.GET.get('check_in'), '%d/%m/%Y %H:%M')
                check_out = datetime.datetime.strptime(req.GET.get('check_out'), '%d/%m/%Y %H:%M')
                n_pernoites = (check_out.date() - check_in.date()).days
                produtos = list(chain(ProdutosPeraltas.objects.filter(n_dias=n_pernoites)))
                produtos.append(ProdutosPeraltas.objects.get(produto__icontains='all party'))

                if n_pernoites == 0:
                    produtos.append(ProdutosPeraltas.objects.get(produto__icontains='ceu'))
                    produtos.append(ProdutosPeraltas.objects.get(produto__icontains='visita técnica'))

                if n_pernoites >= 2:
                    produtos.append(ProdutosPeraltas.objects.get(produto__icontains='ac 3 dias ou mais'))

                return JsonResponse({'ids': [produto.id for produto in produtos]})

            if req.GET.get('id_cliente'):
                cliente = ClienteColegio.objects.get(pk=req.GET.get('id_cliente'))

                try:
                    relacoes = RelacaoClienteResponsavel.objects.get(cliente=cliente)
                except RelacaoClienteResponsavel.DoesNotExist:
                    return JsonResponse({'responsaveis': []})
                else:
                    return JsonResponse({
                        'responsaveis': [responsavel.id for responsavel in relacoes.responsavel.all()]
                    })

            if req.GET.get('nome_id'):
                if req.GET.get('nome_id') == 'id_opcionais':
                    selecao = OrcamentoOpicional.objects.get(pk=req.GET.get('id'))
                elif req.GET.get('nome_id') == 'id_atividades':
                    selecao = AtividadesEco.objects.get(id=req.GET.get('id'))
                else:
                    selecao = Atividades.objects.get(id=req.GET.get('id'))

                return JsonResponse({'valor': selecao.valor})
        else:
            dados = processar_formulario(req.POST)

            if 'orcamento' not in dados:
                return dados

            data = dados['orcamento']
            valores_op = dados['valores_op']
            gerencia = dados['gerencia']
            opt_data = []
            act_data = []
            act_sky_data = []
            # Verificar parametros obrigatórios
            if verify_data(data):
                return verify_data(data)
            
            # GERANDO ORÇAMENTO
            budget = Budget(data['periodo_viagem'], data['n_dias'], data["hora_check_in"],
                            data["hora_check_out"], data["lista_de_dias"])
            # TAXAS
            budget.set_commission(gerencia["comissao"] / 100) if "comissao" in gerencia else ...
            budget.set_business_fee(gerencia["taxa_comercial"] / 100) if "taxa_comercial" in gerencia else ...
            budget.transport.set_min_payers(data["minimo_pagantes"]) if "minimo_pagantes" in data else ...
            budget.transport.set_min_payers(gerencia["minimo_onibus"]) if "minimo_onibus" in gerencia else ...
            budget.set_business_fee(data["taxa_comercial"]) if "taxa_comercial" in data else ...
            budget.set_commission(data["comissao_de_vendas"]) if "comissao_de_vendas" in data else ...
            # budget.period.set_discount(gerencia["desconto_produto"]) if "desconto_produto" in gerencia else ...
            budget.period.set_discount(data["desconto_periodo_viagem"]) if "desconto_periodo_viagem" in data else ...
            budget.daily_rate.set_discount(data["desconto_diarias"]) if "desconto_diarias" in data else ...
            budget.daily_rate.set_discount(gerencia["desconto_produto"]) if "desconto_produto" in gerencia else ...
            budget.monitor.calc_value_monitor(data['tipo_monitoria'])
            budget.monitor.set_discount(gerencia["desconto_monitoria"]) if "desconto_monitoria" in gerencia else ...
            budget.monitor.set_discount(data["desconto_tipo_monitoria"]) if "desconto_tipo_monitoria" in gerencia else ...
            budget.transport.calc_value_transport(data.get("transporte"))
            budget.transport.set_discount(gerencia["desconto_transporte"]) if "desconto_transporte" in gerencia else ...
            budget.transport.set_discount(data["desconto_transporte"]) if "desconto_transporte" in data else ...
            budget.total.set_discount(gerencia["desconto_geral"]) if "desconto_geral" in gerencia else ...

            # OPICIONAIS
            if len(valores_op) == 0:
                if "opcionais" in data:
                    opt_data = [[opt, 0, 0, 0] for opt in data['opcionais']]

                if "atividades" in data:
                    act_data = [[act, 0, 0, 0] for act in data["atividades"]]

                if "atividades_ceu" in data:
                    act_sky_data = [[act, 0, 0, 0] for act in data["atividades_ceu"]]
            else:
                for key, value in valores_op.items():
                    if  'opcional' in key:
                        opt_data.append(value)
                    elif 'peraltas' in key:
                        act_data.append(value)
                    elif 'ceu' in key:
                        act_sky_data.append(value)


            budget.set_optional(opt_data)
            budget.optional.calc_value_optional(budget.array_description_optional)
            budget.set_activities(act_data)
            budget.activities.calc_value_optional(budget.array_description_activities)
            budget.set_activities_sky(act_sky_data)
            budget.activities_sky.calc_value_optional(budget.array_description_activities_sky)
            budget.set_others(data.get("outros"))
            budget.others.calc_value_optional(budget.array_description_others)

            # CAlCULAR TOTAL
            budget.total.calc_total_value(
                monitor=budget.monitor,
                period=budget.period,
                optional=budget.optional,
                others=budget.others,
                activities=budget.activities,
                activities_sky=budget.activities_sky,
                daily_rate=budget.daily_rate,
                transport=budget.transport,
                days=data["n_dias"],
            )

            if req.POST.get('salvar') == 'true':
                try:
                    valor_final = budget.total.calc_value_with_discount() + budget.total.calc_business_fee(
                        budget.business_fee) + budget.total.calc_commission(budget.commission)
                    data['valor'] = f'{valor_final:.2f}'
                    data['opcionais_extra'] = data['outros']
                    data['data_vencimento'] = datetime.date.today() + datetime.timedelta(days=10)
                    data['status_orcamento'] = StatusOrcamento.objects.get(status__contains='aberto').id

                    orcamento = CadastroOrcamento(data)
                    pre_orcamento = orcamento.save(commit=False)
                    pre_orcamento.objeto_gerencia = dados['gerencia']
                    pre_orcamento.objeto_orcamento = budget.return_object()

                    if budget.total.general_discount != 0 or dados['gerencia'][
                        'data_pagamento'] != datetime.datetime.today().date() + datetime.timedelta(days=15):
                        pre_orcamento.necessita_aprovacao_gerencia = True

                    pre_orcamento.colaborador = req.user
                    orcamento_salvo = orcamento.save()
                except Exception as e:
                    return JsonResponse({
                        "status": "error",
                        "data": budget.return_object(),
                        "msg": e,
                    })
                else:
                    diretoria = User.objects.filter(groups__name__icontains='Diretoria')
                    lista_emails = set()

                    for colaborador in diretoria:
                        lista_emails.add(colaborador.email)
                    lista_emails.add('bruno.furlanetto@hotmail.com')
                    EmailSender(lista_emails).orcamento_aprovacao(orcamento_salvo.id)
                    return JsonResponse({
                        "status": "success",
                        "msg": "",
                    })
            else:
                # RESPONSE BUDGET CLASS
                return JsonResponse({
                    "status": "success",
                    "data": budget.return_object(),
                    "msg": "",
                })

    if req.method != 'POST':
        cadastro_orcamento = CadastroOrcamento()

        return render(req, 'orcamento/orcamento.html', {
            'orcamento': cadastro_orcamento,
            'tipo_orcamento': req.GET.get('tipo_de_orcamento')
        })
