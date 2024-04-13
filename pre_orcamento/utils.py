import unidecode

cores_temas = {
    "Planetário": "#003366",
    "Observação": "#336699",
    "Astronomia": "#3366cc",
    "Geologia": "#ffa664",
    "Física": "#6699cc",
    "Astronáutica": "#336666",
    "Água": "#336633",
    "Fazendinha": "#666633",
    "Meio ambiente": "#666666",
    "Eclusa": "#999999",
    "Fazenda de café": "#663300",
    "Formatura": "#660000"
}


def ranqueamento_atividades(atividades_ceu, atividades_peraltas, id_series, id_temas_ceu, id_temas_peraltas, id_pacotes):
    infos_atividades_ceu = []
    infos_atividades_peralas = []

    if atividades_ceu:
        for atividade in atividades_ceu:
            infos_atividade = atividade.informacoes_atividade()
            pontuacao = 0

            pontuacao += len([serie for serie in atividade.serie.all() if serie.id in id_series])
            pontuacao += len([pacote for pacote in atividade.tipo_pacote.all() if pacote.id in id_pacotes])
            pontuacao += 1 if atividade.tema_atividade.id in id_temas_ceu else 0

            infos_atividade['pontuacao'] = pontuacao
            infos_atividade['cor'] = cores_temas[atividade.tema_atividade.tipo_atividade]
            infos_atividades_ceu.append(infos_atividade)

    if atividades_peraltas:
        for atividade in atividades_peraltas:
            infos_atividade = atividade.informacoes_atividade()
            pontuacao = 0

            pontuacao += len([serie.id for serie in atividade.serie.all() if serie.id in id_series])
            pontuacao += len([pacote.id for pacote in atividade.tipo_pacote.all() if pacote.id in id_pacotes])
            pontuacao += 1 if atividade.tipo_atividade.id in id_temas_peraltas else 0

            infos_atividade['pontuacao'] = pontuacao
            infos_atividade['cor'] = cores_temas[atividade.tipo_atividade.tipo_atividade]
            infos_atividades_peralas.append(infos_atividade)

    atividades_ranqueadas = {
        'ceu': sorted(infos_atividades_ceu, key=lambda k: k['pontuacao'], reverse=True),
        'peraltas': sorted(infos_atividades_peralas, key=lambda k: k['pontuacao'], reverse=True),
    }

    return atividades_ranqueadas
