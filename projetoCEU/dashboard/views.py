import json
from datetime import datetime
from itertools import chain

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import render, redirect

from cadastro.models import RelatorioDeAtendimentoPublicoCeu, RelatorioDeAtendimentoColegioCeu, \
    RelatorioDeAtendimentoEmpresaCeu
from escala.models import Escala
from .funcoes import is_ajax, juntar_dados, contar_atividades, teste_aviso, contar_horas

from ceu.models import Professores


def dashboard(request):

    if request.user in User.objects.filter(groups__name='CEU'):
        return redirect('dashboardCeu')

    if request.user in User.objects.filter(groups__name='Peraltas'):
        return redirect('dashboardPeraltas')

    if User.objects.filter(pk=request.user.id, groups__name='Colégio').exists():
        return redirect('fichaAvaliacao')


@login_required(login_url='login')
def dashboardCeu(request):

    if request.user not in User.objects.filter(groups__name='CEU'):
        return redirect('dashboardPeraltas')

    # ---------------------- Dados inicias apresentados na tabela ----------------------------------------
    # Relatórios de atendimento ao público
    dados_publico = RelatorioDeAtendimentoPublicoCeu.objects.order_by('atividades__atividade_1__data_e_hora').filter(
        data_atendimento=datetime.now().date())
    # Relatórios de atendimento com colégio
    dados_colegio = RelatorioDeAtendimentoColegioCeu.objects.order_by('atividades__atividade_1__data_e_hora').filter(
        check_in__date__lte=datetime.now().date(), check_out__date__gte=datetime.now().date())
    # Relatórios de atendimento com empresa
    dados_empresa = RelatorioDeAtendimentoEmpresaCeu.objects.order_by('locacoes__locacao_1__data_e_hora').filter(
        check_in__date__lte=datetime.now().date(), check_out__date__gte=datetime.now().date())

    dados_iniciais = list(chain(dados_publico, dados_colegio, dados_empresa))
    data_hoje = datetime.now().date()

    # ------------------ Relatórios para conta de atividades e horas do mês --------------------
    usuario_logado = Professores.objects.get(usuario=request.user)
    # Relatórios de atendimento ao público
    usuario_publico = RelatorioDeAtendimentoPublicoCeu.objects.filter(
        data_atendimento__month=datetime.now().month).filter(
        equipe__icontains=json.dumps(usuario_logado.usuario.first_name))
    # Relatórios de atendimento de colégio
    usuario_colegio = RelatorioDeAtendimentoColegioCeu.objects.filter(
        Q(check_in__month=datetime.now().month) | Q(check_out__month=datetime.now().month)).filter(
        equipe__icontains=json.dumps(usuario_logado.usuario.first_name))
    # Relatórios de atendimento de empresa
    usuario_empresa = RelatorioDeAtendimentoEmpresaCeu.objects.filter(
        Q(check_in__month=datetime.now().month) | Q(check_out__month=datetime.now().month)).filter(
        equipe__icontains=json.dumps(usuario_logado.usuario.first_name))

    relatorios_usuario = list(chain(usuario_publico, usuario_colegio, usuario_empresa))

    # ------------------ Parte para chegar no resumo do mês -------------------
    # n_atividades = contar_atividades(usuario_logado, relatorios_usuario)
    # n_horas = contar_horas(usuario_logado, relatorios_usuario)

    # ----------- Seleção da escala do dia -------------
    escalas = Escala.objects.filter(data=datetime.now())
    equipe_escalada = None

    if len(escalas) > 0:
        for escala in escalas:
            equipe_escalada = escala.equipe.split(', ')

    # ------------ Ajax enviado para construir as linhas da tabela para a data selecionada ----------------
    if is_ajax(request) and request.method == 'POST':
        data_selecao = request.POST.get('data_selecionada')

        # Relatórios de atendimento ao público
        publico = RelatorioDeAtendimentoPublicoCeu.objects.order_by('atividades__atividade_1__data_e_hora').filter(
            data_atendimento=data_selecao)
        # Relatórios de atendimento de colégio
        colegio = RelatorioDeAtendimentoColegioCeu.objects.order_by('atividades__atividade_1__data_e_hora').filter(
            check_in__date__lte=data_selecao, check_out__date__gte=data_selecao)
        # Relatórios de atendimento de empresa
        empresa = RelatorioDeAtendimentoEmpresaCeu.objects.order_by('atividades__atividade_1__data_e_hora').filter(
            check_in__date__lte=data_selecao, check_out__date__gte=data_selecao)

        relatorios = list(chain(publico, colegio, empresa))
        dados = juntar_dados(relatorios)

        return JsonResponse({'dados': dados,})

    # ------------- Verificação de entrega da disponibilidade do mês sseguinte -------------

    mostrar_aviso_disponibilidade = teste_aviso(request.user.last_login, usuario_logado, request.user.id)
    depois_25 = False
    if datetime.now().day > 25:
        depois_25 = True

    if request.method != 'POST':
        professores = Professores.objects.all()

        return render(request, 'dashboard/dashboardCeu.html', {'professores': professores, 'relatorios': dados_iniciais,
                                                               'data': data_hoje, 'equipe_escalada': equipe_escalada,
                                                               # 'n_atividades': n_atividades, 'n_horas': n_horas,
                                                               'mostrar_aviso': mostrar_aviso_disponibilidade,
                                                               'depois_25': depois_25})


@login_required(login_url='login')
def dashboardPeraltas(request):

    if request.user not in User.objects.filter(groups__name='Peraltas'):
        return redirect('dashboardCeu')

    return render(request, 'dashboard/dashboardPeraltas.html')
