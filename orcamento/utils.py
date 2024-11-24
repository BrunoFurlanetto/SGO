from datetime import datetime, timedelta
import re

from django.contrib.auth.models import User
from django.http import JsonResponse

from peraltas.models import ProdutosPeraltas
from .mock import mock_optional
from .models import OrcamentoOpicional, HorariosPadroes, OrcamentoPeriodo, TiposDePacote, Orcamento, OrcamentoMonitor, \
    ValoresTransporte


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


def processar_formulario(dados, user):
    valores_opcionais = {}
    gerencia = {}
    # outros = []
    op_extras = 0
    orcamento = {}
    padrao_orcamento = r'orcamento\[(\w+)\]'
    padrao_valores_op = r'dados_op\[(\w+)\]'
    padrao_gerencia = r'gerencia\[(\w+)\]'
    padrao_extra = r'opcionais_extra\[(\w+)\]'

    for key in dados.keys():
        if re.match(padrao_extra, key):
            op_extras += 1 / 4

    if op_extras > 0:
        orcamento['opcionais_extra'] = compilar_outros(dados, int(op_extras))

    for key, valor in dados.items():
        correspondencia_orcamento = re.match(padrao_orcamento, key)
        correspondencia_valores_op = re.match(padrao_valores_op, key)
        correspondencia_gerencia = re.match(padrao_gerencia, key)

        if correspondencia_orcamento:
            if 'opcionais' in key:
                try:
                    orcamento[correspondencia_orcamento.group(1)] = list(map(int, dados.getlist(key)))
                except ValueError:
                    ...
            else:
                orcamento[correspondencia_orcamento.group(1)] = valor

        if correspondencia_valores_op and 'extra' not in key:
            lista = []

            for i, item in enumerate(dados.getlist(key)):
                print(i, item, key)
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

            if 'alterado' in key:
                gerencia[correspondencia_gerencia.group(1)] = bool(int(valor))

    # Tratamento de informações apartir do campo data_viagem
    if "data_viagem" in orcamento and orcamento['data_viagem'] != '':
        checks = orcamento['data_viagem'].split(' - ')
        check_in_complete = checks[0].split(' ')
        check_out_complete = checks[1].split(' ')

        # convert str to time obj
        hour_check_in = datetime.strptime(check_in_complete[1], '%H:%M').time()
        hour_check_out = datetime.strptime(check_out_complete[1], '%H:%M').time()

        # Convert str to date obj
        date_check_in = datetime.strptime(check_in_complete[0], '%d/%m/%Y').date()
        date_check_out = datetime.strptime(check_out_complete[0], '%d/%m/%Y').date()

        # filter check_in and check_out
        try:
            time_in = HorariosPadroes.objects.get(
                horario__lte=hour_check_in,
                final_horario__gte=hour_check_in,
                entrada_saida=True,
            )
        except HorariosPadroes.DoesNotExist:
            return JsonError(f'Horário de check in informado não permitido!')

        try:
            time_out = HorariosPadroes.objects.get(
                horario__lte=hour_check_out,
                final_horario__gte=hour_check_out,
                entrada_saida=False,
            )
        except HorariosPadroes.DoesNotExist:
            return JsonError(f'Horário de check out informado não permitido!')

        # Do period list
        period_days = []
        days_list = []
        current_date = date_check_in
        usuario_financeiro = User.objects.filter(pk=user.id, groups__name__icontains='financeiro').exists()

        if not OrcamentoPeriodo.verificar_validade(date_check_in, date_check_out, usuario_financeiro):
            return JsonError(
                f'Não foi encontrado tarifario para as datas solicitadas, por favor peça o cadastro a diretoria.'
            )

        if not OrcamentoMonitor.verificar_validade(date_check_in, date_check_out, usuario_financeiro):
            return JsonError(
                f'Não foi encontrado tarifario de monitoria para as datas solicitadas, por favor peça o cadastro a diretoria.'
            )

        if not ValoresTransporte.verificar_validade(date_check_in, date_check_out, usuario_financeiro):
            return JsonError(
                f'Não foi encontrado tarifario de monitoria para as datas solicitadas, por favor peça o cadastro a diretoria.'
            )

        while current_date <= date_check_out:
            days_list.append(current_date)

            if usuario_financeiro:
                period = OrcamentoPeriodo.objects.get(
                    inicio_vigencia__lte=current_date,
                    final_vigencia__gte=current_date,
                    dias_semana_validos__in=[current_date.weekday()],
                    liberado=True
                )
            else:
                period = OrcamentoPeriodo.objects.get(
                    inicio_vigencia__lte=current_date,
                    final_vigencia__gte=current_date,
                    dias_semana_validos__in=[current_date.weekday()]
                )

            period_days.append(period)
            current_date += timedelta(days=1)

        num_days = len(period_days)
        # Racionais entrada e saída refeição TODO: Retirar depois dos testes do Sérgio
        orcamento['racional_check_in'] = time_in.racional
        orcamento['racional_check_out'] = time_out.racional
        # Get ID for hours, Num Days And IDs for Periods:
        orcamento['hora_check_in'] = time_in.id
        orcamento['hora_check_out'] = time_out.id
        orcamento['n_dias'] = num_days
        orcamento['periodo_viagem'] = period_days
        orcamento['lista_de_dias'] = days_list
        orcamento['check_in'] = datetime.strptime(checks[0], '%d/%m/%Y %H:%M').astimezone().strftime('%Y-%m-%d %H:%M')
        orcamento['check_out'] = datetime.strptime(checks[1], '%d/%m/%Y %H:%M').astimezone().strftime('%Y-%m-%d %H:%M')

        try:
            only_sky = TiposDePacote.objects.filter(pk=orcamento['tipo_de_pacote'], so_ceu=True).exists()
        except ValueError:
            only_sky = False
        except KeyError:
            only_sky = False

        orcamento['only_sky'] = only_sky

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


def compilar_outros(dados, op_extras):
    outros = []

    for i in range(0, op_extras):
        outros.append({
            'id': dados[f'opcionais_extra[{i}][id]'],
            'nome': dados[f'opcionais_extra[{i}][nome]'],
            'valor': float(dados[f'opcionais_extra[{i}][valor]'].replace(',', '.')),
            'descricao': dados[f'opcionais_extra[{i}][descricao]'],
        })

    return outros
