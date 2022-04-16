import datetime

from ceu.models import Atividades, Locaveis


def salvar_atividades_ceu(dados, ficha_de_evento):
    dados_atividade = {}
    n_atividades = 0

    for chave in dados.keys():
        if 'atividade_' in chave:
            n_atividades += 1

    if n_atividades == 0:
        return

    for i in range(1, n_atividades + 1):
        dados_atividade[f'atividade_{i}'] = {
            'atividade': str(Atividades.objects.get(pk=dados.get(f'atividade_{i}'))),
            'data_e_hora': dados.get(f'data_hora_{i}').replace('T', ' '),
            'participantes': int(dados.get(f'participantes_{i}')),
            'serie': dados.get(f'serie_participantes_{i}')
        }

    ficha_de_evento.atividades_ceu = dados_atividade
    return


def check_in_and_check_out_atividade(ficha_de_evento):

    if ficha_de_evento.atividades_ceu is not None:
        ficha_de_evento.check_in_ceu = ficha_de_evento.atividades_ceu[f'atividade_1']['data_e_hora']
        atividade_cadastrada = Atividades.objects.get(atividade=ficha_de_evento.atividades_ceu[f'atividade_1']['atividade'])
        duracao = atividade_cadastrada.duracao
        hora_ultima_atividade = datetime.datetime.strptime(
            ficha_de_evento.atividades_ceu[f'atividade_{len(ficha_de_evento.atividades_ceu)}']['data_e_hora'],
            '%Y-%m-%d %H:%M')
        ficha_de_evento.check_out_ceu = hora_ultima_atividade + duracao
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
            'espaco': str(Locaveis.objects.get(local__id=int(dados.get(f'locacao_{i}')))),
            'check_in': dados.get(f'entrada_{i}').replace('T', ' '),
            'check_out': dados.get(f'saida_{i}').replace('T', ' '),
            'local_coffee': dados.get(f'local-coffee_{i}'),
            'hora_coffee': dados.get(f'hora-coffee_{i}'),
            'participantes': int(dados.get(f'participantes-loc_{i}')),
        }

    ordem_de_servico.locacao_ceu = dados_locacao
    ordem_de_servico.check_in_ceu = dados.get(f'entrada_1').replace('T', ' ')
    ordem_de_servico.check_out_ceu = dados.get(f'saida_{n_locacoes}').replace('T', ' ')

    return
