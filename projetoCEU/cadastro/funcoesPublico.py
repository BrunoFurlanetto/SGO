import math
# ------------------------- Funções relacionadas ao salvamento das atividades -------------------------------
from ceu.models import Atividades, Professores


def salvar_atividades(dados, relatorio):
    dados_atividade = {}
    participantes = teste_participantes_por_atividade(dados)
    print(dados)

    for i in range(1, 6):

        if dados.get(f'ativ{i}') is not None or dados.get(f'ativ{i}') != '':
            print(dados.get(f'ativ{i}'))
            professores = pegar_professores(dados, i)
            data_e_hora = f'{dados.get("data_atendimento")} {dados.get(f"horaAtividade_{i}")}'

# ---------------------- Teste pra saber a atividade que está sendo adcionada -------------------------------
            if dados.get('participantes_confirmados', None):
                if int(dados.get('participantes_confirmados')) > 67 and \
                        float(dados.get('participantes_confirmados')) % 2 != 0:
                    if i == 1 or i == 3:
                        participantes = participantes + 1
                    elif i == 2 or i == 4:
                        participantes = participantes - 1
            else:
                if int(dados.get('participantes_previa')) > 67 and \
                        float(dados.get('participantes_previa')) % 2 != 0:
                    if i == 1 or i == 3:
                        participantes = participantes + 1
                    elif i == 2 or i == 4:
                        participantes = participantes - 1

            if i == 5:
                if dados.get('participantes_confirmados', None):
                    participantes = int(dados.get('participantes_confirmados'))
                else:
                    participantes = int(dados.get('participantes_previa'))
# -----------------------------------------------------------------------------------------------------------

            dados_atividade[f'atividade_{i}'] = {'atividade': int(dados.get(f'ativ{i}')), 'professores': professores,
                                                 'data_e_hora': data_e_hora, 'participantes': participantes}

    relatorio.atividades = dados_atividade

# -----------------------------------------------------------------------------------------------------------


def pegar_professores(dados, j):
    professores = []

    for d in dados:
        if f'atv{j}' in d and dados[d] != '':
            professor = Professores.objects.get(id=int(dados[d]))
            professores.append(professor.id)

    return professores
# -----------------------------------------------------------------------------------------------------------


def teste_participantes_por_atividade(dados):

    if dados.get('horaAtividade_1') == dados.get('horaAtividade_2'):

        if dados.get('participantes_confirmados', None):
            return math.floor(float(dados.get('participantes_confirmados')) / 2)
        else:
            return math.floor(float(dados.get('participantes_previa')) / 2)

    else:

        if dados.get('participantes_confirmados', None):
            return math.floor(float(dados.get('participantes_confirmados')))
        else:
            return math.floor(float(dados.get('participantes_previa')))

# -----------------------------------------------------------------------------------------------------------


# -------------------------- Funções pra pegar a equipe escalada no atendimento -----------------------------
def salvar_equipe(dados, relatorio):
    coordenador = Professores.objects.get(id=int(dados.get('coordenador')))
    professores = {'coordenador': coordenador.id}

    for i in range(2, 5):
        if dados.get(f'professor_{i}') != '':
            professor = Professores.objects.get(id=int(dados.get(f'professor_{i}')))
            professores[f'professor_{i}'] = professor.id

    relatorio.equipe = professores
# -----------------------------------------------------------------------------------------------------------
