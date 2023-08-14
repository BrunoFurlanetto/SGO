import json
from datetime import datetime
from itertools import chain

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User, Group
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import render, redirect

from cadastro.models import RelatorioDeAtendimentoPublicoCeu, RelatorioDeAtendimentoColegioCeu, \
    RelatorioDeAtendimentoEmpresaCeu
from escala.models import Escala, DiaLimite
from orcamento.models import Orcamento
from peraltas.models import DiaLimitePeraltas, DiaLimitePeraltas, Monitor, FichaDeEvento, InformacoesAdcionais
from projetoCEU.utils import email_error
from .funcoes import is_ajax, juntar_dados, contar_atividades, teste_aviso, contar_horas, teste_aviso_monitoria

from ceu.models import Professores
from .utils_peraltas import campos_necessarios_aprovacao


@login_required(login_url='login')
def dashboard(request):
    if request.user.has_perm('cadastro.view_relatoriodeatendimentopublicoceu'):
        return redirect('dashboardCeu')
    elif not request.user.has_perm('fichaAvaliacao.add_fichadeavaliacao'):
        return redirect('dashboardPeraltas')
    else:
        return redirect('fichaAvaliacao')


@login_required(login_url='login')
def dashboardCeu(request):
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
    try:  # Try necessário devido ao usuário da Gla ser do CEU e não ser professor
        usuario_logado = Professores.objects.get(usuario=request.user)
        professor_logado = True
    except Professores.DoesNotExist:
        professor_logado = False
        mostrar_aviso_disponibilidade = False
        depois_25 = False
    except Exception as e:
        email_error(request.user.get_full_name(), e, __name__)
        messages.error(request, 'Houve um erro inesperado, tente novamente mais tarde')
        return redirect('logout')
    else:
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

        # ------------- Verificação de entrega da disponibilidade do mês sseguinte -------------
        mostrar_aviso_disponibilidade = teste_aviso(request.user.last_login, usuario_logado, request.user.id)
        dia_limite, p = DiaLimite.objects.get_or_create(id=1, defaults={'dia_limite': 25})
        depois_25 = False

        if datetime.now().day > dia_limite.dia_limite:
            depois_25 = True

    # ----------- Seleção da escala do dia -------------
    # escalas = Escala.objects.filter(data=datetime.now())
    # equipe_escalada = None
    #
    # if len(escalas) > 0:
    #     for escala in escalas:
    #         equipe_escalada = escala.equipe.split(', ')

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

        return JsonResponse({'dados': dados, })

    if request.method != 'POST':
        professores = Professores.objects.all()

        return render(request, 'dashboard/dashboardCeu.html', {
            'professores': professores, 'relatorios': dados_iniciais,
            'data': data_hoje,  # 'equipe_escalada': equipe_escalada,
            'professor': professor_logado,
            # 'n_atividades': n_atividades, 'n_horas': n_horas,
            'mostrar_aviso': mostrar_aviso_disponibilidade,
            'depois_25': depois_25
        })


@login_required(login_url='login')
def dashboardPeraltas(request):
    dia_limite_peraltas, p = DiaLimitePeraltas.objects.get_or_create(id=1, defaults={'dia_limite_peraltas': 25})
    orcamentos_para_gerencia = Orcamento.objects.filter(necessita_aprovacao_gerencia=True)
    orcamentos = Orcamento.objects.filter(colaborador=request.user, necessita_aprovacao_gerencia=False)
    msg_monitor = None
    grupos_usuario = request.user.groups.all()
    diretoria = Group.objects.get(name='Diretoria')

    if is_ajax(request):
        orcamento = Orcamento.objects.get(pk=request.POST.get('id_orcamento'))

        return JsonResponse(campos_necessarios_aprovacao(orcamento))

    try:
        monitor = Monitor.objects.get(usuario=request.user)
    except Monitor.DoesNotExist:
        monitor = None
    else:
        msg_monitor = teste_aviso_monitoria(
            request.user.last_login.astimezone(),
            monitor,
            dia_limite_peraltas
        )

    if request.POST.get('termo_de_aceite'):
        monitor.aceite_do_termo = True
        monitor.save()
    print(request.POST)
    return render(request, 'dashboard/dashboardPeraltas.html', {
        'msg_acampamento': msg_monitor,
        'termo_monitor': not monitor.aceite_do_termo if monitor else None,
        'diretoria': diretoria in grupos_usuario,
        'orcamentos_gerencia': orcamentos_para_gerencia,
        'orcamentos': orcamentos,
        # 'ultimas_versoes': FichaDeEvento.logs_de_alteracao(),
    })
