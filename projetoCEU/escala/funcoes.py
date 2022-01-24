import datetime

from escala.models import Disponibilidade


def is_ajax(request):
    return request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest'


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


def contar_dias(dias):
    lista_dias = dias.split(', ')
    return len(lista_dias)


def verificar_mes(dias):
    dia_referencia = dias.split(', ')[0]
    mes = datetime.datetime.strptime(dia_referencia, '%d/%m/%Y').month

    nome_meses = {1: 'Janeiro', 2: 'Fevereiro', 3: 'Março', 4: 'Abril', 5: 'Maio', 6: 'Junho',
                  7: 'Julho', 8: 'Agosto', 9: 'Setembro', 10: 'Outubro', 11: 'Novembro', 12: 'Dezembro'}

    return nome_meses[mes]

