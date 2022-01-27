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


def verificar_dias(dias_enviados, professor):
    dia_referencia = dias_enviados.split(', ')[0]
    lista_dias = dias_enviados.split(', ')
    mes = datetime.datetime.strptime(dia_referencia, '%d/%m/%Y').month
    ano = datetime.datetime.strptime(dia_referencia, '%d/%m/%Y').year
    dias_ja_cadastrados = []
    dias_a_cadastrar = []

    # nome_meses = {1: 'Janeiro', 2: 'Fevereiro', 3: 'Março', 4: 'Abril', 5: 'Maio', 6: 'Junho',
    #               7: 'Julho', 8: 'Agosto', 9: 'Setembro', 10: 'Outubro', 11: 'Novembro', 12: 'Dezembro'}

    dias_cadastrados = Disponibilidade.objects.filter(professor=professor, mes=mes, ano=ano)
    print(mes)

    if dias_cadastrados:
        for cadastrado in dias_cadastrados:
            lista_dias_cadastrados = cadastrado.dias_disponiveis.split(', ')
            for dias in lista_dias:

                if dias in lista_dias_cadastrados:
                    dias_ja_cadastrados.append(dias)
                else:
                    dias_a_cadastrar.append(dias)
    else:
        dias_a_cadastrar.append(dias_enviados)

    return ', '.join(dias_a_cadastrar), ', '.join(dias_ja_cadastrados)


def contar_dias(dias):
    lista_dias = dias.split(', ')
    return len(lista_dias)


def verificar_mes_e_ano(dias):
    dia_referencia = dias.split(', ')[0]
    mes = datetime.datetime.strptime(dia_referencia, '%d/%m/%Y').month
    ano = datetime.datetime.strptime(dia_referencia, '%d/%m/%Y').year

    # nome_meses = {1: 'Janeiro', 2: 'Fevereiro', 3: 'Março', 4: 'Abril', 5: 'Maio', 6: 'Junho',
    #               7: 'Julho', 8: 'Agosto', 9: 'Setembro', 10: 'Outubro', 11: 'Novembro', 12: 'Dezembro'}

    return mes, ano
