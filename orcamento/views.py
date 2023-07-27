from django.http import JsonResponse, HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from peraltas.models import ClienteColegio, RelacaoClienteResponsavel, Vendedor
from projetoCEU.utils import is_ajax
from .models import CadastroOrcamento, OrcamentoOpicional, Orcamento
from .utils import verify_data, processar_formulario, verificar_gerencia
from .budget import Budget


def calc_budget(req):
    if is_ajax(req):
        if req.method == 'GET':
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

            if req.GET.get('id_opcional'):
                opcional = OrcamentoOpicional.objects.get(pk=req.GET.get('id_opcional'))
                return JsonResponse({'fixo': opcional.fixo, 'valor': opcional.valor})
        else:
            if req.POST.get('novo_opcional'):
                valor = float(req.POST.get('valor').replace(',', '.'))

                try:
                    novo_op = OrcamentoOpicional.objects.create(
                        nome=req.POST.get('novo_opcional'),
                        valor=valor,
                        descricao=req.POST.get('descricao'),
                    )
                    novo_op.save()
                except Exception as e:
                    return JsonResponse({'adicionado': False, 'erro': e})
                else:
                    return JsonResponse({'adicionado': True, 'text': novo_op.nome, 'id': novo_op.id})

            # JSON
            dados = processar_formulario(req.POST)
            data = dados['orcamento']
            valores_op = dados['valores_op']
            gerencia = dados['gerencia']
            opt_data = []
            # data = req.body
            # data = json.loads(data.decode('utf-8'))
            print(gerencia)
            # Verificar parametros obrigatórios
            if verify_data(data):
                return verify_data(data)

            # GERANDO ORÇAMENTO
            budget = Budget(data['periodo_viagem'], data['n_dias'],
                            data["hora_check_in"], data["hora_check_out"])

            if "taxa_comercial" in data:
                budget.set_business_fee(data["taxa_comercial"])

            if "comissao_de_vendas" in data:
                budget.set_commission(data["comissao_de_vendas"])

            if "desconto_periodo_viagem" in data:
                budget.period.set_discount(data["desconto_periodo_viagem"])

            if "desconto_diarias" in data:
                budget.daily_rate.set_discount(data["desconto_diarias"])

            if "tipo_monitoria" in data and data['tipo_monitoria'] != '':
                budget.monitor.calc_value_monitor(data['tipo_monitoria'])

            if "desconto_tipo_monitoria" in data:
                budget.monitor.set_discount(data["desconto_tipo_monitoria"])

            if "minimo_pagantes" in data:  # numero de minimo_pagantes
                budget.transport.min_payers(data["minimo_pagantes"])

            if "transporte" in data:
                budget.transport.calc_value_transport(data["transporte"])

            if "desconto_transporte" in data:
                budget.transport.set_discount(data["desconto_transporte"])

            if "opcionais" in data:
                opt_data = [[opt, 0, 0, 0] for opt in data['opcionais']]

            if "outros" in data:
                other_data = [[opt, 0, 0, 0] for opt in data['outros']]
                for other in other_data:
                    opt_data.append(other)

            if len(opt_data) > 0:
                budget.set_optional(opt_data, False)
                budget.optional.calc_value_optional(budget.array_description_optional)

            if len(valores_op) > 0:
                print(valores_op)
                opt_data = [opt for opt in valores_op.values()]
                print(opt_data)
                budget.set_optional(opt_data)
                budget.optional.calc_value_optional(budget.array_description_optional)


            # CAlCULAR TOTAL
            budget.total.calc_total_value(
                monitor=budget.monitor,
                period=budget.period,
                optional=budget.optional,
                daily_rate=budget.daily_rate,
                transport=budget.transport,
            )
            # RESPOSTA

            if req.POST.get('salvar') == 'true':
                try:
                    dados['orcamento']['valor'] = f'{budget.total.value:.2f}'  # TODO: Alterar para valor com desconto quando a API estiver pronta
                    orcamento = CadastroOrcamento(dados['orcamento'])
                    pre_orcamento = orcamento.save(commit=False)
                    pre_orcamento.objeto_gerencia = dados['gerencia']
                    pre_orcamento.objeto_orcamento = budget.return_object()
                    pre_orcamento.necessita_aprovacao_gerencia = budget.total.general_discount != 0
                    pre_orcamento.aprovado = budget.total.general_discount == 0
                    pre_orcamento.colaborador = req.user
                    orcamento.save()
                except Exception as e:
                    return JsonResponse({
                        "status": "error",
                        "data": budget.return_object(),
                        "msg": e,
                    })
                else:
                    return JsonResponse({
                        "status": "success",
                        "msg": "",
                    })
            else:
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

@csrf_exempt
def teste_orcamento(req):
    # JSON
    dados = processar_formulario(req.POST)
    data = dados['orcamento']
    valores_op = dados['valores_op']
    gerencia = dados['gerencia']
    # data = req.body
    # data = json.loads(data.decode('utf-8'))
    print(gerencia)
    # Verificar parametros obrigatórios
    if verify_data(data):
        return verify_data(data)

    # GERANDO ORÇAMENTO
    budget = Budget(data['periodo_viagem'], data['n_dias'],
                    data["hora_check_in"], data["hora_check_out"])

    if "taxa_comercial" in data:
        budget.set_business_fee(data["taxa_comercial"])

    if "comissao_de_vendas" in data:
        budget.set_commission(data["comissao_de_vendas"])

    if "desconto_periodo_viagem" in data:
        budget.period.set_discount(data["desconto_periodo_viagem"])

    if "desconto_diarias" in data:
        budget.daily_rate.set_discount(data["desconto_diarias"])

    if "tipo_monitoria" in data and data['tipo_monitoria'] != '':
        budget.monitor.calc_value_monitor(data['tipo_monitoria'])

    if "desconto_tipo_monitoria" in data:
        budget.monitor.set_discount(data["desconto_tipo_monitoria"])

    if "minimo_pagantes" in data:  # numero de minimo_pagantes
        budget.transport.min_payers(data["minimo_pagantes"])

    if "transporte" in data:
        budget.transport.calc_value_transport(data["transporte"])

    if "desconto_transporte" in data:
        budget.transport.set_discount(data["desconto_transporte"])

    if "opcionais" in data:
        opt_data = [[opt, 0, 0] for opt in data['opcionais']]
        budget.set_optional(opt_data)
        budget.optional.calc_value_optional(budget.array_description_optional)

    if len(valores_op) > 0:
        print(valores_op)
        opt_data = [opt for opt in valores_op.values()]
        print(opt_data)
        budget.set_optional(opt_data)
        budget.optional.calc_value_optional(budget.array_description_optional)

    # CAlCULAR TOTAL
    budget.total.calc_total_value(
        monitor=budget.monitor,
        period=budget.period,
        optional=budget.optional,
        daily_rate=budget.daily_rate,
        transport=budget.transport,
    )
    # RESPOSTA
