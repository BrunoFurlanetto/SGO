from datetime import datetime
from itertools import chain

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.shortcuts import render, redirect

from cadastro.models import RelatorioDeAtendimentoPublicoCeu, RelatorioDeAtendimentoColegioCeu, \
    RelatorioDeAtendimentoEmpresaCeu
from escala.models import Escala
from .funcoes import is_ajax, juntar_dados, contar_atividades, teste_aviso

from ceu.models import Professores


@login_required(login_url='login')
def dashboard(request):
    # --------------------------- Parte para verificação de autenticação ---------------------------------
    ver_icons = User.objects.filter(pk=request.user.id, groups__name='Colégio').exists()

    if ver_icons:
        return redirect('fichaAvaliacao')
    # ----------------------------------------------------------------------------------------------------
    dados_publico = RelatorioDeAtendimentoPublicoCeu.objects.order_by('atividades__atividade_1__data_e_hora').filter(
        data_atendimento=datetime.now().date())
    dados_colegio = RelatorioDeAtendimentoColegioCeu.objects.order_by('atividades__atividade_1__data_e_hora').filter(
        check_in__date__lt=datetime.now().date(), check_out__date__gt=datetime.now().date())
    # dados_empresa =
    dados_iniciais = list(chain(dados_publico, dados_colegio))
    data_hoje = datetime.now().date()

    usuario_logado = Professores.objects.get(usuario=request.user)

    # ------------------ Ordens para conta de atividades e horas do mês --------------------
    ordens_usuario = RelatorioDeAtendimentoPublicoCeu.objects.filter(
        equipe__icontains=usuario_logado).filter(
        data_atendimento__month=datetime.now().month).values()

    # ------------- Verificação de entrega da disponibilidade do mês sseguinte -------------
    mostrar_aviso_disponibilidade = teste_aviso(request.user.last_login, usuario_logado, request.user.id)
    depois_25 = False
    if datetime.now().day > 25:
        depois_25 = True

    # ----------- Seleção da escala do dia -------------
    escalas = Escala.objects.filter(data=datetime.now())

    equipe_escalada = None
    if len(escalas) > 0:
        for escala in escalas:
            equipe_escalada = escala.equipe.split(', ')

    if is_ajax(request) and request.method == 'POST':
        data_selecao = request.POST.get('data_selecionada')

        publico = RelatorioDeAtendimentoPublicoCeu.objects.order_by('atividades__atividade_1__data_e_hora').filter(
            data_atendimento=data_selecao)
        colegio = RelatorioDeAtendimentoColegioCeu.objects.order_by('atividades__atividade_1__data_e_hora').filter(
            check_in__date__lte=data_selecao, check_out__date__gte=data_selecao)
        empresa = RelatorioDeAtendimentoEmpresaCeu.objects.order_by('atividades__atividade_1__data_e_hora').filter(
            check_in__date__lte=data_selecao, check_out__date__gte=data_selecao)

        relatorios = list(chain(publico, colegio, empresa))
        print(relatorios)

        dados = juntar_dados(relatorios)

        return JsonResponse({'dados': dados})

    if request.method != 'POST':
        professores = Professores.objects.all()

        ordens_usuario = RelatorioDeAtendimentoPublicoCeu.objects.filter(
            equipe__icontains=usuario_logado.usuario.first_name).filter(
            data_atendimento__month=datetime.now().month)

        # ------------------ Parte para chegar no resumo do mês -------------------
        n_atividade = contar_atividades(usuario_logado, ordens_usuario.values())
        # n_horas = contar_horas(usuario_logado, ordens_usuario.values())
        # -------------------------------------------------------------------------

        return render(request, 'dashboard/dashboard.html', {'professores': professores, 'relatorios': dados_iniciais,
                                                            'data': data_hoje})
        # , {'ordemDeServico': dados_iniciais, 'data': data,
        #  'equipe_escalada': equipe_escalada, 'n_atividades': n_atividade,
        #  'n_horas': n_horas, 'mostrar': mostrar_aviso_disponibilidade,
        #  'depois_25': depois_25})
