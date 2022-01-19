
def escalar(coodenador, prof_2, prof_3, prof_4, prof_5):
    equipe = [coodenador]

    if prof_2:
        equipe.append(prof_2)

    if prof_3:
        equipe.append(prof_3)

    if prof_4:
        equipe.append(prof_4)

    if prof_5:
        equipe.append(prof_5)

    return ', '.join(equipe)
