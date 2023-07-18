from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from peraltas.models import ClienteColegio, RelacaoClienteResponsavel
from projetoCEU.utils import is_ajax
from .models import CadastroOrcamento, OrcamentoOpicional
from .utils import verify_data, processar_formulario
from .budget import Budget


# @csrf_exempt
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

            if req.GET.get('lista_opcionais[]'):
                opcionais = OrcamentoOpicional.objects.filter(id__in=req.GET.getlist('lista_opcionais[]'))
                opcionais_json = []

                for opcional in opcionais:
                    opcionais_json.append({
                        'id': opcional.id,
                        'nome': opcional.nome,
                        'valor': float(opcional.valor),
                        'fixo': opcional.fixo,
                    })

                return JsonResponse({'retorno': opcionais_json})
        else:
            if req.POST.get('novo_opcional'):
                valor = float(req.POST.get('valor').split(' ')[1].replace(',', '.'))

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
            # data = req.body
            # data = json.loads(data.decode('utf-8'))
            print(data, valores_op)
            # Verificar parametros obrigatórios
            if verify_data(data):
                return verify_data(data)

            # GERANDO ORÇAMENTO
            budget = Budget(data['periodo_viagem'], data['n_dias'],
                            data["hora_check_in"], data["hora_check_out"])

            if "tipo_monitoria" in data:
                budget.monitor.calc_value_monitor(data['tipo_monitoria'])

            if "minimo_pagantes" in data:  # numero de minimo_pagantes
                budget.transport.min_payers(data["minimo_pagantes"])

            if "transporte" in data:
                budget.transport.calc_value_transport(data["transporte"])

            if "opicionais" in data:
                budget.set_optional(data["opicionais"])
                budget.optional.calc_value_optional(data['opicionais'])

            # RESPOSTA
            return JsonResponse({
                "status": "success",
                "data": {
                    "periodo_viagem": budget.period.do_object(
                        percent_commission=budget.commission,
                        percent_business_fee=budget.commission
                    ),
                    "n_dias": budget.days,
                    "minimo_pagantes": budget.transport.min_payers,
                    "valores": {
                        "tipo_monitoria": budget.monitor.do_object(
                            percent_commission=budget.commission,
                            percent_business_fee=budget.commission
                        ),
                        "diaria": budget.daily_rate.do_object(
                            percent_commission=budget.commission,
                            percent_business_fee=budget.commission
                        ),
                        "transport": budget.transport.do_object(
                            percent_commission=budget.commission,
                            percent_business_fee=budget.commission
                        ),
                        "optional": budget.optional.do_object(
                            percent_commission=budget.commission,
                            percent_business_fee=budget.commission
                        )
                    },
                    "description_optional_values": budget.array_description_optional,
                    "total": {
                        "valor": 0,
                        "desconto": 0,
                        "valor_com_desconto": 0,
                        "taxa_comercial": 0,
                        "comissao_de_vendas": 0,
                    },
                    "desconto_geral": 0,
                },
                "msg": "",
            })

    if req.method != 'POST':
        cadastro_orcamento = CadastroOrcamento()

        return render(req, 'orcamento/orcamento.html', {
            'orcamento': cadastro_orcamento,
            'tipo_orcamento': req.GET.get('tipo_de_orcamento')
        })
