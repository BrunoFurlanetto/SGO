
def juntar_equipe(os):
    equipe = str(os.coordenador)

    if os.professor_2:
        equipe += f', {os.professor_2}'

    if os.professor_3:
        equipe += f', {os.professor_3}'

    if os.professor_4:
        equipe += f', {os.professor_4}'

    return equipe


def contar_atividades(os):
    n_atividades = 1
    atividades = [os.atividade_1]
    professores = []
    horas = [os.hora_atividade_1]

    profs = str(os.prf_1_atv_1)

    if os.prf_2_atv_1:
        profs += f', {os.prf_2_atv_1}'
    if os.prf_3_atv_1:
        profs += f', {os.prf_3_atv_1}'
    if os.prf_4_atv_1:
        profs += f', {os.prf_4_atv_1}'

    professores.append(profs)

    if os.atividade_2:
        n_atividades += 1
        atividades.append(os.atividade_2)

    profs = str(os.prf_1_atv_2)

    if os.prf_2_atv_2:
        profs += f', {os.prf_2_atv_2}'
    if os.prf_3_atv_2:
        profs += f', {os.prf_3_atv_2}'
    if os.prf_4_atv_2:
        profs += f', {os.prf_4_atv_2}'

    professores.append(profs)
    horas.append(os.hora_atividade_2)

    if os.atividade_3:
        n_atividades += 1
        atividades.append(os.atividade_3)

        profs = str(os.prf_1_atv_3)

        if os.prf_2_atv_3:
            profs += f', {os.prf_2_atv_3}'
        if os.prf_3_atv_3:
            profs += f', {os.prf_3_atv_3}'
        if os.prf_4_atv_3:
            profs += f', {os.prf_4_atv_3}'

        professores.append(profs)
        horas.append(os.hora_atividade_3)

    if os.atividade_4:
        n_atividades += 1
        atividades.append(os.atividade_4)

        profs = str(os.prf_1_atv_4)

        if os.prf_2_atv_4:
            profs += f', {os.prf_2_atv_4}'
        if os.prf_3_atv_4:
            profs += f', {os.prf_3_atv_4}'
        if os.prf_4_atv_4:
            profs += f', {os.prf_4_atv_4}'

        professores.append(profs)
        horas.append(os.hora_atividade_4)

    if os.atividade_5:
        n_atividades += 1
        atividades.append(os.atividade_5)

        profs = str(os.prf_1_atv_5)

        if os.prf_2_atv_5:
            profs += f', {os.prf_2_atv_5}'
        if os.prf_3_atv_5:
            profs += f', {os.prf_3_atv_5}'
        if os.prf_4_atv_5:
            profs += f', {os.prf_4_atv_5}'

        professores.append(profs)
        horas.append(os.hora_atividade_5)

    return n_atividades, atividades, horas, professores
