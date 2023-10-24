import json
from datetime import time, datetime
from io import BytesIO
from itertools import chain

import django.db.utils
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import JsonResponse, HttpResponse, FileResponse
from django.shortcuts import render, redirect

from ordemDeServico.models import CadastroOrdemDeServico, OrdemDeServico, CadastroDadosTransporte, DadosTransporte, \
    TipoVeiculo
from peraltas.models import CadastroFichaDeEvento, CadastroCliente, ClienteColegio, CadastroResponsavel, Responsavel, \
    CadastroInfoAdicionais, CadastroCodigoApp, FichaDeEvento, RelacaoClienteResponsavel, Vendedor, \
    GrupoAtividade, AtividadesEco, AtividadePeraltas, InformacoesAdcionais, CodigosApp, EventosCancelados, Eventos, \
    Monitor, EmpresaOnibus
from projetoCEU import gerar_pdf
from projetoCEU.envio_de_emails import EmailSender
from projetoCEU.utils import verificar_grupo, email_error
from .funcoes import is_ajax, requests_ajax, pegar_refeicoes, ver_empresa_atividades, numero_coordenadores, \
    separar_dados_transporte, salvar_dados_transporte, verificar_codigos
from cadastro.models import RelatorioPublico, RelatorioColegio, RelatorioEmpresa, RelatorioDeAtendimentoPublicoCeu, \
    RelatorioDeAtendimentoColegioCeu
from ceu.models import Professores, Atividades, Locaveis
from .funcoesColegio import pegar_colegios_no_ceu, pegar_empresas_no_ceu, \
    salvar_atividades_colegio, salvar_equipe_colegio, salvar_locacoes_empresa, criar_usuario_colegio
from .funcoesFichaEvento import salvar_atividades_ceu, check_in_and_check_out_atividade, salvar_locacoes_ceu, \
    slavar_atividades_ecoturismo
from .funcoesPublico import salvar_atividades, salvar_equipe, requisicao_ajax, teste_participantes_por_atividade
from django.core.paginator import Paginator


@login_required(login_url='login')
def publico(request, id_relatorio=None):
    if id_relatorio:
        relatorio = RelatorioDeAtendimentoPublicoCeu.objects.get(pk=id_relatorio)
        relatorio_publico = RelatorioPublico(instance=relatorio)
        coordenador_relatorio = Professores.objects.get(pk=relatorio.equipe['coordenador'])
        editar = datetime.now().day - relatorio.data_hora_salvo.day < 2 and coordenador_relatorio.usuario == request.user
    else:
        relatorio = editar = None
        relatorio_publico = RelatorioPublico()

    atividades = Atividades.objects.filter(publico=True)
    professores = Professores.objects.all()

    if is_ajax(request):
        return JsonResponse(requisicao_ajax(request.POST))

    if request.method != 'POST':
        return render(request, 'cadastro/publico.html', {
            'relatorio': relatorio,
            'formulario': relatorio_publico,
            'atividades': atividades,
            'professores': professores,
            'editar': editar
        })

    if request.POST.get('excluir'):
        try:
            relatorio.delete()
        except Exception as e:
            messages.error(request, f'Houve um erro inesperado ({e}), por favor tente mais tarde')
            return redirect('dashboard')
        else:
            messages.success(request, 'Relatório de atendimento ao público apagado com sucesso')
            return redirect('dashboard')
    else:
        if id_relatorio:
            relatorio_publico = RelatorioPublico(request.POST, instance=relatorio)
        else:
            relatorio_publico = RelatorioPublico(request.POST)

        relatorio = relatorio_publico.save(commit=False)
        salvar_equipe(request.POST, relatorio)
        salvar_atividades(request.POST, relatorio)

        try:
            relatorio.save()
        except Exception as e:
            messages.error(request, f'Houve um erro inesperado ({e}), por favor tente mais tarde')
            return redirect('dashboard')
        else:
            messages.success(request, 'Relatório de atendimento ao público salva com sucesso')
            return redirect('dashboard')


@login_required(login_url='login')
def colegio(request, id_relatorio=None):
    relatorio_colegio = RelatorioColegio()
    professores = Professores.objects.all()
    monitores = Monitor.objects.all()
    atividades = Atividades.objects.all()
    ordens = pegar_colegios_no_ceu()

    if request.method != 'POST':
        if not id_relatorio:
            if request.GET.get('colegio'):
                ordem_de_servico = OrdemDeServico.objects.get(pk=request.GET.get('colegio'))
                relatorio_colegio = RelatorioColegio(
                    initial=RelatorioDeAtendimentoColegioCeu.dados_iniciais(ordem_de_servico)
                )

                return render(request, 'cadastro/colegio.html', {
                    'formulario': relatorio_colegio,
                    'ordens': ordens,
                    'ordem': ordem_de_servico,
                    'professores': professores,
                    'monitores': monitores,
                    'atividades': atividades
                })
            else:
                return render(request, 'cadastro/colegio.html', {
                    'formulario': relatorio_colegio,
                    'ordens': ordens,
                    'professores': professores
                })
        else:
            relatorio = RelatorioDeAtendimentoColegioCeu.objects.get(pk=id_relatorio)
            relatorio_colegio = RelatorioColegio(instance=relatorio)
            coordenador_relatorio = Professores.objects.get(pk=relatorio.equipe['coordenador'])
            editar = datetime.now().day - relatorio.data_hora_salvo.day < 2 and coordenador_relatorio.usuario == request.user

            return render(request, 'cadastro/colegio.html', {
                'relatorio': relatorio,
                'formulario': relatorio_colegio,
                'professores': professores,
                'monitores': monitores,
                'atividades': atividades,
                'editar': editar
            })

    if is_ajax(request):
        return JsonResponse(requests_ajax(request.POST))

    if id_relatorio:
        relatorio_editado = RelatorioDeAtendimentoColegioCeu.objects.get(pk=id_relatorio)
        relatorio_colegio = RelatorioColegio(request.POST, instance=relatorio_editado)
    else:
        ordem = OrdemDeServico.objects.get(pk=request.POST.get('ordem'))
        relatorio_colegio = RelatorioColegio(request.POST, initial=RelatorioDeAtendimentoColegioCeu.dados_iniciais(ordem))

    if relatorio_colegio.is_valid():
        relatorio = relatorio_colegio.save(commit=False)
        ordem = OrdemDeServico.objects.get(id=int(request.POST.get('ordem')))
        relatorio.check_in = ordem.check_in_ceu
        relatorio.check_out = ordem.check_out_ceu
        salvar_equipe_colegio(request.POST, relatorio)
        salvar_atividades_colegio(request.POST, relatorio)

        if request.POST.get('loc_1'):
            salvar_locacoes_empresa(request.POST, relatorio)

        try:
            novo_colegio = relatorio_colegio.save()
        except Exception as e:
            email_error(request.user.get_full_name(), e, __name__)
            messages.error(request, 'Houve um erro insperado, por favor tente novamente mais tarde!')
            return redirect('dashboardCeu')
        else:
            ordem.relatorio_ceu_entregue = True
            ordem.save()

            if not id_relatorio:
                email, senha = criar_usuario_colegio(novo_colegio, ordem.id)
            else:
                return redirect('dashboardCeu')

            return render(request, 'cadastro/colegio.html', {
                'formulario': relatorio_colegio,
                'professores': professores,
                'mostrar': True,
                'email': email,
                'senha': senha
            })
    else:
        messages.warning(request, relatorio_colegio.errors)
        ordem_de_servico = OrdemDeServico.objects.get(id=int(request.POST.get('id_ordem')))

        return render(request, 'cadastro/colegio.html', {
            'formulario': relatorio_colegio,
            'ordens': ordens,
            'ordem': ordem_de_servico,
            'professores': professores,
            'monitores': monitores,
            'atividades': atividades
        })


@login_required(login_url='login')
def empresa(request):
    relatorio_empresa = RelatorioEmpresa()
    professores = Professores.objects.all()
    empresas = pegar_empresas_no_ceu()

    if request.method != 'POST':
        return render(request, 'cadastro/empresa.html', {'formulario': relatorio_empresa,
                                                         'professores': professores,
                                                         'empresas': empresas})

    if is_ajax(request):
        return JsonResponse(requests_ajax(request.POST))

    relatorio_empresa = RelatorioEmpresa(request.POST)

    if relatorio_empresa.is_valid():
        ordem = OrdemDeServico.objects.get(id=int(request.POST.get('id_ordem')))
        relatorio = relatorio_empresa.save(commit=False)
        salvar_equipe_colegio(request.POST, relatorio)
        salvar_locacoes_empresa(request.POST, relatorio)

        if request.POST.get('ativ_1'):
            salvar_atividades_colegio(request.POST, relatorio)

        try:
            relatorio_empresa.save()
        except Exception as e:
            email_error(request.user.get_full_name(), e, __name__)
            messages.error(request, 'Houve um erro inesperado, por favor, tente mais tarde')
            relatorio_empresa = RelatorioEmpresa()
            return render(request, 'cadastro/empresa.html', {'formulario': relatorio_empresa,
                                                             'professores': professores,
                                                             'empresas': empresas})
        else:
            ordem.relatorio_ceu_entregue = True
            ordem.save()
            messages.success(request, 'Relatório de atendimento salvo com sucesso!')
            return redirect('dashboard')
    else:
        messages.warning(request, relatorio_empresa.errors)
        return render(request, 'cadastro/empresa.html', {'formulario': relatorio_empresa,
                                                         'professores': professores,
                                                         'empresas': empresas})


@login_required(login_url='login')
def ordemDeServico(request, id_ordem_de_servico=None, id_ficha_de_evento=None):
    atividades_acampamento = AtividadePeraltas.objects.all()
    grupos_atividades_acampamento = GrupoAtividade.objects.all()
    tipos_veiculos = TipoVeiculo.objects.all()
    form_transporte = CadastroDadosTransporte()
    forms_transporte = []
    transportes_salvos = []
    transporte = None

    if is_ajax(request):
        if request.method == 'GET':
            viacoes = [{'id': viacao.id, 'tipo': viacao.viacao} for viacao in EmpresaOnibus.objects.all()]
            veiculos = [{'id': veiculo.id, 'tipo': veiculo.tipo_veiculo} for veiculo in tipos_veiculos]

            return JsonResponse({'viacoes': viacoes, 'veiculos': veiculos})

        if request.POST.get('id_dado'):
            try:
                transporte_excluido = DadosTransporte.objects.get(pk=request.POST.get('id_dado'))
                transporte_excluido.delete()
            except Exception as e:
                return HttpResponse(e)
            else:
                return HttpResponse(True)

        return JsonResponse(requests_ajax(request.POST))

    if request.POST.get('gerar_pdf'):
        ordem_pdf = OrdemDeServico.objects.get(pk=id_ordem_de_servico)
        gerar_pdf.ordem_de_servico(ordem_pdf)

        return FileResponse(
            open('temp/ordem_de_servico.pdf', 'rb'),
            content_type='application/pdf',
            as_attachment=True,
            filename=f'Ordem de serviço de {ordem_pdf.ficha_de_evento.cliente}.pdf'
        )

    if id_ordem_de_servico:
        ordem_servico = OrdemDeServico.objects.get(id=int(id_ordem_de_servico))
        form = CadastroOrdemDeServico(instance=ordem_servico)

        for transporte in ordem_servico.dados_transporte.all():
            form_transporte = CadastroDadosTransporte(instance=transporte)
            forms_transporte.append(form_transporte)

        ficha_de_evento = FichaDeEvento.objects.get(id=ordem_servico.ficha_de_evento.id)
        atividades_eco = AtividadesEco.objects.all()
        atividades_ceu = Atividades.objects.all()
        espacos = Locaveis.objects.all()
        fichas_de_evento = None
    else:
        form = CadastroOrdemDeServico()
        fichas_de_evento = FichaDeEvento.objects.filter(os=False, pre_reserva=False).order_by('check_in')
        ficha_de_evento = ordem_servico = None
        atividades_eco = atividades_ceu = espacos = None

    if id_ficha_de_evento:
        ficha_de_evento = FichaDeEvento.objects.get(id=int(id_ficha_de_evento))

    if request.method != 'POST':
        return render(request, 'cadastro/ordem_de_servico.html', {
            'form': form,
            'forms_transporte': forms_transporte if len(forms_transporte) > 0 else [form_transporte],
            'fichas': fichas_de_evento,
            'ficha_de_evento': ficha_de_evento,
            'ordem_servico': ordem_servico,
            'atividades_acampamento': atividades_acampamento,
            'grupos_atividades_acampamento': grupos_atividades_acampamento,
            'atividades_eco': atividades_eco,
            'atividades_ceu': atividades_ceu,
            'espacos': espacos,
            'tipos_veiculos': tipos_veiculos,
            'n_coordenadores': numero_coordenadores(ficha_de_evento)
        })

    if request.POST.get('excluir'):
        try:
            EventosCancelados.objects.create(
                cliente=ordem_servico.ficha_de_evento.cliente.__str__(),
                cnpj_cliente=ordem_servico.ficha_de_evento.cliente.cnpj,
                estagio_evento='ordem_servico',
                atendente=ordem_servico.vendedor.usuario.get_full_name(),
                produto_contratado=ordem_servico.ficha_de_evento.produto,
                produto_corporativo_contratado=ordem_servico.ficha_de_evento.produto_corporativo,
                data_entrada=ordem_servico.ficha_de_evento.data_preenchimento,
                data_saida=datetime.now().date(),
                data_evento=ordem_servico.check_in.date(),
                motivo_cancelamento=request.POST.get('motivo_cancelamento'),
                participantes=ordem_servico.n_participantes,
                tipo_evento='colegio' if ordem_servico.tipo == 'Colégio' else 'corporativo'
            )
            ordem_servico.ficha_de_evento.os = False
            ordem_servico.ficha_de_evento.save()

            if ordem_servico.dados_transporte:
                for dados_transporte in ordem_servico.dados_transporte.all():
                    dados_transporte.delete()

            ordem_servico.delete()
        except Exception as e:
            messages.error(request, f'Houve um erro inesperado: {e}. Tente novamente mais tarde')
        else:
            messages.success(request, 'Ordem de serviço excluída com sucesso')

        return redirect('dashboard')

    if id_ordem_de_servico:
        form = CadastroOrdemDeServico(request.POST, request.FILES, instance=ordem_servico)
        permicao_coordenacao = ordem_servico.permicao_coordenadores

        if request.POST.get('empresa_onibus'):
            transportes_salvos = DadosTransporte.salvar_dados(request.POST)
    else:
        permicao_coordenacao = False
        form = CadastroOrdemDeServico(request.POST, request.FILES)

        if request.POST.get('empresa_onibus'):
            transportes_salvos = DadosTransporte.salvar_dados(request.POST)

    ordem_de_servico = form.save(commit=False)
    ordem_de_servico.permicao_coordenadores = permicao_coordenacao
    ficha = FichaDeEvento.objects.get(id=int(request.POST.get('ficha_de_evento')))
    slavar_atividades_ecoturismo(request.POST, ordem_de_servico)

    try:
        salvar_atividades_ceu(request.POST, ordem_de_servico)
        check_in_and_check_out_atividade(ordem_de_servico)
        salvar_locacoes_ceu(request.POST, ordem_de_servico)

        ordem_de_servico = form.save()

        try:
            evento = Eventos.objects.get(ficha_de_evento=ficha)
        except Eventos.DoesNotExist:
            ficha_para_evento = FichaDeEvento.objects.get(id=ordem_de_servico.ficha_de_evento.id)
            evento = Eventos.objects.create(ficha_de_evento=ficha_para_evento)

        evento.ordem_de_servico = ordem_de_servico
        evento.save()

        if ficha.escala:
            ordem_de_servico.escala = True

        if len(request.POST.getlist('empresa_onibus')) > 0:
            ordem_de_servico.dados_transporte.set(transportes_salvos)

        ordem_de_servico.save()
    except Exception as e:
        email_error(request.user.get_full_name(), e, __name__)
        messages.error(request, 'Houve um erro inesperado ao salvar a ordem de serviço, por favor tente mais tarde,'
                                f' ou entre em contato com o desenvolvedor. ({e})')

        return redirect('dashboardPeraltas')
    else:
        ficha.os = True
        ficha.save()

        if ordem_de_servico.tipo == 'Empresa':
            messages.success(request, f'Ordem de serviço da empresa {ordem_de_servico.instituicao} salva com sucesso')
        else:
            messages.success(request, f'Ordem de serviço do colégio {ordem_de_servico.instituicao} salva com sucesso')

        if not id_ordem_de_servico:
            EmailSender([ficha.vendedora.usuario.email]).mensagem_cadastro_ordem(
                ordem_de_servico.check_in, ordem_de_servico.check_out, ordem_de_servico.ficha_de_evento.cliente
            )

            if len(ordem_de_servico.dados_transporte.all()) > 0:
                for transporte in ordem_de_servico.dados_transporte.all():
                    EmailSender([transporte.monitor_embarque.usuario.email]).mensagem_monitor_embarque(
                        ordem_de_servico.ficha_de_evento.cliente,
                        ordem_de_servico.check_in,
                        transporte.monitor_embarque.usuario.get_full_name()
                    )

        return redirect('dashboardPeraltas')


@login_required(login_url='login')
def fichaDeEvento(request, id_pre_reserva=None, id_ficha_de_evento=None):
    form = CadastroFichaDeEvento()
    form_transporte = CadastroDadosTransporte()
    form_adicionais = CadastroInfoAdicionais()
    form_app = CadastroCodigoApp()
    atividades_ceu = Atividades.objects.all()
    grupos_atividade = GrupoAtividade.objects.all()
    dados_pre_reserva = ficha_de_evento = None
    diretoria = User.objects.filter(pk=request.user.id, groups__name='Diretoria').exists()

    try:
        vendedora = Vendedor.objects.get(usuario=request.user)
        form.vendedora = vendedora.id
    except Vendedor.DoesNotExist:
        ...
    except Exception as e:
        email_error(request.user.get_full_name(), e, __name__)
        messages.error(request, f'Houve um erro inesperado: {e}. Tente novamente mais tarde.')
        return redirect('dashboard')

    if is_ajax(request):
        if request.method == 'GET':
            if request.GET.getlist('codigos_eficha[]'):
                return JsonResponse(verificar_codigos(request.GET.getlist('codigos_eficha[]')))

            return HttpResponse(ClienteColegio.objects.get(pk=request.GET.get('id_cliente')).cnpj)

        if request.FILES != {}:
            return JsonResponse(requests_ajax(request.POST, request.FILES))
        else:
            if request.POST.get('id_cliente_sem_app') and request.POST.get('infos') == 'app':
                cliente = ClienteColegio.objects.get(pk=request.POST.get('id_cliente_sem_app'))
                cliente.codigo_app_pf = request.POST.get('cliente_pf')
                cliente.codigo_app_pj = request.POST.get('cliente_pj')
                cliente.save()

            return JsonResponse(requests_ajax(request.POST))

    if request.method != 'POST':
        if id_pre_reserva:
            pre_reserva = FichaDeEvento.objects.get(pk=id_pre_reserva, pre_reserva=True, agendado=True)
            form = CadastroFichaDeEvento(instance=pre_reserva)

            return render(request, 'cadastro/ficha-de-evento.html', {
                'form': form,
                'form_transporte': form_transporte,
                'formAdicionais': form_adicionais,
                'formApp': form_app,
                'pre_reserva': pre_reserva,
                'grupos_atividade': grupos_atividade,
                'atividades_ceu': atividades_ceu,
                'diretoria': diretoria,
                'coorporativo': not pre_reserva.produto.colegio,
                'editando': False
            })

        if id_ficha_de_evento:
            ficha_de_evento = FichaDeEvento.objects.get(pk=id_ficha_de_evento)
            form = CadastroFichaDeEvento(instance=ficha_de_evento)
            form_adicionais = CadastroInfoAdicionais(instance=ficha_de_evento.informacoes_adcionais)
            form_app = CadastroCodigoApp(instance=ficha_de_evento.codigos_app)

            return render(request, 'cadastro/ficha-de-evento.html', {
                'ficha_de_evento': ficha_de_evento,
                'form': form,
                'formAdicionais': form_adicionais,
                'formApp': form_app,
                'grupos_atividade': grupos_atividade,
                'atividades_ceu': atividades_ceu,
                'diretoria': diretoria,
                'editando': True
            })

        return render(request, 'cadastro/ficha-de-evento.html', {
            'form': form,
            'formAdicionais': form_adicionais,
            'formApp': form_app,
            'grupos_atividade': grupos_atividade,
            'atividades_ceu': atividades_ceu,
            'diretoria': diretoria,
            'editando': False
        })

    if request.POST.get('excluir'):
        ficha_de_evento = FichaDeEvento.objects.get(pk=id_ficha_de_evento)

        try:
            EventosCancelados.objects.create(
                cliente=ficha_de_evento.cliente.__str__(),
                cnpj_cliente=ficha_de_evento.cliente.cnpj,
                estagio_evento='ficha_evento',
                atendente=ficha_de_evento.vendedora.usuario.get_full_name(),
                produto_contratado=ficha_de_evento.produto,
                produto_corporativo_contratado=ficha_de_evento.produto_corporativo,
                data_entrada=ficha_de_evento.data_preenchimento,
                data_saida=datetime.now().date(),
                data_evento=ficha_de_evento.check_in.date(),
                motivo_cancelamento=request.POST.get('motivo_cancelamento'),
                participantes=ficha_de_evento.qtd_convidada,
                tipo_evento='corporativo' if ficha_de_evento.produto_corporativo else 'colegio'
            )
            ficha_de_evento.delete()
        except Exception as e:
            messages.error(request, f'Houve um erro inesperado ({e}). Tente novamente mais tarde.')
            return redirect('dashboard')
        else:
            messages.success(request, 'Ficha de evento escluída com sucesso!')
            return redirect('dashboard')

    if id_ficha_de_evento or id_pre_reserva:
        ficha_de_evento = FichaDeEvento.objects.get(pk=id_ficha_de_evento if id_ficha_de_evento else id_pre_reserva)
        escala = ficha_de_evento.escala
        os = ficha_de_evento.os
        form = CadastroFichaDeEvento(request.POST, request.FILES, instance=ficha_de_evento)
    else:
        os = escala = False
        form = CadastroFichaDeEvento(request.POST, request.FILES)

    if form.is_valid():
        novo_evento = form.save(commit=False)
        novo_evento.refeicoes = pegar_refeicoes(request.POST)
        novo_evento.empresa = ver_empresa_atividades(request.POST)
        novo_evento.pre_reserva = False
        novo_evento.os = os
        novo_evento.escala = escala
        novo_evento.adesao = (novo_evento.qtd_confirmada / novo_evento.qtd_convidada) * 100

        if not id_ficha_de_evento:
            novo_evento.data_preenchimento = datetime.today().date()

        if len(request.POST.getlist('locacoes_ceu')) > 0:
            novo_evento.informacoes_locacoes = FichaDeEvento.juntar_dados_locacoes(request.POST)

        try:
            form.save()
        except Exception as e:
            email_error(request.user.get_full_name(), e, __name__)
            messages.error(request, 'Houve um erro inesperado, por favor tente mais tarde')

            return redirect('ficha_de_evento')
        else:
            if not id_ficha_de_evento:
                coordenadores_acampamento = User.objects.filter(groups__name='Coordenador acampamento')
                operacional = User.objects.filter(groups__name='Operacional')
                lista_emails = set()

                for grupo in [operacional, coordenadores_acampamento]:
                    for colaborador in grupo:
                        lista_emails.add(colaborador.email)

                EmailSender(
                    list(lista_emails)
                ).mensagem_cadastro_ficha(
                    novo_evento.check_in,
                    novo_evento.check_out,
                    novo_evento.cliente,
                    novo_evento.vendedora
                )

            messages.success(
                request,
                'Ficha de evento salva com sucesso' if not ficha_de_evento else 'Ficha de evento editada com sucesso'
            )

            return redirect('dashboard')
    else:
        messages.warning(request, form.errors)
        return render(request, 'cadastro/ficha-de-evento.html', {
            'form': form,
            'form_transporte': form_transporte,
            'formAdicionais': form_adicionais,
            'formApp': form_app,
            'dados_pre_reserva': dados_pre_reserva,
            'grupos_atividade': grupos_atividade,
            'atividades_ceu': atividades_ceu,
            'diretoria': diretoria,
        })


@login_required(login_url='login')
def listaCliente(request):
    form = CadastroCliente()
    form_responsavel = CadastroResponsavel()
    clientes = ClienteColegio.objects.all().order_by('-id')
    paginacao = Paginator(clientes, 5)
    pagina = request.GET.get('page')
    clientes = paginacao.get_page(pagina)

    if is_ajax(request):
        return JsonResponse(requests_ajax(request.POST, usuario=request.user))

    # ------------------------------------------------------------------------------------------------------------------
    if request.GET.get('termo'):
        termo = request.GET.get('termo')

        if termo is None or not termo:
            messages.add_message(request, messages.ERROR, 'Campo busca não pode ficar vazio')
            return redirect('lista_cliente')

        clientes = ClienteColegio.objects.filter(cnpj=termo)

        paginacao = Paginator(clientes, 5)
        pagina = request.GET.get('page')
        clientes = paginacao.get_page(pagina)

        return render(request, 'cadastro/lista-cliente.html', {'clientes': clientes,
                                                               'form': form,
                                                               'formResponsavel': form_responsavel})

    if request.method != 'POST':
        return render(request, 'cadastro/lista-cliente.html', {'form': form,
                                                               'clientes': clientes,
                                                               'formResponsavel': form_responsavel})

    if request.POST.get('update') == 'true':
        cliente = ClienteColegio.objects.get(id=int(request.POST.get('id')))
        responsavel_cadastro_cliente = cliente.responsavel_cadastro
        form = CadastroCliente(request.POST, instance=cliente)

        if form.is_valid():
            try:
                form.save()
            except Exception as e:
                email_error(request.user.get_full_name(), e, __name__)
                messages.error(request, 'Houve um erro inesperado, por favor tente mais tarde')
            else:
                cliente.responsavel_alteracao = request.user
                cliente.responsavel_cadastro = responsavel_cadastro_cliente
                cliente.save()
                messages.success(request, 'Cliente atualizado com sucesso!')
                return redirect('lista_cliente')
        else:
            messages.warning(request, form.errors)
            return redirect('lista_cliente')


@login_required(login_url='login')
def listaResponsaveis(request):
    responsavel_sem_cliente = []
    form = CadastroResponsavel()
    clientes = ClienteColegio.objects.all()
    responsaveis = Responsavel.objects.all()

    for responsavel in responsaveis:
        try:
            relacao = RelacaoClienteResponsavel.objects.get(responsavel=responsavel.id)
        except RelacaoClienteResponsavel.DoesNotExist:
            responsavel_sem_cliente.append(responsavel.nome)
        else:
            responsavel.responsavel_por = relacao.cliente.nome_fantasia

    if len(responsavel_sem_cliente) > 0:
        messages.warning(request, f'Responsáveis sem cliente cadastrado na ficha: {", ".join(responsavel_sem_cliente)}')

    paginacao = Paginator(responsaveis, 5)
    pagina = request.GET.get('page')
    responsaveis = paginacao.get_page(pagina)

    # ---------------------------------------------
    if request.GET.get('cliente'):
        cliente = request.GET.get('cliente')

        if cliente is None or not cliente:
            messages.add_message(request, messages.ERROR, 'Campo busca não pode ficar vazio')
            return redirect('lista_responsaveis')

        responsaveis = list(chain())

        try:
            relacoes = RelacaoClienteResponsavel.objects.filter(cliente=int(cliente))
            print(relacoes)
        except RelacaoClienteResponsavel.DoesNotExist:
            responsaveis = []
        except Exception as e:
            email_error(request.user.get_full_name(), e, __name__)
            messages.error(request, 'Houve um erro inesperado, por favor tentar mais tarde!')
            return redirect('lista_responsaveis')
        else:
            for relacao in relacoes:
                for responsavel in relacao.responsavel.all():
                    responsaveis.append(Responsavel.objects.get(id=responsavel.id))

            for responsavel in responsaveis:
                relacao = RelacaoClienteResponsavel.objects.get(responsavel=responsavel.id)
                responsavel.responsavel_por = relacao.cliente.nome_fantasia

        paginacao = Paginator(responsaveis, 5)
        pagina = request.GET.get('page')
        responsaveis = paginacao.get_page(pagina)

        return render(request, 'cadastro/lista-responsaveis.html', {'form': form,
                                                                    'clientes': clientes,
                                                                    'responsaveis': responsaveis})

    if request.method != 'POST':
        return render(request, 'cadastro/lista-responsaveis.html', {'form': form,
                                                                    'clientes': clientes,
                                                                    'responsaveis': responsaveis})

    if is_ajax(request):
        return JsonResponse(requests_ajax(request.POST))

    if request.POST.get('update') == 'true':
        responsavel = Responsavel.objects.get(id=int(request.POST.get('id')))
        responsavel_cadastro = responsavel.responsavel_cadastro
        cliente = ClienteColegio.objects.get(id=int(request.POST.get('id_responsavel_por')))
        form = CadastroResponsavel(request.POST, instance=responsavel)

        if form.is_valid():
            try:
                form.save()
            except Exception as e:
                email_error(request.user.get_full_name(), e, __name__)
                messages.error(request, 'Houve um erro inesperado, tente novemente mais tarde!')
                return redirect('lista_responsaveis')
            else:
                responsavel.responsavel_cadastro = responsavel_cadastro
                responsavel.responsavel_atualizacao = request.user
                responsavel.save()

                try:
                    RelacaoClienteResponsavel.objects.get(responsavel=responsavel.id)
                except RelacaoClienteResponsavel.DoesNotExist:
                    nova_relacao = RelacaoClienteResponsavel.objects.create(cliente=cliente)
                    nova_relacao.responsavel.add(responsavel.id)

                messages.success(request, 'Dados do responsável atualizada com sucesso!')
                return redirect('lista_responsaveis')

        else:
            messages.warning(request, form.errors)
            return redirect('lista_responsaveis')

    form = CadastroResponsavel(request.POST)

    if form.is_valid():
        try:
            novo_responsavel = form.save(commit=False)
            novo_responsavel.responsavel_cadastro = request.user
            novo_responsavel = form.save()
        except Exception as e:
            email_error(request.user.get_full_name(), e, __name__)
            messages.error(request, 'Houve um erro inesperado, tente novemente mais tarde!')
            return redirect('lista_responsaveis')
        else:

            try:
                relacao = RelacaoClienteResponsavel.objects.get(cliente=int(request.POST.get('responsavel_por')))
            except RelacaoClienteResponsavel.DoesNotExist:
                cliente = ClienteColegio.objects.get(id=int(request.POST.get('responsavel_por')))
                RelacaoClienteResponsavel(cliente=cliente).save()
                relacao = RelacaoClienteResponsavel.objects.get(cliente=int(request.POST.get('responsavel_por')))
            except Exception as e:
                email_error(request.user.get_full_name(), e, __name__)
                messages.error(request, 'Houve um erro inesperado, tente novemente mais tarde!')
                return redirect('lista_responsaveis')
            finally:
                relacao.responsavel.add(novo_responsavel.id)

            messages.success(request, 'Novo responsável salvo com sucesso!')
            return redirect('lista_responsaveis')

    else:
        messages.warning(request, form.errors)
        return redirect('lista_responsaveis')
