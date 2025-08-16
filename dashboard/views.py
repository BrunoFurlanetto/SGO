import json
import os as so
import re
from datetime import datetime, timedelta
from itertools import chain

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User, Group
from django.db.models import Q
from django.http import JsonResponse, HttpResponse, FileResponse
from django.shortcuts import render, redirect

from cadastro.models import RelatorioDeAtendimentoPublicoCeu, RelatorioDeAtendimentoColegioCeu, \
    RelatorioDeAtendimentoEmpresaCeu
from escala.models import Escala, DiaLimite
from financeiro.models import FichaFinanceira
from mensagens.models import Mensagem
from orcamento.gerar_orcamento import gerar_pdf_orcamento
from ordemDeServico.models import OrdemDeServico
from peraltas.models import DiaLimitePeraltas, DiaLimitePeraltas, Monitor, FichaDeEvento, InformacoesAdcionais, \
    Vendedor, ProdutosPeraltas, NivelMonitoria, EscalaAcampamento, ClienteColegio
from projetoCEU.integracao_rd import alterar_campos_personalizados, formatar_envio_valores
from orcamento.models import Orcamento, StatusOrcamento, ValoresPadrao, Tratativas, OrcamentosPromocionais, \
    MotivosRecusa
from peraltas.models import DiaLimitePeraltas, DiaLimitePeraltas, Monitor, FichaDeEvento, InformacoesAdcionais
from projetoCEU.envio_de_emails import EmailSender
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
            equipe__icontains=json.dumps(usuario_logado.id))
        # Relatórios de atendimento de colégio
        usuario_colegio = RelatorioDeAtendimentoColegioCeu.objects.filter(
            Q(check_in__month=datetime.now().month) | Q(check_out__month=datetime.now().month)).filter(
            equipe__icontains=json.dumps(usuario_logado.id))
        # Relatórios de atendimento de empresa
        usuario_empresa = RelatorioDeAtendimentoEmpresaCeu.objects.filter(
            Q(check_in__month=datetime.now().month) | Q(check_out__month=datetime.now().month)).filter(
            equipe__icontains=json.dumps(usuario_logado.id))

        relatorios_usuario = list(chain(usuario_publico, usuario_colegio, usuario_empresa))

        # ------------------ Parte para chegar no resumo do mês -------------------
        # n_atividades = contar_atividades(usuario_logado, relatorios_usuario)
        # n_horas = contar_horas(usuario_logado, relatorios_usuario)
        n_atividades = n_horas = 0
        # ------------- Verificação de entrega da disponibilidade do mês sseguinte -------------
        mostrar_aviso_disponibilidade = teste_aviso(request.user.last_login, usuario_logado, request.user.id)
        dia_limite, p = DiaLimite.objects.get_or_create(id=1, defaults={'dia_limite': 25})
        depois_25 = False

        if datetime.now().day > dia_limite.dia_limite:
            depois_25 = True

    # ----------- Seleção da escala do dia -------------
    escalas = Escala.objects.filter(data_escala=datetime.now())
    equipe_escalada = None

    if len(escalas) > 0:
        for escala in escalas:
            equipe_escalada = [Professores.objects.get(pk=professor).usuario.first_name for professor in escala.equipe]

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

        if request.user.has_perms('escala.add_escala'):
            atividades_sem_definicao = OrdemDeServico.atividades_ceu_nao_definidas()
        else:
            atividades_sem_definicao = None

        return render(request, 'dashboard/dashboardCeu.html', {
            'professores': professores, 'relatorios': dados_tabela,
            'data': data_relatorio,
            'equipe_escalada': equipe_escalada,
            'professor': professor_logado,
            'n_atividades': 0,
            'n_horas': 0,
            'mostrar_aviso': mostrar_aviso_disponibilidade,
            'depois_25': depois_25,
            'atividades_sem_definicao': atividades_sem_definicao,
            'eventos_sem_avaliacao': OrdemDeServico.objects.filter(
                check_in_ceu__isnull=False,
                relatorio_ceu_entregue=True,
                ficha_avaliacao=False
            ),
        })


@login_required(login_url='login')
def dashboardPeraltas(request):
    dia_limite_peraltas, p = DiaLimitePeraltas.objects.get_or_create(id=1, defaults={'dia_limite_peraltas': 25})
    msg_monitor = sem_escalas = com_escalas = None
    diretoria = User.objects.filter(pk=request.user.id, groups__name__icontains='Diretoria').exists()
    operacional = User.objects.filter(pk=request.user.id, groups__name__icontains='operacional').exists()
    coordenador_monitoria = request.user.has_perm('peraltas.add_escalaacampamento')
    fichas_financeiras = None
    escalas_feitas = None
    avaliacoes_clientes_colegio = []
    avaliacoes_clientes_corporativo = []
    avaliacoes_coordenador_monitoria = []
    avaliacoes_monitores = []

    try:
        monitor = Monitor.objects.get(usuario=request.user)
    except Monitor.DoesNotExist:
        monitor = None
    else:
        if not isinstance(monitor.nivel, NivelMonitoria):
            messages.error(
                request,
                'Você não tem nenhum nível atribuido no seu perfíl, isto impossibilita que seja escalado. Por favor entrar em contato com o coordenador!'
            )

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
        escalas_feitas = EscalaAcampamento.objects.filter(
            check_in_cliente__date__gte=datetime.today(),
        )
        ordens_colaborador = OrdemDeServico.objects.filter(
            check_in__date__gte=datetime.today(),
        )
    else:
        fichas_colaborador = FichaDeEvento.objects.filter(
            vendedora__usuario=request.user,
            os=False,
            check_in__date__gte=datetime.today(),
        )
        ordens_colaborador = OrdemDeServico.objects.filter(
            vendedor__usuario=request.user,
            check_in__date__gte=datetime.today(),
        )

    fichas = fichas_colaborador.filter(pre_reserva=False)
    pre_reservas = fichas_colaborador.filter(pre_reserva=True, agendado=False)
    confirmados = fichas_colaborador.filter(pre_reserva=True, agendado=True)
    fichas_adesao = fichas_colaborador.filter(os=False, pre_reserva=False)
    avisos = fichas_colaborador.filter(
        pre_reserva=True,
        check_in__date__gte=datetime.today().date(),
        check_in__date__lte=(datetime.today() + timedelta(days=50)).date()
    )
    orcamentos_colaborador = Orcamento.objects.filter(
        colaborador=request.user, data_ultima_edicao__date__gt=(datetime.today() - timedelta(days=365)).date()
    )
    pacotes = OrcamentosPromocionais.objects.filter(
        orcamento__previa=False,
    )

    if diretoria:
        fichas_financeira_aprovacao = FichaFinanceira.objects.filter(autorizado_diretoria=False, negado=False)
    else:
        fichas_financeira_aprovacao = None

    fichas_financeira_colaborador = FichaFinanceira.objects.filter(
        dados_evento__colaborador=request.user.id,
        data_aprovacao_diretoria__isnull=False,
        orcamento__check_in__date__gte=(datetime.today() - timedelta(days=180)).date(),
    )
    msg_monitor = None
    grupos_usuario = request.user.groups.all()
    diretoria = Group.objects.get(name='Diretoria')

    try:
        financeiro = Group.objects.get(name='Financeiro')
    except Group.DoesNotExist:
        financeiro = None

    if financeiro in grupos_usuario:
        fichas_financeiras = FichaFinanceira.objects.filter(
            data_preenchimento_comercial__date__gte=(datetime.today() - timedelta(days=180)).date(),
        )

    if is_ajax(request):
        if request.POST.get('novo_status'):
            status = StatusOrcamento.objects.get(status__icontains=request.POST.get('novo_status'))

            if '_' in request.POST.get('id_orcamento'):
                tratativa = Tratativas.objects.get(id_tratativa=request.POST.get('id_orcamento'))
                tratativa.status = status

                if request.POST.get('motivo_recusa') != '':
                    tratativa.motivo_recusa = request.POST.get('motivo_recusa')

                try:
                    tratativa.save()
                except Exception as e:
                    return JsonResponse({'status': 'error', 'msg': e})
                else:
                    tratativa.perder_orcamentos()
                    return JsonResponse({'status': 'success'})
            else:
                orcamento = Orcamento.objects.get(pk=request.POST.get('id_orcamento'))
                orcamento.status_orcamento = status

                if request.POST.get('motivo_recusa') != '':
                    orcamento.motivo_recusa = request.POST.get('motivo_recusa')
                else:
                    tratativa = Tratativas.objects.get(orcamentos__in=[int(request.POST.get('id_orcamento'))])
                    tratativa.ganhar_orcamento(int(request.POST.get('id_orcamento')))

                try:
                    orcamento.save()
                except Exception as e:
                    return JsonResponse({'status': 'error', 'msg': e})
                else:
                    return JsonResponse({'status': 'success'})

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

    # Inicializa as variáveis vazias
    avaliacoes_clientes_colegio = OrdemDeServico.objects.none()
    avaliacoes_clientes_corporativo = OrdemDeServico.objects.none()
    ordens_coordenadores = OrdemDeServico.objects.none()
    avaliacoes_monitores = EscalaAcampamento.objects.none()
    avaliacoes_coordenador_monitoria = OrdemDeServico.objects.none()

    # Avaliações de colégio
    if request.user.has_perm('pesquisasSatisfacao.add_avaliacaocolegio'):
        avaliacoes_clientes_colegio = OrdemDeServico.objects.filter(
            check_out__date__lte=datetime.today().date(),
            cliente_avaliou=False,
            ficha_de_evento__produto__colegio=True
        ).exclude(
            check_out__date__lt=(datetime.today() - timedelta(days=180)).date()
        ).order_by('-check_out')

    # Avaliações corporativas
    if request.user.has_perm('pesquisasSatisfacao.add_avaliacaocorporativo'):
        avaliacoes_clientes_corporativo = OrdemDeServico.objects.filter(
            check_out__date__lte=datetime.today().date(),
            cliente_avaliou=False,
            ficha_de_evento__produto__colegio=False
        ).exclude(
            check_out__date__lt=(datetime.today() - timedelta(days=180)).date()
        ).order_by('-check_out')

    # Coordenadores avaliados por monitores
    if request.user.has_perm('pesquisasSatisfacao.add_monitoravaliandocoordenacao'):
        ordens_coordenadores = OrdemDeServico.objects.filter(
            check_out__date__lte=datetime.today().date(),
            monitor_responsavel=request.user.monitor,
        ).select_related('ficha_de_evento')

        ficha_excluida = ordens_coordenadores.values_list('ficha_de_evento', flat=True)
        avaliacoes_monitores = EscalaAcampamento.objects.filter(
            check_out_cliente__date__lte=datetime.today().date(),
            ficha_de_evento__os=True
        ).exclude(
            ficha_de_evento__in=ficha_excluida
        ).exclude(
            check_out_cliente__date__lt=(datetime.today() - timedelta(days=180)).date()
        ).order_by('-check_out_cliente')

    # Monitoria avaliada por coordenadores
    if request.user.has_perm('pesquisasSatisfacao.add_coordenacaoavaliandomonitoria'):
        avaliacoes_coordenador_monitoria = OrdemDeServico.objects.filter(
            check_out__date__lte=datetime.today().date(),
            escala=True
        ).exclude(
            check_out__date__lt=(datetime.today() - timedelta(days=180)).date()
        ).order_by('-check_out')

    # Filtro adicional por monitor, se houver
    if monitor:
        if avaliacoes_clientes_colegio.exists():
            avaliacoes_clientes_colegio = avaliacoes_clientes_colegio.filter(monitor_responsavel=monitor)

        if avaliacoes_clientes_corporativo.exists():
            avaliacoes_clientes_corporativo = avaliacoes_clientes_corporativo.filter(monitor_responsavel=monitor)

        if avaliacoes_coordenador_monitoria.exists():
            avaliacoes_coordenador_monitoria = avaliacoes_coordenador_monitoria.filter(
                monitor_responsavel=monitor
            ).exclude(avaliou_monitoria=monitor)

        if avaliacoes_monitores.exists():
            avaliacoes_monitores = avaliacoes_monitores.filter(
                monitores_acampamento=monitor
            ).exclude(avaliou_coordenadores=monitor)

    if request.POST.get('termo_de_aceite'):
        monitor.aceite_do_termo = True
        monitor.save()
    print(Orcamento.objects.filter(previa=True))
    return render(request, 'dashboard/dashboardPeraltas.html', {
        'data_um_ano': (datetime.today() - timedelta(days=365)).date(),
        'msg_acampamento': msg_monitor,
        'termo_monitor': not monitor.aceite_do_termo if monitor else None,
        'diretoria': diretoria in grupos_usuario,
        'fichas_adesao': fichas_adesao,
        'fichas': fichas,
        'ordens_colaborador': ordens_colaborador,
        'pre_reservas': pre_reservas,
        'confirmados': confirmados,
        'sem_escalas': sem_escalas,
        'escalas_feitas': escalas_feitas,
        'avisos': avisos,
        'operacional': operacional,
        'coordenador_monitoria': coordenador_monitoria,
        'comercial': User.objects.filter(pk=request.user.id, groups__name__icontains='comercial').exists(),
        'monitor': monitor,
        'financeiro': financeiro in grupos_usuario,
        'tratativas': Tratativas.objects.filter(
            orcamentos__in=orcamentos_colaborador).distinct() if financeiro not in grupos_usuario else [],
        'pacotes': pacotes,
        'fichas_financeira_aprovacao': fichas_financeira_aprovacao,
        'fichas_financeira_aguardando_aprovacao': fichas_financeira_colaborador.filter(negado=False,
                                                                                       autorizado_diretoria=False),
        'fichas_financeira_negadas': fichas_financeira_colaborador.filter(negado=True),
        'fichas_financeira_aprovadas': fichas_financeira_colaborador.filter(negado=False),
        'fichas_financeiras': fichas_financeiras,
        'previas_orcamento': orcamentos_colaborador.filter(previa=True),
        'orcamentos_aprovacao': Orcamento.objects.filter(
            gerente_responsavel=request.user,
            status_orcamento=StatusOrcamento.objects.get(
                analise_gerencia=True,
                negativa_gerencia=False,
                aprovacao_gerencia=False,
            ),
        ),
        'outras_previas': Orcamento.objects.filter(previa=True).exclude(
            colaborador=request.user) if request.user.has_perm('orcamento.ver_outras_previas') else [],
        'eventos_coordenador_avaliar': avaliacoes_coordenador_monitoria,
        'avaliacoes_monitores': avaliacoes_monitores,
        'avaliacoes_cliente': list(chain(avaliacoes_clientes_colegio, avaliacoes_clientes_corporativo)),
        'motivos_recusa': MotivosRecusa.objects.all(),
        'clientes': ClienteColegio.objects.all(),
        # 'ultimas_versoes': FichaDeEvento.logs_de_alteracao(),
    })
