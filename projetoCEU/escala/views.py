from datetime import datetime

from django.contrib import messages
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from cadastro.models import Professores
from escala.funcoes import escalar
from escala.models import Escala


def escala(request):
    if not request.user.is_authenticated:
        return redirect('login')

    professores = Professores.objects.all()
    escalas = Escala.objects.all()
    ver_icons = User.objects.filter(pk=request.user.id, groups__name='Colégio').exists()
    edita = User.objects.filter(pk=request.user.id, groups__name='Coordenador pedagógico').exists()

    for escala in escalas:
        data = escala.data
        equipe = escala.equipe.split(', ')

    if request.method != 'POST':
        return render(request, 'escala/escala.html', {'professores': professores,
                                                      'equipe': equipe, 'data': data, 'escalas': escalas,
                                                      'ver': ver_icons, 'edita': edita})

    # ------------------- Pegando respostas do fomulário e montado a equipe ----------------------
    data_post = request.POST.get('data_escala')
    data = datetime.strptime(data_post, '%d/%m/%Y').date()
    coordenador = request.POST.get('coordenador')
    professor_2 = request.POST.get('professor_2')
    professor_3 = request.POST.get('professor_3')
    professor_4 = request.POST.get('professor_4')
    professor_5 = request.POST.get('professor_5')

    equipe = escalar(coordenador, professor_2, professor_3, professor_4, professor_5)

    # ------------------- Salvando a escala ----------------------
    try:
        nova_escala = Escala(data=data, equipe=equipe)
        nova_escala.save()
    except:
        messages.error(request, 'Ocorreu um erro inesperado, tente novamente mais tarde!')
    else:
        messages.success(request, f'Escala para o dia {data} com {equipe}, salva com sucesso!')
    finally:
        return redirect('escala')


def disponibilidade(request):
    return render(request, 'escala/disponibilidade.html')
