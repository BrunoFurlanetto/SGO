
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
    horas = [os.hora_atividade_1]

    if os.atividade_2:
        horas.append(os.hora_atividade_2)

    if os.atividade_3:
        horas.append(os.hora_atividade_3)

    if os.atividade_4:
        horas.append(os.hora_atividade_4)

    if os.atividade_5:
        horas.append(os.hora_atividade_5)

    return n_atividades, atividades, horas
