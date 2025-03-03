import json
from datetime import datetime, time

from cozinha.models import HorarioRefeicoes

hotcodigo_validos = ['000001', '000004', '000027']


def filtrar_reservas_por_dia(reservas, dia_especifico):
    reservas_filtradas = []

    for reserva in reservas:
        data_entrada = datetime.strptime(reserva["HORTUDATAENTRADA"], "%Y-%m-%d %H:%M:%S").date()
        data_saida = datetime.strptime(reserva["HORTUDATASAIDA"], "%Y-%m-%d %H:%M:%S").date()

        if data_entrada <= dia_especifico <= data_saida:
            reservas_filtradas.append(reserva)

    return reservas_filtradas


def filtrar_reservas_por_hotcodigo():
    with open('.\\reservas.json', 'r', encoding='utf-8') as arquivo:
        reservas = json.load(arquivo)
        reservas_filtradas = [
            reserva for reserva in reservas if reserva["K_HOTCODIGO"] in hotcodigo_validos or reserva["K_HOTCODIGO_01"] in hotcodigo_validos
        ]

    return reservas_filtradas


def determinar_refeicoes(reserva, refeicoes, dia_especifico):
    checkin = datetime.strptime(reserva["HORTUDATAENTRADA"], "%Y-%m-%d %H:%M:%S")
    checkout = datetime.strptime(reserva["HORTUDATASAIDA"], "%Y-%m-%d %H:%M:%S")
    horario_checkin = datetime.strptime(reserva["HORTUDATAENTRADA"], "%Y-%m-%d %H:%M:%S").time()
    horario_checkout = datetime.strptime(reserva["HORTUDATASAIDA"], "%Y-%m-%d %H:%M:%S").time()
    refeicoes_reserva = []

    if checkin.date() < dia_especifico < checkout.date():
        return [refeicao.refeicao for refeicao in refeicoes]

    for refeicao in refeicoes:
        if checkin.date() == dia_especifico:
            if refeicao.hora_final >= horario_checkin:
                refeicoes_reserva.append(refeicao.refeicao)
        else:
            if refeicao.hora_final <= horario_checkout:
                refeicoes_reserva.append(refeicao.refeicao)

    return refeicoes_reserva


def somar_pessoas_por_refeicao(dia_especifico, reservas):
    refeicoes = HorarioRefeicoes.objects.filter(hospedagem=True).order_by('hora_inicio', 'hora_final')
    soma_refeicoes = {refeicao.refeicao: {"adultos": 0, "criancas": 0, "monitores": 0, "total": 0} for refeicao in refeicoes}

    for reserva in reservas:
        refeicoes_reserva = determinar_refeicoes(reserva, refeicoes, dia_especifico)

        for refeicao in refeicoes_reserva:
            soma_refeicoes[refeicao]["adultos"] += reserva["HORTUQUANTIDADEADULTO"]
            soma_refeicoes[refeicao]["criancas"] += reserva["HORTUQUANTIDADECRIANCA"]
            soma_refeicoes[refeicao]["monitores"] += 0
            soma_refeicoes[refeicao]["total"] += reserva["HORTUQUANTIDADEADULTO"] + reserva["HORTUQUANTIDADECRIANCA"]

    return soma_refeicoes


def filtrar_refeicoes(dia_especifico):
    reservas_filtradas = filtrar_reservas_por_hotcodigo()
    reservas_filtradas = filtrar_reservas_por_dia(reservas_filtradas, dia_especifico)
    soma_refeicoes = somar_pessoas_por_refeicao(dia_especifico, reservas_filtradas)
    max_adultos = max([refeicao["adultos"] for refeicao in soma_refeicoes.values()])
    max_criancas = max([refeicao["criancas"] for refeicao in soma_refeicoes.values()])

    return soma_refeicoes, max_adultos, max_criancas
