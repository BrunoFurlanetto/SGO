from django.contrib.auth.models import User
from django.shortcuts import render

from ordemDeServico.models import OrdemDeServico
from peraltas.models import FichaDeEvento


def eventos(request):
    ordens = OrdemDeServico.objects.all()
    fichas_de_evento = FichaDeEvento.objects.all()
    ver_ficha = User.objects.filter(pk=request.user.id, groups__name='Coordenador monitoria').exists() or User.objects.filter(pk=request.user.id, groups__name='Administrativo Peraltas').exists()
    professor_ceu = False

    if request.user in User.objects.filter(groups__name='CEU') and request.user in User.objects.filter(groups__name='Professor'):
        professor_ceu = True

    print(professor_ceu)

    return render(request, 'calendarioEventos/calendario_eventos.html', {'eventos': ordens,
                                                                         'fichas': fichas_de_evento,
                                                                         'professor_ceu': professor_ceu,
                                                                         'ver_ficha': ver_ficha})
