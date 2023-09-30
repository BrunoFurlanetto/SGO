import math
# ------------------------- Funções relacionadas ao salvamento das atividades -------------------------------
from ceu.models import Atividades, Professores


def requisicao_ajax(requisicao):
    if requisicao.get('campo') == 'professor':
        professores_db = Professores.objects.all()
        professores = {}

        for professor in professores_db:
            professores[professor.id] = professor.usuario.get_full_name()

        return professores

    if requisicao.get('campo') == 'atividade':
        if requisicao.get('publico'):
            atividades_db = Atividades.objects.filter(publico=True)
        else:
            atividades_db = Atividades.objects.all()
        atividades = {}

        for atividade in atividades_db:
            atividades[atividade.id] = atividade.atividade

        return atividades


def salvar_atividades(dados, relatorio):
    dados_atividade = {}
    i = 1

    while True:
        participantes = teste_participantes_por_atividade(dados)

        if dados.getlist(f'ativ_{i}', None):
            professores = [
                int(id_professor) for id_professor in dados.getlist(f'professores_ativ_{i}') if id_professor != ''
            ]
            inicio = dados.getlist(f"ativ_{i}")[0]

            # ---------------------- Teste pra saber a atividade que está sendo adcionada -------------------------------
            if dados.get('participantes_confirmados', None):
                if int(dados.get('participantes_confirmados')) > 65 and \
                        float(dados.get('participantes_confirmados')) % 2 != 0:
                    if i % 2 == 1:
                        participantes = participantes
                    else:
                        participantes = participantes + 1
            else:
                if int(dados.get('participantes_previa')) > 65 and \
                        float(dados.get('participantes_previa')) % 2 != 0:
                    if i % 2 == 1:
                        participantes = participantes
                    else:
                        participantes = participantes + 1

            if i == 5:
                if dados.get('participantes_confirmados', None):
                    participantes = int(dados.get('participantes_confirmados'))
                else:
                    participantes = int(dados.get('participantes_previa'))
            # -----------------------------------------------------------------------------------------------------------

            dados_atividade[f'atividade_{i}'] = {
                'atividade': int(dados.getlist(f'ativ_{i}')[1]),
                'professores': professores,
                'inicio': inicio,
                'participantes': participantes
            }
        else:
            break

        i += 1
    print(dados_atividade)
    relatorio.atividades = dados_atividade


def teste_participantes_por_atividade(dados):
    if dados.getlist('ativ_1')[0] == dados.getlist('ativ_2')[0]:
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
    professores = {'coordenador': int(dados.get('coordenador'))}

    for professor_id, i in enumerate(dados.getlist('professores'), start=2):
        professores[f'professor_{i}'] = int(professor_id)

    relatorio.equipe = professores
# -----------------------------------------------------------------------------------------------------------
