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

        # --------------------- Verificar a data e hora de check in e chek out no CEU ----------------------------------
        check_in = datetime
        check_out = []
        for i in range(1, len(ficha_de_evento.atividades_ceu) + 1):
            data = datetime.datetime.strptime(ficha_de_evento.atividades_ceu[f'atividade_{i}']['data_e_hora'],
                                              '%Y-%m-%d %H:%M')

            if i == 1:
                check_in = data
                check_out.append(data)
                check_out.append(ficha_de_evento.atividades_ceu[f'atividade_{i}']['atividade'])
            elif check_in > data:
                check_in = data

            if check_out[0] < data:
                check_out[0] = data
                check_out[1] = ficha_de_evento.atividades_ceu[f'atividade_{i}']['atividade']
        # --------------------------------------------------------------------------------------------------------------

        ficha_de_evento.check_in_ceu = check_in
        print(ficha_de_evento.check_in_ceu)
        atividade_cadastrada = Atividades.objects.get(atividade=check_out[1])
        duracao = atividade_cadastrada.duracao
        ficha_de_evento.check_out_ceu = check_out[0] + duracao
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
            'espaco': str(Locaveis.objects.get(id=int(dados.get(f'locacao_{i}')))),
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
