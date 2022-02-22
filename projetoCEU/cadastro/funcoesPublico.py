from datetime import datetime


def salvar_atividades(dados, relatorio):
    print('Foi')

    if dados.get('atividade_1') != '':
        atividade = dados.get('ativ1')
        professores = pegar_professores(dados)
        data_e_hora = 2222

        if dados.get('participantes_confirmados', None):
            participantes = int(dados.get('participantes_confirmados'))
        else:
            participantes = int(dados.get('participantes_previa'))

        dados_atividade = {'atividade_1': {'atividade': atividade, 'professores': professores,
                                           'data_e_hora': data_e_hora, 'participantes': participantes}
                           }

        relatorio.atividades = dados_atividade
        print(relatorio.atividades)
    else:
        return


def pegar_professores(dados):
    professores = []

    for d in dados:
        if 'atv1' in d and dados[d] is not None:
            professores.append(dados[d])

    return professores


def formatar_data_e_hora():
    a = 1
    b = 2

    return a, b
