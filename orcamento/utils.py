from datetime import datetime, timedelta
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
    gerencia = {}
    padrao_orcamento = r'orcamento\[(\w+)\]'
    padrao_valores_op = r'dados_op\[(\w+)\]'
    padrao_gerencia = r'gerencia\[(\w+)\]'

    for key, valor in dados.items():
        correspondencia_orcamento = re.match(padrao_orcamento, key)
        correspondencia_valores_op = re.match(padrao_valores_op, key)
        correspondencia_gerencia = re.match(padrao_gerencia, key)

        if correspondencia_orcamento:
            if 'opcionais' in key or 'outros' in key:
                orcamento[correspondencia_orcamento.group(1)] = list(map(int, dados.getlist(key)))
            else:
                orcamento[correspondencia_orcamento.group(1)] = valor

        if correspondencia_valores_op:
            lista = []

            for i, item in enumerate(dados.getlist(key)):
                if i == 0:
                    lista.append(int(item))
                else:
                    lista.append(float(item.replace(',', '.')))

            valores_opcionais[correspondencia_valores_op.group(1)] = lista

        if correspondencia_gerencia:
            if 'observacoes' in key:
                gerencia[correspondencia_gerencia.group(1)] = valor
            elif key == 'minimo_onibus':
                gerencia[correspondencia_gerencia.group(1)] = int(valor)
            else:
                try:
                    gerencia[correspondencia_gerencia.group(1)] = float(valor.replace('%', '').replace(',', '.'))
                except ValueError:
                    gerencia[correspondencia_gerencia.group(1)] = valor

    return {'orcamento': orcamento, 'valores_op': valores_opcionais, 'gerencia': gerencia}


def verificar_gerencia(dados):
    data_pagamento_padrao = datetime.today() + timedelta(days=15)
    descontos = [
        dados['desconto_produto'],
        dados['desconto_monitoria'],
        dados['desconto_trasnporte'],
        dados['desconto_geral'],
    ]

    for desconto in descontos:
        if desconto != 0.00:
            return True

    if dados['comissao'] != 9.0 or dados['taxa_comercial'] != 5.0 or dados['minimo_onibus'] != 30.0:
        return True

    if dados['data_pagamento'] != data_pagamento_padrao.strftime('%Y-%m-%d'):
        return True
