from datetime import timedelta, datetime

from django.db.models import Q

from cadastro.models import OrdemDeServico, Tipo, Professores


def is_ajax(request):
    return request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest'


def verificar_anos(os):
    anos = []

    for ordem in os:
        if not ordem.data_atendimento.year in anos:
            anos.append(ordem.data_atendimento.year)

    return anos


def pegar_mes(ordens):
    temp = []
    meses = {1: 'Janeiro', 2: 'Fevereiro', 3: 'Março', 4: 'Abril', 5: 'Maio', 6: 'Junho', 7: 'Julho',
             8: 'Agosto', 9: 'Setembro', 10: 'Outubro', 11: 'Novembro', 12: 'Dezembro'}

    for ordem in ordens:
        if not meses[ordem.data_atendimento.month] in temp:
            temp.append(meses[ordem.data_atendimento.month])

    return ', '.join(temp)


def contar_atividades(professor):
    n_atividades = 0
    ordens = OrdemDeServico.objects.filter(Q(coordenador=professor) | Q(professor_2=professor) |
                                           Q(professor_3=professor) | Q(professor_4=professor)).filter(
        Q(tipo=Tipo.objects.get(tipo='Público')) |
        Q(tipo=Tipo.objects.get(tipo='Colégio'))).filter(
        data_atendimento__month=datetime.now().month).values()

    for ordem in ordens:
        for nome in ordem:
            if 'prf' in nome and ordem[nome] is not None:

                if Professores.objects.get(pk=ordem[nome]) == professor:
                    n_atividades += 1

    return n_atividades


def contar_horas(professor):
    n_horas = timedelta()
    ordens = OrdemDeServico.objects.filter(
        Q(coordenador=professor) | Q(professor_2=professor)).filter(
        Q(tipo=Tipo.objects.get(tipo='Empresa'))).filter(data_atendimento__month=datetime.now().month).values()

    for ordem in ordens:
        for nome in ordem:
            if 'atv_1' in nome and ordem[nome] is not None:

                if Professores.objects.get(pk=ordem[nome]) == professor:
                    n_horas += ordem['soma_horas_1']

            if 'atv_2' in nome and ordem[nome] is not None:

                if Professores.objects.get(pk=ordem[nome]) == professor:
                    if ordem['soma_horas_2'] is not None:
                        n_horas += ordem['soma_horas_2']

            if 'atv_3' in nome and ordem[nome] is not None:

                if ordem['soma_horas_3'] is not None:
                    if Professores.objects.get(pk=ordem[nome]) == professor:
                        n_horas += ordem['soma_horas_3']

    return formatar_horas(n_horas)


def contar_diaria(professor):
    ordens = OrdemDeServico.objects.filter(Q(coordenador=professor) | Q(professor_2=professor) |
                                           Q(professor_3=professor) | Q(professor_4=professor)).filter(
        Q(tipo=Tipo.objects.get(tipo='Público')) |
        Q(tipo=Tipo.objects.get(tipo='Colégio'))).filter(data_atendimento__month=datetime.now().month).values()

    if professor.diarista:
        return len(ordens)
    else:
        return 0


def formatar_horas(horas):
    if horas != timedelta(days=0):
        h = horas.days * 24 + horas.seconds // 3600
        m = (horas.seconds % 3600) / 3600
        total = h + m
        return str(round(total, 2))
    else:
        h = horas.seconds // 3600
        m = (horas.seconds % 3600) / 3600
        total = h + m
        return str(round(total, 2))
