from itertools import chain
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.shortcuts import render, redirect

from ordemDeServico.models import CadastroOrdemDeServico, OrdemDeServico
from peraltas.models import CadastroFichaDeEvento, CadastroCliente, ClienteColegio, CadastroResponsavel, Responsavel, \
    CadastroInfoAdicionais, CadastroCodigoApp, FichaDeEvento, RelacaoClienteResponsavel, Vendedor, \
    GrupoAtividade, CadastroDadosTransporte, AtividadesEco, AtividadePeraltas, InformacoesAdcionais, CodigosApp, \
    DadosTransporte
from projetoCEU.utils import verificar_grupo, email_error
from .funcoes import is_ajax, requests_ajax, pegar_refeicoes, ver_empresa_atividades
from cadastro.models import RelatorioPublico, RelatorioColegio, RelatorioEmpresa
from ceu.models import Professores, Atividades, Locaveis
from .funcoesColegio import pegar_colegios_no_ceu, pegar_empresas_no_ceu, \
    salvar_atividades_colegio, salvar_equipe_colegio, salvar_locacoes_empresa, criar_usuario_colegio
from .funcoesFichaEvento import salvar_atividades_ceu, check_in_and_check_out_atividade, salvar_locacoes_ceu, \
    slavar_atividades_ecoturismo
from .funcoesPublico import salvar_atividades, salvar_equipe, requisicao_ajax
from django.core.paginator import Paginator


@login_required(login_url='login')
def publico(request):
    relatorio_publico = RelatorioPublico()
    atividades = Atividades.objects.filter(publico=True)
    professores = Professores.objects.all()
    range_j = range(1, 5)

    if is_ajax(request):
        return JsonResponse(requisicao_ajax(request.POST))

    if request.method != 'POST':
        return render(request, 'cadastro/publico.html', {'formulario': relatorio_publico,
                                                         'rangej': range_j, 'atividades': atividades,
                                                         'professores': professores})

    relatorio_publico = RelatorioPublico(request.POST)
    relatorio = relatorio_publico.save(commit=False)
    salvar_equipe(request.POST, relatorio)
    salvar_atividades(request.POST, relatorio)

    try:
        relatorio.save()
    except Exception as e:
        email_error(request.user.get_full_name(), e, __name__)
        messages.error(request, 'Houve um erro inesperado, por favor tente mais tarde')
        return render(request, 'cadastro/publico.html', {'formulario': relatorio_publico,
                                                         'rangej': range_j, 'atividades': atividades,
                                                         'professores': professores})
    else:
        messages.success(request, 'Relatório de atendimento ao público salva com sucesso')
        return redirect('dashboard')


@login_required(login_url='login')
def colegio(request):
    relatorio_colegio = RelatorioColegio()
    professores = Professores.objects.all()
    colegios_no_ceu = pegar_colegios_no_ceu()

    if request.method != 'POST':
        return render(request, 'cadastro/colegio.html', {'formulario': relatorio_colegio,
                                                         'colegios': colegios_no_ceu,
                                                         'professores': professores})

    if is_ajax(request):
        return JsonResponse(requests_ajax(request.POST))

    relatorio_colegio = RelatorioColegio(request.POST)

    if relatorio_colegio.is_valid():
        relatorio = relatorio_colegio.save(commit=False)
        ordem = OrdemDeServico.objects.get(id=int(request.POST.get('id_ordem')))
        salvar_equipe_colegio(request.POST, relatorio)
        salvar_atividades_colegio(request.POST, relatorio)

        if request.POST.get('loc_1'):
            salvar_locacoes_empresa(request.POST, relatorio)

        try:
            novo_colegio = relatorio_colegio.save()
        except Exception as e:
            email_error(request.user.get_full_name(), e, __name__)
            messages.error(request, 'Houve um erro insperado, por favor tente novamente mais tarde!')
            relatorio_colegio = RelatorioColegio()
            return render(request, 'cadastro/colegio.html', {'formulario': relatorio_colegio,
                                                             'colegios': colegios_no_ceu,
                                                             'professores': professores})
        else:
            ordem.relatorio_ceu_entregue = True
            ordem.save()

            email, senha = criar_usuario_colegio(novo_colegio)

            return render(request, 'cadastro/colegio.html', {'formulario': relatorio_colegio,
                                                             'colegios': colegios_no_ceu,
                                                             'professores': professores,
                                                             'mostrar': True,
                                                             'email': email,
                                                             'senha': senha})

    else:
        messages.warning(request, relatorio_colegio.errors)
        return render(request, 'cadastro/colegio.html', {'formulario': relatorio_colegio,
                                                         'colegios': colegios_no_ceu,
                                                         'professores': professores})


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

    if id_ordem_de_servico:
        ordem_servico = OrdemDeServico.objects.get(id=int(id_ordem_de_servico))
        form = CadastroOrdemDeServico(instance=ordem_servico)
        ficha_de_evento = FichaDeEvento.objects.get(id=ordem_servico.ficha_de_evento.id)
        atividades_eco = AtividadesEco.objects.all()
        atividades_ceu = Atividades.objects.all()
        espacos = Locaveis.objects.all()
        fichas_de_evento = None
    else:
        form = CadastroOrdemDeServico()
        fichas_de_evento = FichaDeEvento.objects.filter(os=False).order_by('check_in')
        ficha_de_evento = ordem_servico = None
        atividades_eco = atividades_ceu = espacos = None

    if id_ficha_de_evento:
        ficha_de_evento = FichaDeEvento.objects.get(id=int(id_ficha_de_evento))

    if request.method != 'POST':
        return render(request, 'cadastro/ordem_de_servico.html', {
            'form': form,
            'fichas': fichas_de_evento,
            'ficha_de_evento': ficha_de_evento,
            'ordem_servico': ordem_servico,
            'atividades_acampamento': atividades_acampamento,
            'grupos_atividades_acampamento': grupos_atividades_acampamento,
            'atividades_eco': atividades_eco,
            'atividades_ceu': atividades_ceu,
            'espacos': espacos
        })

    if is_ajax(request):
        return JsonResponse(requests_ajax(request.POST))

    if request.POST.get('excluir'):
        try:
            ordem_servico.delete()
        except Exception as e:
            messages.error(request, f'Houve um erro inesperado: {e}. Tente novamente mais tarde')
        else:
            messages.success(request, 'Ordem de serviço excluída com sucesso')

        return redirect('dashboard')

    if id_ordem_de_servico:
        form = CadastroOrdemDeServico(request.POST, request.FILES, instance=ordem_servico)
    else:
        form = CadastroOrdemDeServico(request.POST, request.FILES)

    ordem_de_servico = form.save(commit=False)
    ficha = FichaDeEvento.objects.get(id=int(request.POST.get('ficha_de_evento')))

    try:
        slavar_atividades_ecoturismo(request.POST, ordem_de_servico)
        salvar_atividades_ceu(request.POST, ordem_de_servico)
        check_in_and_check_out_atividade(ordem_de_servico)
        salvar_locacoes_ceu(request.POST, ordem_de_servico)

        if ficha.escala:
            form.escala = True

        form.save()
    except Exception as e:
        email_error(request.user.get_full_name(), e, __name__)
        messages.error(request, 'Houve um erro inesperado ao salvar a ficha do evento, por favor tente mais tarde,'
                                'ou entre em contato com o desenvolvedor.')

        return redirect('dashboardPeraltas')
    else:
        ficha.os = True
        ficha.save()

        if ordem_de_servico.tipo == 'Empresa':
            messages.success(request, f'Ordem de serviço da empresa {ordem_de_servico.instituicao} salva com sucesso')
        else:
            messages.success(request, f'Ordem de serviço do colégio {ordem_de_servico.instituicao} salva com sucesso')

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

    try:
        vendedora = Vendedor.objects.get(usuario=request.user)
        form.vendedora = vendedora.id
    except Vendedor.DoesNotExist:
        ...
    except Exception as e:
        email_error(request.user.get_full_name(), e, __name__)
        messages.error(request, f'Houve um erro inesperado: {e}. Tente novamente mais tarde.')
        return redirect('dashboard')

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
                'editando': False
            })

        if id_ficha_de_evento:
            ficha_de_evento = FichaDeEvento.objects.get(pk=id_ficha_de_evento)
            dados_transporte = ficha_de_evento.informacoes_adcionais.informacoes_transporte
            form = CadastroFichaDeEvento(instance=ficha_de_evento)
            form_adicionais = CadastroInfoAdicionais(instance=ficha_de_evento.informacoes_adcionais)
            form_app = CadastroCodigoApp(instance=ficha_de_evento.codigos_app)
            form_transporte = CadastroDadosTransporte(instance=dados_transporte)

            return render(request, 'cadastro/ficha-de-evento.html', {
                'ficha_de_evento': ficha_de_evento,
                'dados_transporte': dados_transporte,
                'form': form,
                'form_transporte': form_transporte,
                'formAdicionais': form_adicionais,
                'formApp': form_app,
                'grupos_atividade': grupos_atividade,
                'atividades_ceu': atividades_ceu,
                'editando': True
            })

        return render(request, 'cadastro/ficha-de-evento.html', {
            'form': form,
            'form_transporte': form_transporte,
            'formAdicionais': form_adicionais,
            'formApp': form_app,
            'grupos_atividade': grupos_atividade,
            'atividades_ceu': atividades_ceu,
            'editando': False
        })

    if is_ajax(request):
        if request.FILES != {}:
            return JsonResponse(requests_ajax(request.POST, request.FILES))
        else:
            return JsonResponse(requests_ajax(request.POST))

    if request.POST.get('excluir'):
        ficha_de_evento = FichaDeEvento.objects.get(pk=id_ficha_de_evento)
        ficha_de_evento.delete()
        messages.success(request, 'Ficha de evento excluída com sucesso!')

        return redirect('dashboard')

    if id_ficha_de_evento or id_pre_reserva:
        ficha_de_evento = FichaDeEvento.objects.get(pk=id_ficha_de_evento if id_ficha_de_evento else id_pre_reserva)
        form = CadastroFichaDeEvento(request.POST, request.FILES, instance=ficha_de_evento)
    else:
        form = CadastroFichaDeEvento(request.POST, request.FILES)

    if form.is_valid():
        novo_evento = form.save(commit=False)
        novo_evento.refeicoes = pegar_refeicoes(request.POST)
        novo_evento.empresa = ver_empresa_atividades(request.POST)
        novo_evento.pre_reserva = False

        try:
            form.save()
        except Exception as e:
            email_error(request.user.get_full_name(), e, __name__)
            messages.error(request, 'Houve um erro inesperado, por favor tente mais tarde')

            return redirect('ficha_de_evento')
        else:
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
            'atividades_ceu': atividades_ceu
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
        return JsonResponse(requests_ajax(request.POST))

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
        form = CadastroCliente(request.POST, instance=cliente)

        if form.is_valid():
            try:
                form.save()
            except Exception as e:
                email_error(request.user.get_full_name(), e, __name__)
                messages.error(request, 'Houve um erro inesperado, por favor tente mais tarde')
            else:
                cliente.responsavel_alteracao = request.user
                cliente.save()
                messages.success(request, 'Cliente atualizado com sucesso!')
                return redirect('lista_cliente')

        else:
            messages.warning(request, form.errors)
            return redirect('lista_cliente')

    form = CadastroCliente(request.POST)

    if form.is_valid():
        try:
            novo_cliente = form.save(commit=False)
            novo_cliente.responsavel_alteracao = request.user
            form.save()
        except Exception as e:
            email_error(request.user.get_full_name(), e, __name__)
            messages.error(request, 'Houve um erro inesperado, por favor tentar mais tarde!')

            if request.POST.get('id_responsavel') != '':
                responsavel = Responsavel.objects.get(id=request.POST.get('id_responsavel'))
                responsavel.delete()

            return redirect('lista_cliente')
        else:
            nova_relacao = RelacaoClienteResponsavel.objects.create(cliente=novo_cliente)
            nova_relacao.responsavel.add(request.POST.get('id_responsavel'))
            nova_relacao.save()
            messages.success(request, 'Cliente salvo com sucesso')
            return redirect('lista_cliente')
    else:
        try:
            responsavel_com_erro = Responsavel.objects.get(id=request.POST.get('id_responsavel'))
            responsavel_com_erro.delete()
            messages.warning(request, form.errors)
        except Responsavel.DoesNotExist:
            ...
        finally:
            return render(request, 'cadastro/lista-cliente.html', {'form': form,
                                                                   'clientes': clientes,
                                                                   'formResponsavel': form_responsavel})


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
            relacoes = RelacaoClienteResponsavel.objects.get(cliente=int(cliente))
        except RelacaoClienteResponsavel.DoesNotExist:
            responsaveis = []
        except Exception as e:
            email_error(request.user.get_full_name(), e, __name__)
            messages.error(request, 'Houve um erro inesperado, por favor tentar mais tarde!')
            return redirect('lista_responsaveis')
        else:
            for responsavel in relacoes.responsavel.all():
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
                try:
                    relacao_existente = RelacaoClienteResponsavel.objects.get(responsavel=responsavel.id)
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
