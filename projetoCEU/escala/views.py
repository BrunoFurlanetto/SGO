from datetime import datetime
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from cadastro.models import OrdemDeServico, Professores
from escala.models import Escala


def escala(request):
    if not request.user.is_authenticated:
        return redirect('login')

    professores = Professores.objects.all()
    escala = Escala.objects.all()
    ver_icons = User.objects.filter(pk=request.user.id, groups__name='Colégio').exists()

    if request.method != 'POST':
        return render(request, 'escala/escala.html', {'professores': professores,
                                                      'escala': escala, 'ver': ver_icons})
    else:
        data_post = request.POST.get('data_escala')
        data = datetime.strptime(data_post, '%Y-%m-%d').date()
        coordenador = Professores.objects.get(nome=request.POST.get('coordenador'))
        professor_2 = None if request.POST.get('professor_2') == '' else Professores.objects.get(
            nome=request.POST.get('professor_2'))
        professor_3 = None if request.POST.get('professor_3') == '' else Professores.objects.get(
            nome=request.POST.get('professor_3'))
        professor_4 = None if request.POST.get('professor_4') == '' else Professores.objects.get(
            nome=request.POST.get('professor_4'))
        professor_5 = None if request.POST.get('professor_5') == '' else Professores.objects.get(
            nome=request.POST.get('professor_5'))

        novaEscala = Escala(
            data=data, coordenador=coordenador, professor_2=professor_2, professor_3=professor_3,
            professor_4=professor_4, professor_5=professor_5)

        novaEscala.save()

        return redirect('escala')
