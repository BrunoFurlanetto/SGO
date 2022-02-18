from datetime import datetime
from django.contrib import messages
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.shortcuts import render, redirect
from cadastro.models import Professores
from escala.funcoes import escalar, contar_dias, verificar_mes_e_ano, verificar_dias, is_ajax
from escala.models import Escala, Disponibilidade


def escala(request):
    if not request.user.is_authenticated:
        return redirect('login')

    professores = Professores.objects.all()
    escalas = Escala.objects.all()
    ver_icons = User.objects.filter(pk=request.user.id, groups__name='Colégio').exists()
    edita = User.objects.filter(pk=request.user.id, groups__name='Coordenador pedagógico').exists()

    # ------------------- Pegar somente professor disponivel no dia selecionado --------------------------
    if is_ajax(request) and request.method == 'POST':
        mes = datetime.strptime(request.POST.get('data_selecionada'), '%d/%m/%Y').month
        mes_selecao = Disponibilidade.objects.filter(mes=mes)
        disponibilidade = Disponibilidade()
        professores_disponiveis = disponibilidade.verificar_dias(mes_selecao, request.POST.get('data_selecionada'))

        return HttpResponse(professores_disponiveis)
    # ----------------------------------------------------------------------------------------------------

    for escala in escalas:
        data = escala.data
        equipe = escala.equipe.split(', ')

    if request.method != 'POST':
        return render(request, 'escala/escala.html', {'professores': professores,
                                                      'equipe': equipe, 'data': data, 'escalas': escalas,
                                                      'ver': ver_icons, 'edita': edita})

    # # ------------------- Pegando respostas do fomulário e montado a equipe ----------------------
    if not is_ajax(request):
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
        antes_25 = True if datetime.now().day < 25 else False
        coordenador = User.objects.filter(pk=request.user.id, groups__name='Coordenador pedagógico').exists()
        professores = Professores.objects.all()
        return render(request, 'escala/disponibilidade.html', {'antes_25': antes_25, 'professores': professores,
                                                               'coordenador': coordenador})

    professor = Professores.objects.get(nome=request.user.first_name)

    if request.POST.get('professor') is not None:
        professor = Professores.objects.get(nome=request.POST.get('professor'))

    dias = verificar_dias(request.POST.get('datas_disponiveis'), Professores.objects.get(nome=professor))

    if dias[0]:
        n_dias = contar_dias(dias[0])
        mes_e_ano_cadastro = verificar_mes_e_ano(dias[0])
    else:
        n_dias = 0
        mes_e_ano_cadastro = verificar_mes_e_ano(dias[1])

    ja_cadastrado = Disponibilidade.objects.filter(professor=professor, mes=mes_e_ano_cadastro[0],
                                                   ano=mes_e_ano_cadastro[1])

    try:
        if ja_cadastrado:

            if dias[0]:
                for cadastro in ja_cadastrado:
                    ja_cadastrado.update(dias_disponiveis=cadastro.dias_disponiveis + ', ' + dias[0],
                                         n_dias=cadastro.n_dias + n_dias)

                    if dias[1]:
                        messages.warning(request, f'dias {dias[1]} não cadastrados por já estar na base de dados"')
                    messages.success(request, 'Disponibilidade atualizada com sucesso')
                    return redirect('dashboard')
            else:
                messages.warning(request, 'Todos os dias selecionados já estão salvos na base de dados!')
                return redirect('dashboard')

        else:
            dias_disponiveis = Disponibilidade(professor=professor, mes=mes_e_ano_cadastro[0],
                                               ano=mes_e_ano_cadastro[1], n_dias=n_dias, dias_disponiveis=dias[0])
            dias_disponiveis.save()
            messages.success(request, 'Disponibilidade salva com sucesso')
            return redirect('dashboard')
    except:
        messages.error(request, 'Houve um erro inesperado, tente novamente mais tarde!')
        return redirect('dashboard')
