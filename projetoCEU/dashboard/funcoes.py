from django.contrib.auth.models import User
from cadastro.models import Professores
from datetime import datetime, timedelta
from escala.models import Disponibilidade


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
    n_horas = timedelta()

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

    if horas != timedelta(days=0):
        h = horas.days * 24 + horas.seconds // 3600
        m = (horas.seconds % 3600) / 60
        return f'{h}h{m:.0f}min'
    else:
        h = horas.seconds // 3600
        m = (horas.seconds % 3600) / 60
        return f'{h}h{m:.0f}min'


def teste_aviso(hora_login, usuario, id_usuario):
    diferenca = timedelta(hours=hora_login.hour, minutes=hora_login.minute, seconds=hora_login.second)
    diferenca -= timedelta(hours=datetime.now().hour, minutes=datetime.now().minute, seconds=datetime.now().second)

    if datetime.now().month != 12:
        consulta = Disponibilidade.objects.filter(professor=usuario, mes=datetime.now().month + 1)
    else:
        consulta = Disponibilidade.objects.filter(professor=usuario, mes=1, ano=datetime.now().year + 1)

    if len(consulta) == 0:
        if datetime.now().day > 20:
            if User.objects.filter(pk=id_usuario, groups__name='Professor').exists():
                if diferenca == timedelta(days=0, hours=3):
                    return True

    return False
