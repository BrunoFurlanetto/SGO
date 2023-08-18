from calendar import monthrange
from datetime import datetime, timedelta

from django.db.models import Q

from ordemDeServico.models import OrdemDeServico
from peraltas.models import FichaDeEvento


def gerar_lotacao(mes, ano):
    lista_pessoas_datas = {}
    mes_anterior = mes - 1 if mes != 1 else 12
    mes_proximo = mes + 1 if mes != 12 else 1
    meses = [mes_anterior, mes, mes_proximo]

    for loop, _mes in enumerate(meses):
        if loop == 0 and mes == 1:
            _ano = ano - 1
        elif loop == 2 and mes == 12:
            _ano = ano + 1
        else:
            _ano = ano

        ultimo_dia_mes = monthrange(_ano, _mes)[1]

        ordens_mes_ano = OrdemDeServico.objects.filter(
            Q(check_in__month=_mes) | Q(check_out__month=_mes),
            Q(check_in__year=_ano) | Q(check_out__year=_ano),
        )
        fichas_mes_ano = FichaDeEvento.objects.filter(os=False).filter(
            Q(check_in__month=_mes) | Q(check_out__month=_mes),
            Q(check_in__year=_ano) | Q(check_out__year=_ano),
            pre_reserva=False
        )
        pre_reservas_mes = FichaDeEvento.objects.filter(os=False).filter(
            Q(check_in__month=_mes) | Q(check_out__month=_mes),
            Q(check_in__year=_ano) | Q(check_out__year=_ano),
            pre_reserva=True
        )

        for dia in range(1, ultimo_dia_mes + 1):
            _data = datetime(year=_ano, month=_mes, day=dia).date()
            n_pessoas_confirmadas = n_pessoas_reservadas = 0

            for ordem in ordens_mes_ano:
                if ordem.check_in.date() <= _data <= ordem.check_out.date():
                    n_pessoas_confirmadas += ordem.n_participantes
                    n_pessoas_confirmadas += ordem.n_professores if ordem.n_professores else 0

            for ficha in fichas_mes_ano:
                if ficha.check_in.date() <= _data <= ficha.check_out.date():
                    convidados = ficha.qtd_convidada if ficha.qtd_convidada else 0
                    confirmados = ficha.qtd_confirmada if ficha.qtd_confirmada else 0
                    confirmados += ficha.qtd_professores if ficha.qtd_professores else 0
                    n_pessoas_confirmadas += confirmados

                    if convidados - confirmados > 0:
                        n_pessoas_reservadas = convidados - confirmados
                    else:
                        n_pessoas_reservadas = 0



            for pre_reserva in pre_reservas_mes:
                if pre_reserva.check_in.date() <= _data <= pre_reserva.check_out.date():
                    n_pessoas_reservadas += pre_reserva.qtd_convidada if pre_reserva.qtd_convidada else 0

            lista_pessoas_datas[f'{datetime(_ano, _mes, dia).strftime("%Y-%m-%d")}'] = {
                'confirmadas': n_pessoas_confirmadas,
                'reservadas': n_pessoas_reservadas,
                'total': n_pessoas_confirmadas + n_pessoas_reservadas
            }

    return lista_pessoas_datas
