from datetime import datetime
from itertools import chain

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from ceu.models import Professores
from escala.funcoes import escalar, contar_dias, verificar_mes_e_ano, verificar_dias, is_ajax, \
    alterar_dia_limite_peraltas, pegar_clientes_data_selecionada, monitores_disponiveis
from escala.models import Escala, Disponibilidade, DiaLimite
from ordemDeServico.models import OrdemDeServico
from peraltas.models import DiaLimiteAcampamento, DiaLimiteHotelaria, ClienteColegio, FichaDeEvento
from peraltas.models import Monitor, DisponibilidadeAcampamento, DisponibilidadeHotelaria


@login_required(login_url='login')
def escala(request):
    professores = Professores.objects.all()
    escalas = Escala.objects.all()
    ver_icons = User.objects.filter(pk=request.user.id, groups__name='Colégio').exists()
    edita = User.objects.filter(pk=request.user.id, groups__name='Coordenador pedagógico').exists()

    if request.method != 'POST':
        return render(request, 'escala/escala.html', {'professores': professores,
                                                      'escalas': escalas,
                                                      'ver': ver_icons, 'edita': edita})

    # ------------------- Pegar somente professor disponivel no dia selecionado --------------------------
    if is_ajax(request) and request.method == 'POST':
        mes = datetime.strptime(request.POST.get('data_selecionada'), '%d/%m/%Y').month
        mes_selecao = Disponibilidade.objects.filter(mes=mes)
        disponibilidade = Disponibilidade()
        professores_disponiveis = disponibilidade.verificar_dias(mes_selecao, request.POST.get('data_selecionada'))

        return HttpResponse(professores_disponiveis)
    # ----------------------------------------------------------------------------------------------------

    # # ------------------- Pegando respostas do fomulário e montado a equipe ----------------------
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


@login_required(login_url='login')
def disponibilidade(request):
    dia_limite = DiaLimite.objects.get(id=1)

    if request.method != 'POST':
        antes_dia = True if datetime.now().day < dia_limite.dia_limite else False
        coordenador = User.objects.filter(pk=request.user.id, groups__name='Coordenador pedagógico').exists()
        professores = Professores.objects.all()

        return render(request, 'escala/disponibilidade.html', {'antes_dia': antes_dia, 'dia_limite': dia_limite,
                                                               'professores': professores, 'coordenador': coordenador})

    if is_ajax(request):
        try:
            dia_limite.dia_limite = request.POST.get('novo_dia')
            dia_limite.save()
        except:
            return JsonResponse({'tipo': 'error',
                                 'mensagem': 'Houve um erro inesperado, tente novamente mais tarde!'})
        else:
            return JsonResponse({'tipo': 'sucesso',
                                 'mensagem': 'Dia limite alterado com sucesso!'})

    professor = Professores.objects.get(usuario__first_name=request.user.first_name)

    if request.POST.get('professor') is not None and request.POST.get('professor') != '':
        professor = Professores.objects.get(id=int(request.POST.get('professor')))

    dias = verificar_dias(request.POST.get('datas_disponiveis'), Professores.objects.get(usuario=professor.usuario))

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


def disponibilidadePeraltas(request):
    dia_limite_acampamento = DiaLimiteAcampamento.objects.get(id=1)
    dia_limite_hotelaria = DiaLimiteHotelaria.objects.get(id=1)

    if request.method != "POST":
        antes_dia_limite_acampamento = True if datetime.now().day < dia_limite_acampamento.dia_limite_acampamento else False
        antes_dia_limite_hotelaria = True if datetime.now().day < dia_limite_hotelaria.dia_limite_hotelaria else False

        coordenador_acampamento = User.objects.filter(pk=request.user.id, groups__name='Coordenador monitoria').exists()
        coordenador_hotelaria = User.objects.filter(pk=request.user.id, groups__name='Coordenador hotelaria').exists()
        monitores = Monitor.objects.all()

        return render(request, 'escala/disponibilidade-peraltas.html', {
            'coordenador_acampamento': coordenador_acampamento,
            'coordenador_hotelaria': coordenador_hotelaria,
            'dia_limite_acampamento': dia_limite_acampamento.dia_limite_acampamento,
            'dia_limite_hotelaria': dia_limite_hotelaria.dia_limite_hotelaria,
            'monitores': monitores,
            'antes_dia_limite_acampamento': antes_dia_limite_acampamento,
            'antes_dia_limite_hotelaria': antes_dia_limite_hotelaria,
        })

    if is_ajax(request):
        if request.POST.get('novo_dia'):
            return JsonResponse(alterar_dia_limite_peraltas(request.POST))

        monitor = Monitor.objects.get(usuario=request.user)
        print(request.POST.get('datas_disponiveis'))
        if request.POST.get('monitor') is not None and request.POST.get('monitor') != '':
            monitor = Monitor.objects.get(id=int(request.POST.get('monitor')))

        dias = verificar_dias(request.POST.get('datas_disponiveis'),
                              Monitor.objects.get(usuario=monitor.usuario),
                              peraltas=request.POST.get('peraltas'))

        if dias[0]:
            n_dias = contar_dias(dias[0])
            mes_e_ano_cadastro = verificar_mes_e_ano(dias[0])
        else:
            n_dias = 0
            mes_e_ano_cadastro = verificar_mes_e_ano(dias[1])

        if request.POST.get('peraltas') == 'acampamento':
            ja_cadastrado = DisponibilidadeAcampamento.objects.filter(monitor=monitor,
                                                                      mes=mes_e_ano_cadastro[0],
                                                                      ano=mes_e_ano_cadastro[1])
        else:
            ja_cadastrado = DisponibilidadeHotelaria.objects.filter(monitor=monitor,
                                                                    mes=mes_e_ano_cadastro[0],
                                                                    ano=mes_e_ano_cadastro[1])

        try:
            if ja_cadastrado:

                if dias[0]:
                    for cadastro in ja_cadastrado:
                        ja_cadastrado.update(dias_disponiveis=cadastro.dias_disponiveis + ', ' + dias[0],
                                             n_dias=cadastro.n_dias + n_dias)

                        if dias[1]:
                            msg = f'dias {dias[1]} já estão na base de dados. Disponibilidade atualizada com sucesso'
                            return JsonResponse({'tipo': 'sucesso',
                                                 'mensagem': msg})
                else:
                    return JsonResponse({'tipo': 'aviso',
                                         'mensagem': 'Todos os dias selecionados já estão salvos na base de dados!'})

            else:

                if request.POST.get('peraltas') == 'acampamento':
                    dias_disponiveis = DisponibilidadeAcampamento(monitor=monitor,
                                                                  mes=mes_e_ano_cadastro[0],
                                                                  ano=mes_e_ano_cadastro[1],
                                                                  n_dias=n_dias,
                                                                  dias_disponiveis=dias[0])
                else:
                    dias_disponiveis = DisponibilidadeHotelaria(monitor=monitor,
                                                                mes=mes_e_ano_cadastro[0],
                                                                ano=mes_e_ano_cadastro[1],
                                                                n_dias=n_dias,
                                                                dias_disponiveis=dias[0])

                dias_disponiveis.save()
                return JsonResponse({'tipo': 'sucesso',
                                     'mensagem': 'Disponibilidade salva com sucesso'})
        except:
            return JsonResponse({'tipo': 'erro',
                                 'mensagem': 'Houve um erro inesperado, tente novamente mais tarde!'})


def verEscalaPeraltas(request):
    edita = User.objects.filter(pk=request.user.id, groups__name='Coordenador monitoria').exists()

    return render(request, 'escala/escala_peraltas.html', {'edita': edita})


def escalarMonitores(request, setor, data):
    data_selecionada = datetime.strptime(data, '%d-%m-%Y').date()
    clientes_dia = pegar_clientes_data_selecionada(data_selecionada)
    monitores_hotelaria, monitores_acampamento = monitores_disponiveis(data_selecionada)
    print(monitores_acampamento)

    return render(request, 'escala/escalar_monitores.html', {'clientes_dia': clientes_dia,
                                                             'data': data_selecionada,
                                                             'setor': setor,
                                                             'monitores_hotelaria': monitores_hotelaria,
                                                             'monitores_acampamento': monitores_acampamento})
