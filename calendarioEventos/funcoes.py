from calendar import monthrange
from datetime import datetime, timedelta

from ordemDeServico.models import OrdemDeServico
from peraltas.models import FichaDeEvento


def gerar_lotacao(mes, ano):
    lista_pessoas_datas = {}
    ultimo_dia_mes = monthrange(int(ano), int(mes))[1]
    ordens_mes_ano = OrdemDeServico.objects.filter(check_in__month=int(mes), check_in__year=int(ano))
    fichas_mes_ano = FichaDeEvento.objects.filter(os=False).filter(
        check_in__month=int(mes),
        check_in__year=int(ano),
        pre_reserva=False
    )
    pre_reservas_mes = FichaDeEvento.objects.filter(os=False).filter(
        check_in__month=int(mes),
        check_in__year=int(ano),
        pre_reserva=True
    )

    for dia in range(1, ultimo_dia_mes + 1):
        n_pessoas_confirmadas = n_pessoas_reservadas = 0

        for ordem in ordens_mes_ano:
            if ordem.check_in.day <= dia <= ordem.check_out.day:
                n_pessoas_confirmadas += ordem.n_participantes
                n_pessoas_confirmadas += ordem.n_professores if ordem.n_professores else 0

        for ficha in fichas_mes_ano:
            if ficha.check_in.day <= dia <= ficha.check_out.day:
                n_pessoas_confirmadas += ficha.qtd_confirmada if ficha.qtd_confirmada else 0
                n_pessoas_confirmadas += ficha.qtd_professores if ficha.qtd_professores else 0
                convidadas = ficha.qtd_convidada if ficha.qtd_convidada else 0
                confirmadas = ficha.qtd_confirmada if ficha.qtd_confirmada else 0
                n_pessoas_reservadas += abs(confirmadas - convidadas) if confirmadas <= convidadas else 0

        for pre_reserva in pre_reservas_mes:
            if pre_reserva.check_in.day <= dia <= pre_reserva.check_out.day:
                n_pessoas_reservadas += pre_reserva.qtd_convidada if pre_reserva.qtd_convidada else 0

        lista_pessoas_datas[f'{dia}'] = {
            'confirmadas': n_pessoas_confirmadas,
            'reservadas': n_pessoas_reservadas,
            'total': n_pessoas_confirmadas + n_pessoas_reservadas
        }

    return lista_pessoas_datas
