import re

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


def processar_formulario(dados):
    orcamento = {}
    valores_opcionais = {}
    padrao_orcamento = r'orcamento\[(\w+)\]'
    padrao_valores_op = r'dados_op\[(\w+)\]'

    for key, valor in dados.items():
        correspondencia_orcamento = re.match(padrao_orcamento, key)
        correspondencia_valores_op = re.match(padrao_valores_op, key)

        if correspondencia_orcamento:
            if len(dados.getlist(key)) > 1:
                orcamento[correspondencia_orcamento.group(1)] = list(map(int, dados.getlist(key)))
            else:
                orcamento[correspondencia_orcamento.group(1)] = valor

        elif correspondencia_valores_op:
            lista = []

            for i, item in enumerate(dados.getlist(key)):
                if i == 0:
                    lista.append(int(item))
                else:
                    lista.append(float(item.replace(',', '.')))

            valores_opcionais[correspondencia_valores_op.group(1)] = lista

    return {'orcamento': orcamento, 'valores_op': valores_opcionais}
