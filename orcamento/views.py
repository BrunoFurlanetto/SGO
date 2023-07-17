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
            # ----------------------------------------------------------------------------------------------------------
            # Apenas para teste provisório front. TODO: Tirar do fluxo
            if req.POST.get('periodo_viagem'):
                estadia = int(req.POST.get('n_dias'))
                valor_periodo = float(OrcamentoPeriodo.objects.get(
                    id=req.POST.get('periodo_viagem')).valor) * estadia
                return JsonResponse({'status': True, 'valor_etapa': f'{valor_periodo:.2f}'.replace('.', ',')})

            if req.POST.get('tipo_monitoria'):
                valor_monitoria = float(OrcamentoMonitor.objects.get(
                    pk=req.POST.get('tipo_monitoria')).valor) * estadia

                if req.POST.get('transporte') == 'sim':
                    valor_transporte = 50 * estadia
                else:
                    valor_transporte = 0
                return JsonResponse({'status': True, 'valor_etapa': f'{valor_monitoria + valor_transporte:.2f}'.replace('.', ',')})
            # ----------------------------------------------------------------------------------------------------------
            # data = req.body
            # data = json.loads(data.decode('utf-8'))

            # Verificar parametros obrigatórios
            if verify_data(data):
                return verify_data(data)

            # GERANDO ORÇAMENTO
            budget = Budget(data['periodo_viagem'], data['n_dias'],
                            data["hora_check_in"], data["hora_check_out"])

            if "participantes" in data:  # numero de participantes
                budget.set_pax(data["participantes"])

            if "tipo_monitoria" in data:
                budget.set_monitor(data['tipo_monitoria'])

            if "transporte" in data:
                budget.set_transport(data["transporte"])

            if "opicionais[]" in data:
                budget.add_optional(data['opicionais[]'])

            if "outros[]" in data:
                budget.add_others(data['outros[]'])

            # RESPOSTA
            return JsonResponse({
                "status": "success",
                "data": {
                    "period": budget.get_period_id(),
                    "days": budget.get_days(),
                    "pax": budget.get_pax(),
                    "description_values": {
                        "monitor": budget.get_monitor(),
                        "meal": budget.get_meal(),
                        "transport": budget.get_transport(),
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
