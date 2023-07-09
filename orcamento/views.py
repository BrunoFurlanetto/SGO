from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
import json

from peraltas.models import ClienteColegio, RelacaoClienteResponsavel
from projetoCEU.utils import is_ajax
from .models import CadastroOrcamento
from .utils import verify_data
from .budget import Budget


# @csrf_exempt
def calc_budget(req):
    print(is_ajax(req))
    if is_ajax(req):
        if req.method == 'GET':
            cliente = ClienteColegio.objects.get(pk=req.GET.get('id_cliente'))

            try:
                relacoes = RelacaoClienteResponsavel.objects.get(cliente=cliente)
            except RelacaoClienteResponsavel.DoesNotExist:
                return JsonResponse({'responsaveis': []})
            else:
                return JsonResponse({'responsaveis': [responsavel.id for responsavel in relacoes.responsavel.all()]})
        else:
            # JSON
            print(req.POST)
            data = req.POST
            # data = req.body
            # data = json.loads(data.decode('utf-8'))

            # Verificar parametros obrigatórios
            if verify_data(data):
                return verify_data(data)

            # GERANDO ORÇAMENTO
            budget = Budget(data['period'], data['days'], data["comming"], data["exit"])
            value_monitor = 0
            value_transport = 0

            if "pax" in data:  # numero de participantes
                budget.set_pax(data["pax"])

            if "monitor" in data:
                value_monitor = budget.monitor(data['monitor'])

            if "transport" in data:
                if data['transport']:
                    value_transport = budget.transport()

            if "optional" in data:
                budget.add_optional(data['optional'])

            if "others" in data:
                budget.add_others(data['others'])

            value_meal = budget.meal()

            # RESPOSTA
            return JsonResponse({
                "status": "success",
                "data": {
                    "period": budget.get_period_id(),
                    "days": budget.get_days(),
                    "pax": budget.get_pax(),
                    "description_values": {
                        "monitor": value_monitor,
                        "meal": value_meal,
                        "transport": value_transport,
                        "optional": budget.som_optional()
                    },
                    "description_optional_values": budget.get_optional(),
                    "total": budget.get_total()
                },
                "msg": "",
            })

    if req.method != 'POST':
        cadastro_orcamento = CadastroOrcamento()

        return render(req, 'orcamento/orcamento.html', {
            'orcamento': cadastro_orcamento,
            'tipo_orcamento': req.GET.get('tipo_de_orcamento')
        })
