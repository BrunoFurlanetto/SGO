from cadastro.models import Professores, Tipo
import datetime


def is_ajax(request):
    return request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest'


def contar_atividades(professor_logado, ordens):
    n_atividades = 0

    for ordem in ordens:
        for nome in ordem:
            if 'prf' in nome and ordem[nome] is not None:

                if Professores.objects.get(pk=ordem[nome]) == professor_logado:
                    n_atividades += 1

    return n_atividades


def contar_horas(professor_logado, ordens):
    n_horas = datetime.timedelta()

    for ordem in ordens:
        for nome in ordem:
            if 'atv_1' in nome and ordem[nome] is not None:

                if Professores.objects.get(pk=ordem[nome]) == professor_logado:
                    n_horas += ordem['soma_horas_1']

            if 'atv_2' in nome and ordem[nome] is not None:

                if Professores.objects.get(pk=ordem[nome]) == professor_logado:
                    if ordem['soma_horas_2'] is not None:
                        n_horas += ordem['soma_horas_2']

            if 'atv_3' in nome and ordem[nome] is not None:

                if ordem['soma_horas_3'] is not None:
                    if Professores.objects.get(pk=ordem[nome]) == professor_logado:
                        n_horas += ordem['soma_horas_3']

    return formatar_horas(n_horas)


def formatar_horas(horas):

    if horas != datetime.timedelta(days=0):
        h = horas.days * 24 + horas.seconds // 3600
        m = (horas.seconds % 3600) / 60
        return f'{h}h{m:.0f}min'
    else:
        h = horas.seconds // 3600
        m = (horas.seconds % 3600) / 60
        return f'{h}h{m:.0f}min'
