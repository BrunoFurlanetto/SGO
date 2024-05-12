import unidecode

from peraltas.models import Disciplinas


def ranqueamento_atividades(atividades_ceu, atividades_peraltas, id_series, ids_temas_interesse, id_pacotes):
    infos_atividades_ceu = []
    infos_atividades_peralas = []

    if atividades_ceu:
        for atividade in atividades_ceu:
            infos_atividade = atividade.informacoes_atividade()
            disciplinas_trabalhadas = []
            pontuacao = 0

            pontuacao += len([serie for serie in atividade.serie.all() if serie.id in id_series])
            pontuacao += len([pacote for pacote in atividade.tipo_pacote.all() if pacote.id in id_pacotes])

            for disciplina in atividade.disciplinas.all():
                if disciplina not in disciplinas_trabalhadas and disciplina != atividade.disciplina_primaria:
                    disciplinas_trabalhadas.append(disciplina)

            pontuacao += len(disciplinas_trabalhadas) / 2
            pontuacao += 1 if atividade.disciplina_primaria.id in ids_temas_interesse else 0

            infos_atividade['pontuacao'] = pontuacao
            infos_atividades_ceu.append(infos_atividade)

    if atividades_peraltas:
        for atividade in atividades_peraltas:
            infos_atividade = atividade.informacoes_atividade()
            disciplinas_trabalhadas = []
            pontuacao = 0

            pontuacao += len([serie.id for serie in atividade.serie.all() if serie.id in id_series])
            pontuacao += len([pacote.id for pacote in atividade.tipo_pacote.all() if pacote.id in id_pacotes])

            for disciplina in atividade.disciplinas.all():
                if disciplina not in disciplinas_trabalhadas and disciplina != atividade.disciplina_primaria:
                    disciplinas_trabalhadas.append(disciplina)

            pontuacao += len(disciplinas_trabalhadas) / 2
            pontuacao += 1 if atividade.disciplina_primaria.id in ids_temas_interesse else 0

            infos_atividade['pontuacao'] = pontuacao
            infos_atividades_peralas.append(infos_atividade)

    atividades_ranqueadas = {
        'ceu': sorted(infos_atividades_ceu, key=lambda k: k['pontuacao'], reverse=True),
        'peraltas': sorted(infos_atividades_peralas, key=lambda k: k['pontuacao'], reverse=True),
    }
    print(Disciplinas.listar_cores())
    return {'atividades_ranqueadas': atividades_ranqueadas, 'cores': Disciplinas.listar_cores()}
