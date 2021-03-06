import json
import datetime

from itertools import chain
from time import sleep
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Q
from django.db.models.functions import Concat
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.core.mail import send_mail

from ordemDeServico.models import CadastroOrdemDeServico, OrdemDeServico
from peraltas.models import CadastroFichaDeEvento, CadastroCliente, ClienteColegio, CadastroResponsavel, Responsavel, \
    CadastroInfoAdicionais, CadastroCodigoApp, FichaDeEvento, RelacaoClienteResponsavel, Vendedor, PreReserva
from .funcoes import is_ajax, requests_ajax, pegar_refeicoes
from cadastro.models import RelatorioPublico, RelatorioColegio, RelatorioEmpresa
from ceu.models import Professores, Atividades, Locaveis
from .funcoesColegio import pegar_colegios_no_ceu, pegar_informacoes_cliente, pegar_empresas_no_ceu, \
    salvar_atividades_colegio, salvar_equipe_colegio, salvar_locacoes_empresa, criar_usuario_colegio
from .funcoesFichaEvento import salvar_atividades_ceu, check_in_and_check_out_atividade, salvar_locacoes_ceu
from .funcoesPublico import salvar_atividades, salvar_equipe
from django.core.paginator import Paginator


@login_required(login_url='login')
def publico(request):
    relatorio_publico = RelatorioPublico()
    atividades = Atividades.objects.filter(publico=True)
    professores = Professores.objects.all()
    range_i = range(1, 6)
    range_j = range(1, 5)

    if request.method != 'POST':
        return render(request, 'cadastro/publico.html', {'formulario': relatorio_publico, 'rangei': range_i,
                                                         'rangej': range_j, 'atividades': atividades,
                                                         'professores': professores})

    relatorio_publico = RelatorioPublico(request.POST)
    relatorio = relatorio_publico.save(commit=False)
    salvar_equipe(request.POST, relatorio)
    salvar_atividades(request.POST, relatorio)

    try:
        relatorio.save()
    except:
        messages.error(request, 'Houve um erro inesperado, por favor tente mais tarde')
        return render(request, 'cadastro/publico.html', {'formulario': relatorio_publico, 'rangei': range_i,
                                                         'rangej': range_j, 'atividades': atividades,
                                                         'professores': professores})
    else:
        messages.success(request, 'Relat??rio de atendimento ao p??blico salva com sucesso')
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

        try:
            novo_colegio = relatorio_colegio.save()
        except:
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
        except:
            messages.error(request, 'Houve um erro inesperado, por favor, tente mais tarde')
            relatorio_empresa = RelatorioEmpresa()
            return render(request, 'cadastro/empresa.html', {'formulario': relatorio_empresa,
                                                             'professores': professores,
                                                             'empresas': empresas})
        else:
            ordem.relatorio_ceu_entregue = True
            ordem.save()
            messages.success(request, 'Relat??rio de atendimento salvo com sucesso!')
            return redirect('dashboard')
    else:
        messages.warning(request, relatorio_empresa.errors)
        return render(request, 'cadastro/empresa.html', {'formulario': relatorio_empresa,
                                                         'professores': professores,
                                                         'empresas': empresas})


@login_required(login_url='login')
def ordemDeServico(request):
    form = CadastroOrdemDeServico()
    fichas_de_evento = FichaDeEvento.objects.filter(os=False)

    if request.method != 'POST':
        return render(request, 'cadastro/ordem_de_servico.html', {'form': form,
                                                                  'fichas': fichas_de_evento})

    if is_ajax(request):
        return JsonResponse(requests_ajax(request.POST))

    form = CadastroOrdemDeServico(request.POST, request.FILES)
    ordem_de_servico = form.save(commit=False)
    ficha = FichaDeEvento.objects.get(id=int(request.POST.get('ficha_de_evento')))

    try:
        salvar_atividades_ceu(request.POST, ordem_de_servico)
        check_in_and_check_out_atividade(ordem_de_servico)
        salvar_locacoes_ceu(request.POST, ordem_de_servico)
        
        if ficha.escala:
            form.escala = True

        form.save()
    except:
        messages.error(request, 'Houve um erro inesperado ao salvar a ficha do evento, por favor tente mais tarde,'
                                'ou entre em contato com o desenvolvedor.')
        return redirect('dashboardPeraltas')
    else:
        ficha.os = True
        ficha.save()

        if ordem_de_servico.tipo == 'Empresa':
            messages.success(request, f'Ordem de servi??o da empresa {ordem_de_servico.instituicao} salva com sucesso')
        else:
            messages.success(request, f'Ordem de servi??o do col??gio {ordem_de_servico.instituicao} salva com sucesso')

        return redirect('dashboardPeraltas')


@login_required(login_url='login')
def fichaDeEvento(request, id_cliente=None):
    form = CadastroFichaDeEvento()
    form_adicionais = CadastroInfoAdicionais()
    form_app = CadastroCodigoApp()
    atividades_ceu = Atividades.objects.all()

    if id_cliente:
        pre_reserva_cliente = ClienteColegio.objects.get(id=int(id_cliente))
        pre_reserva = PreReserva.objects.get(cliente=pre_reserva_cliente)
        dados_pre_reserva = {
            'cliente_id': pre_reserva_cliente.id,
            'cliente_nome_fantasia': pre_reserva_cliente.nome_fantasia,
            'check_in': pre_reserva.check_in.strftime('%Y-%m-%dT%H:%M'),
            'check_out': pre_reserva.check_out.strftime('%Y-%m-%dT%H:%M'),
            'qtd': pre_reserva.participantes,
            'vendedor': pre_reserva.vendedor.usuario.get_full_name(),
            'observacoes': pre_reserva.observacoes,
        }
        form.id_vendedora = pre_reserva.vendedor.id
    else:
        dados_pre_reserva = None
        vendedora = Vendedor.objects.get(usuario=request.user)
        form.id_vendedora = vendedora.id

    if request.user in User.objects.filter(groups__name='CEU'):
        grupo_usuario = 'CEU'
    else:
        grupo_usuario = 'Peraltas'

    # send_mail('TESTE', 'Mensagem de Teste',
    #           'no-reply@fundaceoceu.com',
    #           ['bruno.furlanetto@hotmail.com'],
    #           fail_silently=False)

    if request.method != 'POST':
        return render(request, 'cadastro/ficha-de-evento.html', {'form': form,
                                                                 'formAdicionais': form_adicionais,
                                                                 'formApp': form_app,
                                                                 'dados_pre_reserva': dados_pre_reserva,
                                                                 'grupo_usuario': grupo_usuario,
                                                                 'atividades_ceu': atividades_ceu})

    if is_ajax(request):

        if request.FILES != {}:
            return JsonResponse(requests_ajax(request.POST, request.FILES))
        else:
            return JsonResponse(requests_ajax(request.POST))

    form = CadastroFichaDeEvento(request.POST)

    if form.is_valid():
        novo_evento = form.save(commit=False)
        novo_evento.refeicoes = pegar_refeicoes(request.POST)

        try:
            form.save()
        except:
            messages.error(request, 'Houve um erro inesperado, por favor tente mais tarde')
            return redirect('ficha_de_evento')
        else:
            try:
                pre_reserva = PreReserva.objects.get(cliente=novo_evento.cliente, ficha_de_evento=False)
            except PreReserva.DoeNotExists:
                ...
            else:
                pre_reserva.agendado = True
                pre_reserva.ficha_evento = True
                pre_reserva.save()

            messages.success(request, 'Ficha de evento salva com sucesso')
            return redirect('dashboard')
    else:
        messages.warning(request, form.errors)
        return render(request, 'cadastro/ficha-de-evento.html', {'form': form,
                                                                 'formAdicionais': form_adicionais,
                                                                 'formApp': form_app,
                                                                 'grupo_usuario': grupo_usuario,
                                                                 'atividades_ceu': atividades_ceu})


@login_required(login_url='login')
def listaCliente(request):
    form = CadastroCliente()
    form_responsavel = CadastroResponsavel()
    clientes = ClienteColegio.objects.all()
    paginacao = Paginator(clientes, 5)
    pagina = request.GET.get('page')
    clientes = paginacao.get_page(pagina)

    if is_ajax(request):
        return JsonResponse(requests_ajax(request.POST))

    # ---------------------------------------------
    if request.GET.get('termo'):
        termo = request.GET.get('termo')

        if termo is None or not termo:
            messages.add_message(request, messages.ERROR, 'Campo busca n??o pode ficar vazio')
            return redirect('lista_cliente')

        clientes = ClienteColegio.objects.filter(cnpj=termo)

        paginacao = Paginator(clientes, 5)
        pagina = request.GET.get('page')
        clientes = paginacao.get_page(pagina)

        return render(request, 'cadastro/lista-cliente.html', {'clientes': clientes,
                                                               'form': form})

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
            except:
                messages.error(request, 'Houve um erro inesperado, por favor tente mais tarde')
            else:
                messages.success(request, 'Cliente atualizado com sucesso!')
                return redirect('lista_cliente')

        else:
            messages.warning(request, form.errors)
            return redirect('lista_cliente')

    form = CadastroCliente(request.POST)

    if form.is_valid():

        try:
            form.save()
        except:
            messages.error(request, 'Houve um erro inesperado, por favor tentar mais tarde!')
            return redirect('lista_cliente')
        else:
            messages.success(request, 'Cliente salvo com sucesso')
            return redirect('lista_cliente')

    else:
        messages.warning(request, form.errors)
        return redirect('lista_cliente')


@login_required(login_url='login')
def listaResponsaveis(request):
    form = CadastroResponsavel()
    clientes = ClienteColegio.objects.all()
    responsaveis = Responsavel.objects.all()

    for responsavel in responsaveis:
        print(responsavel)
        relacao = RelacaoClienteResponsavel.objects.get(responsavel=responsavel.id)
        responsavel.responsavel_por = relacao.cliente.nome_fantasia
        print(relacao, responsavel.responsavel_por)

    paginacao = Paginator(responsaveis, 5)
    pagina = request.GET.get('page')
    responsaveis = paginacao.get_page(pagina)

    # ---------------------------------------------
    if request.GET.get('cliente'):
        cliente = request.GET.get('cliente')

        if cliente is None or not cliente:
            messages.add_message(request, messages.ERROR, 'Campo busca n??o pode ficar vazio')
            return redirect('lista_responsaveis')

        responsaveis = list(chain())

        try:
            relacoes = RelacaoClienteResponsavel.objects.get(cliente=int(cliente))
        except RelacaoClienteResponsavel.DoesNotExist:
            responsaveis = []
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

        form = CadastroResponsavel(request.POST, instance=responsavel)

        if form.is_valid():

            try:
                form.save()
            except:
                messages.error(request, 'Houve um erro inesperado, tente novemente mais tarde!')
                return redirect('lista_responsaveis')
            else:
                messages.success(request, 'Dados do respons??vel atualizada com sucesso!')
                return redirect('lista_responsaveis')

        else:
            messages.warning(request, form.errors)
            return redirect('lista_responsaveis')

    form = CadastroResponsavel(request.POST)

    if form.is_valid():

        try:
            novo_responsavel = form.save()
        except:
            messages.error(request, 'Houve um erro inesperado, tente novemente mais tarde!')
            return redirect('lista_responsaveis')
        else:

            try:
                relacao = RelacaoClienteResponsavel.objects.get(cliente=int(request.POST.get('responsavel_por')))
            except RelacaoClienteResponsavel.DoesNotExist:
                cliente = ClienteColegio.objects.get(id=int(request.POST.get('responsavel_por')))
                RelacaoClienteResponsavel(cliente=cliente).save()
                relacao = RelacaoClienteResponsavel.objects.get(cliente=int(request.POST.get('responsavel_por')))
            finally:
                relacao.responsavel.add(novo_responsavel.id)

            messages.success(request, 'Novo respons??vel salvo com sucesso!')
            return redirect('lista_responsaveis')

    else:
        messages.warning(request, form.errors)
        return redirect('lista_responsaveis')
