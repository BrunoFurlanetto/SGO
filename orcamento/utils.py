from datetime import datetime, timedelta
import re

from django.http import JsonResponse

from peraltas.models import ProdutosPeraltas
from .mock import mock_optional
from .models import OrcamentoOpicional, HorariosPadroes, OrcamentoPeriodo


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
    valores_opcionais = {}
    gerencia = {}
    outros = []
    op_extras = 0
    orcamento = {}
    padrao_orcamento = r'orcamento\[(\w+)\]'
    padrao_valores_op = r'dados_op\[(\w+)\]'
    padrao_gerencia = r'gerencia\[(\w+)\]'
    padrao_outros = re.compile('.*outros.*')

    for key in dados.keys():
        if padrao_outros.match(key):
            op_extras += 1 / 4

    if op_extras > 0:
        orcamento['outros'] = compilar_outros(dados, int(op_extras))

    for key, valor in dados.items():
        correspondencia_orcamento = re.match(padrao_orcamento, key)
        correspondencia_valores_op = re.match(padrao_valores_op, key)
        correspondencia_gerencia = re.match(padrao_gerencia, key)

        if correspondencia_orcamento:
            if 'opcionais' in key or 'outros' in key or 'atividades' in key:
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
        time_in_all = HorariosPadroes.objects.filter(entrada_saida=1)
        time_in = time_in_all.filter(horario__gte=hour_check_in).order_by('horario')
        time_out_all = HorariosPadroes.objects.filter(entrada_saida=0)
        time_out = time_out_all.filter(horario__lte=hour_check_out).order_by('-horario')

        if len(time_in) == 0:
            time_error = time_in_all.order_by('-horario')[0]
            return JsonError(f'O ultimo horário de check-in valido é {time_error.horario}')

        if len(time_out) == 0:
            time_error = time_out_all.order_by('horario')[0]
            return JsonError(f'O ultimo horário de check-out valido é {time_error.horario}')

        # Do period list
        period_days = []
        days_list = []
        current_date = date_check_in

        while current_date <= date_check_out:
            days_list.append(current_date)

            try:
                period = OrcamentoPeriodo.objects.get(
                    inicio_vigencia__lte=current_date, 
                    final_vigencia__gte=current_date,
                    dias_semana_validos__in=[current_date.weekday()]
                )
            except OrcamentoPeriodo.DoesNotExist:
                return JsonError(f'Não foi encontrado tarifario para essa data, por favor peça o cadastro para a data: {current_date} a diretoria')
            else:
                period_days.append(period)
                current_date += timedelta(days=1)

        # Calc num days
               
        num_days = len(period_days)
        # Get ID for hours, Num Days And IDs for Periods:
        orcamento['hora_check_in'] = (time_in[0]).id
        orcamento['hora_check_out'] = (time_out[0]).id
        orcamento['n_dias'] = num_days
        orcamento['periodo_viagem'] = period_days
        orcamento['lista_de_dias'] = days_list
        orcamento['check_in'] = datetime.strptime(checks[0], '%d/%m/%Y %H:%M').astimezone().strftime('%Y-%m-%d %H:%M')
        orcamento['check_out'] = datetime.strptime(checks[1], '%d/%m/%Y %H:%M').astimezone().strftime('%Y-%m-%d %H:%M')

        try:
            only_sky = ProdutosPeraltas.objects.filter(pk=orcamento['produto'], produto__icontains='ceu').exists()
        except ValueError:
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
            'id': dados[f'outros[{i}][id]'],
            'nome': dados[f'outros[{i}][nome]'],
            'valor': float(dados[f'outros[{i}][valor]'].replace(',', '.')),
            'descricao': dados[f'outros[{i}][descricao]'],
        })

    return outros
