import json
import locale
from datetime import datetime, timedelta
from itertools import chain

import reversion
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import render, redirect
from reversion.models import Version

from cadastro.models import RelatorioDeAtendimentoPublicoCeu, RelatorioDeAtendimentoColegioCeu, \
    RelatorioDeAtendimentoEmpresaCeu
from escala.models import Escala, DiaLimite
from ordemDeServico.models import OrdemDeServico
from peraltas.models import DiaLimitePeraltas, DiaLimitePeraltas, Monitor, FichaDeEvento, InformacoesAdcionais, Vendedor
from projetoCEU.integracao_rd import alterar_campos_personalizados, formatar_envio_valores
from projetoCEU.utils import email_error
from .funcoes import is_ajax, juntar_dados, contar_atividades, teste_aviso, contar_horas, teste_aviso_monitoria

from ceu.models import Professores


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
    # ------------------ Relatórios para conta de atividades e horas do mês --------------------
    try:  # Try necessário devido ao usuário da Gla ser do CEU e não ser professor
        usuario_logado = Professores.objects.get(usuario=request.user)
        professor_logado = True
    except Professores.DoesNotExist:
        professor_logado = False
        mostrar_aviso_disponibilidade = False
        depois_25 = False
    except Exception as e:
        messages.error(request, f'Houve um erro inesperado ({e}), tente novamente mais tarde')
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

    if request.method != 'POST':
        # --------------------------------- Dados apresentados na tabela -----------------------------------------------
        data_relatorio = datetime.today().date()

        if request.GET.get('data_relatorios'):
            data_relatorio = datetime.strptime(request.GET.get('data_relatorios'), '%Y-%m-%d')

        dados_publico = RelatorioDeAtendimentoPublicoCeu.objects.order_by(
            'atividades__atividade_1__inicio').filter(data_atendimento=data_relatorio)
        # Relatórios de atendimento com colégio
        dados_colegio = RelatorioDeAtendimentoColegioCeu.objects.order_by(
            'atividades__atividade_1__data_e_hora').filter(
            check_in__date__lte=data_relatorio, check_out__date__gte=data_relatorio
        )
        # Relatórios de atendimento com empresa
        dados_empresa = RelatorioDeAtendimentoEmpresaCeu.objects.order_by('locacoes__locacao_1__data_e_hora').filter(
            check_in__date__lte=data_relatorio, check_out__date__gte=data_relatorio
        )
        dados_tabela = list(chain(dados_publico, dados_colegio, dados_empresa))
        data_hoje = datetime.now().date()
        professores = Professores.objects.all()

        return render(request, 'dashboard/dashboardCeu.html', {
            'professores': professores, 'relatorios': dados_tabela,
            'data': data_relatorio,  # 'equipe_escalada': equipe_escalada,
            'professor': professor_logado,
            # 'n_atividades': n_atividades, 'n_horas': n_horas,
            'mostrar_aviso': mostrar_aviso_disponibilidade,
            'depois_25': depois_25
        })


@login_required(login_url='login')
def dashboardPeraltas(request):
    dia_limite_peraltas, p = DiaLimitePeraltas.objects.get_or_create(id=1, defaults={'dia_limite_peraltas': 25})
    msg_monitor = sem_escalas = None
    diretoria = User.objects.filter(pk=request.user.id, groups__name__icontains='Diretoria').exists()
    operacional = User.objects.filter(pk=request.user.id, groups__name__icontains='operacional').exists()
    coordenador_monitoria = request.user.has_perm('peraltas.add_escalaacampamento')

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

    if diretoria or operacional or coordenador_monitoria or monitor:
        fichas_colaborador = FichaDeEvento.objects.filter(
            os=False,
            check_in__date__gte=datetime.today(),
        )
        sem_escalas = fichas_colaborador.filter(escala=False, pre_reserva=False)
    else:
        fichas_colaborador = FichaDeEvento.objects.filter(
            vendedora__usuario=request.user,
            os=False,
            check_in__date__gte=datetime.today(),
        )

    fichas = fichas_colaborador.filter(pre_reserva=False)
    pre_reservas = fichas_colaborador.filter(pre_reserva=True, agendado=False)
    confirmados = fichas_colaborador.filter(pre_reserva=True, agendado=True)
    fichas_adesao = fichas_colaborador.filter(os=False, pre_reserva=False)
    ordens_colaborador = OrdemDeServico.objects.filter(
        vendedor__usuario=request.user,
        check_in__date__gte=datetime.today(),
    )
    avisos = fichas_colaborador.filter(
        pre_reserva=True,
        check_in__date__gte=datetime.today().date(),
        check_in__date__lte=(datetime.today() + timedelta(days=50)).date()
    )

    if request.POST.get('termo_de_aceite'):
        monitor.aceite_do_termo = True
        monitor.save()

    return render(request, 'dashboard/dashboardPeraltas.html', {
        'msg_acampamento': msg_monitor,
        'termo_monitor': not monitor.aceite_do_termo if monitor else None,
        'diretoria': diretoria,
        'fichas_adesao': fichas_adesao,
        'fichas': fichas,
        'ordens_colaborador': ordens_colaborador,
        'pre_reservas': pre_reservas,
        'confirmados': confirmados,
        'sem_escalas': sem_escalas,
        'avisos': avisos,
        'operacional': operacional,
        'coordenador_monitoria': coordenador_monitoria,
        'comercial': User.objects.filter(pk=request.user.id, groups__name__icontains='comercial').exists(),
        'monitor': monitor,
        # 'ultimas_versoes': FichaDeEvento.logs_de_alteracao(),
    })  # TODO: Separar os returns para perfis diferentes
