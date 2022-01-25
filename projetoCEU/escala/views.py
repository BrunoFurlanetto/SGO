from datetime import datetime
from django.contrib import messages
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from cadastro.models import Professores
from escala.funcoes import escalar, is_ajax, contar_dias, verificar_mes
from escala.models import Escala, Disponibilidade


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
    if not request.user.is_authenticated:
        return redirect('login')

    if request.method != 'POST':
        return render(request, 'escala/disponibilidade.html')

    if is_ajax(request) and request.method == 'POST':
        n_dias = contar_dias(request.POST.get('datas_disponiveis'))
        mes_cadastro = verificar_mes(request.POST.get('datas_disponiveis'))

        consulta = Disponibilidade.objects.filter(professor=Professores.objects.get(nome=request.user.first_name),
                                                  mes_referencia=mes_cadastro)

        if len(consulta) != 0:
            messages.error(request, 'Mês já cadastrado na base de dados')
            return render(request, 'escala/disponibilidade.html')

        try:
            dias_disponiveis = Disponibilidade(professor=Professores.objects.get(nome=request.user.first_name),
                                               mes_referencia=mes_cadastro, n_dias=n_dias,
                                               dias_disponiveis=request.POST.get('datas_disponiveis'))
            dias_disponiveis.save()
        except:
            messages.error(request, 'Houve um erro inesperado, tente novamente mais tarde!')
            return redirect('dashboard')
        else:
            messages.success(request, 'Disponibilidade salva com sucesso')
            return redirect('dashboard')

    return redirect('disponibilidade')
