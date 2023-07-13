from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
import json

from peraltas.models import ClienteColegio, RelacaoClienteResponsavel
from projetoCEU.utils import is_ajax
from .models import CadastroOrcamento, OrcamentoOpicional, OrcamentoPeriodo, OrcamentoMonitor
from .utils import verify_data
from .budget import Budget


# @csrf_exempt
def calc_budget(req):
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
            if req.POST.get('novo_opcional'):
                valor = float(req.POST.get('valor').split(' ')[1].replace(',', '.'))
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
            # ----------------------------------------------------------------------------------------------------------
            # Apenas para teste provisório front. TODO: Tirar do fluxo
            if req.POST.get('periodo_viagem'):
                estadia = int(req.POST.get('n_dias'))
                valor_periodo = float(OrcamentoPeriodo.objects.get(id=req.POST.get('periodo_viagem')).valor) * estadia
                return JsonResponse({'status': True, 'valor_etapa': f'{valor_periodo:.2f}'.replace('.', ',')})

            if req.POST.get('tipo_monitoria'):
                valor_monitoria = float(OrcamentoMonitor.objects.get(pk=req.POST.get('tipo_monitoria')).valor) * estadia

                if req.POST.get('transporte') == 'sim':
                    valor_transporte = 50 * estadia
                else:
                    valor_transporte = 0
                return JsonResponse({'status': True, 'valor_etapa': f'{valor_monitoria + valor_transporte:.2f}'.replace('.', ',')})

            if req.POST.get('id_opcionais[]'):
                valor_etapa = 0.00

                for id_opcional in req.POST.getlist('id_opcionais[]'):
                    valor_etapa += float(OrcamentoOpicional.objects.get(pk=id_opcional).valor)

                return JsonResponse({'status': True, 'valores': f'{valor_etapa:.2f}'.replace('.', ',')})

            # ----------------------------------------------------------------------------------------------------------
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
