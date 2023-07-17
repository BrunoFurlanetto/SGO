from django.http import JsonResponse
from .mock import mock_optional
from .models import OrcamentoOpicional


def JsonError(msg):
    return JsonResponse({
        "status": "error",
        "data": {},
        "msg": msg
    }, status=422)


def verify_data(data):
    if not "periodo_viagem" in data:
        return JsonError("É necessario informar o 'periodo' como parametro!")

    if not "n_dias" in data:
        return JsonError("É necessario informar a 'quantidade de dias' da estada!")

    # if data['days'] < 2:
    #     return JsonError("No minimo 2 dias na")

    if not "hora_check_in" in data:
        return JsonError("É necessario informar a hora de chegada do evento")

    if not "hora_check_out" in data:
        return JsonError("É necessario informar a hora de saida!")
