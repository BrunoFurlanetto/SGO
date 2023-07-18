from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
import json

from peraltas.models import ClienteColegio, RelacaoClienteResponsavel
from projetoCEU.utils import is_ajax
from .models import CadastroOrcamento, OrcamentoOpicional, OrcamentoPeriodo, OrcamentoMonitor
from .utils import verify_data
from .budget import Budget


# @csrf_exempt  # comentar antes do git
def calc_budget(req):
    global estadia

    if is_ajax(req):
        if req.method == 'GET':
            cliente = ClienteColegio.objects.get(pk=req.GET.get('id_cliente'))

            try:
                relacoes = RelacaoClienteResponsavel.objects.get(
                    cliente=cliente)
            except RelacaoClienteResponsavel.DoesNotExist:
                return JsonResponse({'responsaveis': []})
            else:
                return JsonResponse({'responsaveis': [responsavel.id for responsavel in relacoes.responsavel.all()]})
        else:
            if req.POST.get('novo_opcional'):
                valor = float(req.POST.get('valor').split(' ')
                              [1].replace(',', '.'))
                print(valor)
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
            data = req.POST
            print(data)
            # req.POST.get("periodo_viagem")
            # data = req.body
            # data = json.loads(data.decode('utf-8'))

            # Verificar parametros obrigatórios
            if verify_data(data):
                return verify_data(data)

            # GERANDO ORÇAMENTO
            budget = Budget(data['periodo_viagem'], data['n_dias'],
                            data["hora_check_in"], data["hora_check_out"])

            if "tipo_monitoria" in data:
                budget.monitor.calc_value_monitor(data['tipo_monitoria'])

            if "minimo_pagantes" in data:  # numero de minimo_pagantes
                budget.tranport.min_payers(data["minimo_pagantes"])

            if "transporte" in data:
                budget.tranport.calc_value_trasport(data["transporte"])

            if "opicionais" in data:
                budget.set_optional(data["opicionais"])
                budget.optional.calc_value_optional(data['opicionais'])

            # RESPOSTA
            return JsonResponse({
                "status": "success",
                "data": {
                    "periodo_viagem": budget.period.object,
                    "n_dias": budget.days,
                    "minimo_pagantes": budget.tranport.min_payers,
                    "valores": {
                        "tipo_monitoria": budget.monitor.object,
                        "diaria": budget.daily_rate.object,
                        "transport": budget.tranport.object,
                        "optional": budget.optional.object
                    },
                    "description_optional_values": budget.array_description_optional,
                    "total": 0
                },
                "msg": "",
            })

    if req.method != 'POST':
        cadastro_orcamento = CadastroOrcamento()

        return render(req, 'orcamento/orcamento.html', {
            'orcamento': cadastro_orcamento,
            'tipo_orcamento': req.GET.get('tipo_de_orcamento')
        })
