import datetime

from ceu.models import Atividades, Locaveis
from peraltas.models import AtividadesEco


def slavar_atividades_ecoturismo(dados, ordem_de_servico):
    dados_atividade = {}
    n_atividades = 0

    for chave in dados.keys():
        if 'atividade_eco_' in chave:
            n_atividades += 1

    if n_atividades == 0:
        return

    for i in range(1, n_atividades + 1):
        dados_atividade[f'atividade_{i}'] = {
            'atividade': int(dados.get(f'atividade_eco_{i}')),
            'data_e_hora': dados.get(f'data_hora_eco_{i}').replace('T', ' '),
            'participantes': int(dados.get(f'participantes_eco_{i}')) if dados.get(f'participantes_eco_{i}') != '' else '',
            'serie': dados.get(f'serie_participantes_eco_{i}'),
            'biologo': int(dados.get(f'biologo_eco_{i}')) if dados.get(f'biologo_eco_{i}') != '' else ''
        }

    ordem_de_servico.atividades_eco = dados_atividade
    return


def salvar_atividades_ceu(dados, ficha_de_evento):
    dados_atividade = {}
    n_atividades = 0

    for chave in dados.keys():
        if 'atividade_' in chave and 'eco' not in chave:
            n_atividades += 1

    if n_atividades == 0:
        return

    for i in range(1, n_atividades + 1):
        a_definir = Atividades.objects.get(atividade__icontains='definir').id

        dados_atividade[f'atividade_{i}'] = {
            'atividade': int(dados.get(f'atividade_{i}')) if dados.get(f'atividade_{i}') != '' else a_definir,
            'data_e_hora': dados.get(f'data_hora_{i}').replace('T', ' '),
            'participantes': int(dados.get(f'participantes_{i}')) if dados.get(f'participantes_{i}') != '' else '',
            'serie': dados.get(f'serie_participantes_{i}')
        }

    ficha_de_evento.atividades_ceu = dados_atividade
    return


def check_in_and_check_out_atividade(ordem_de_servico):

    if ordem_de_servico.atividades_ceu is not None:
        # --------------------- Verificar a data e hora de check in e chek out no CEU ----------------------------------
        check_in = datetime
        check_out = []

        for i in range(1, len(ordem_de_servico.atividades_ceu) + 1):
            try:
                data = datetime.datetime.strptime(ordem_de_servico.atividades_ceu[f'atividade_{i}']['data_e_hora'],
                                                  '%Y-%m-%d %H:%M')
            except ValueError:
                ordem_de_servico.check_in_ceu = ordem_de_servico.ficha_de_evento.check_in
                ordem_de_servico.check_out_ceu = ordem_de_servico.ficha_de_evento.check_out

                return

            print('----------', data)
            if i == 1:
                check_in = data
                check_out.append(data)
                check_out.append(ordem_de_servico.atividades_ceu[f'atividade_{i}']['atividade'])
            elif check_in > data:
                check_in = data

            if check_out[0] < data:
                check_out[0] = data
                check_out[1] = ordem_de_servico.atividades_ceu[f'atividade_{i}']['atividade']
        # --------------------------------------------------------------------------------------------------------------

        ordem_de_servico.check_in_ceu = check_in
        atividade_cadastrada = Atividades.objects.get(id=int(check_out[1]))
        duracao = atividade_cadastrada.duracao
        ordem_de_servico.check_out_ceu = check_out[0] + duracao
    else:
        return


def salvar_locacoes_ceu(dados, ordem_de_servico):
    dados_locacao = {}
    n_locacoes = 0

    for chave in dados.keys():
        if 'locacao_' in chave:
            n_locacoes += 1

    if n_locacoes == 0:
        return

    for i in range(1, n_locacoes + 1):
        dados_locacao[f'locacao_{i}'] = {
            'espaco': int(dados.get(f'locacao_{i}')),
            'check_in': dados.get(f'entrada_{i}').replace('T', ' '),
            'check_out': dados.get(f'saida_{i}').replace('T', ' '),
            'local_coffee': dados.get(f'local-coffee_{i}'),
            'hora_coffee': dados.get(f'hora-coffee_{i}'),
            'participantes': int(dados.get(f'participantes-loc_{i}')) if dados.get(f'participantes-loc_{i}') != '' else '',
        }

    ordem_de_servico.locacao_ceu = dados_locacao
    ordem_de_servico.check_in_ceu = dados.get(f'entrada_1').replace('T', ' ') if dados.get(f'entrada_1') != '' else dados.get('check_in')
    ordem_de_servico.check_out_ceu = dados.get(f'saida_{n_locacoes}').replace('T', ' ')  if dados.get(f'saida_{n_locacoes}') != '' else dados.get('check_out')

    return
