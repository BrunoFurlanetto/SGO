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
    CadastroInfoAdicionais, CadastroResumoFinanceiro, CadastroCodigoApp, FichaDeEvento
from .funcoes import is_ajax, requests_ajax, pegar_refeicoes
from cadastro.models import RelatorioPublico, RelatorioColegio, RelatorioEmpresa
from ceu.models import Professores, Atividades, Locaveis
from .funcoesColegio import pegar_colegios_no_ceu, pegar_informacoes_cliente, pegar_empresas_no_ceu, \
    salvar_atividades_colegio, salvar_equipe_colegio
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
    print(relatorio_publico.errors)
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

        try:
            relatorio_colegio.save()
        except:
            messages.error(request, 'Houve um erro insperado, por favor tente novamente mais tarde!')
            relatorio_colegio = RelatorioColegio()
            return render(request, 'cadastro/colegio.html', {'formulario': relatorio_colegio,
                                                             'colegios': colegios_no_ceu,
                                                             'professores': professores})
        else:
            ordem.relatorio_ceu_entregue = True
            ordem.save()
            messages.success(request, 'Relatório de atendimento salvo com sucesso!')
            return redirect('dashboard')

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

    ordem_empresa = OrdemDeServicoEmpresa(request.POST)

    os = ordem_empresa.save(commit=False)
    os.tipo = Tipo.objects.get(tipo='Empresa')
    verificar_locacoes(request.POST, os)
    verificar_atividades(request.POST, os)
    somar_horas(request.POST, os)
    try:
        os.save()
    except:
        messages.error(request, 'Houve um erro inesperado, por favor, verifique se todos os campos estão preenchidos'
                                ' corretamente!')
        ordem_empresa = OrdemDeServicoEmpresa(request.POST)
        return render(request, 'cadastro/empresa.html', {'formulario': ordem_empresa, 'atividades': atividades,
                                                         'horas': horas, 'professores': professores,
                                                         'locacoes': locacoes, 'entradas': entradas, 'saidas': saidas,
                                                         'rangej': range_j, 'rangei': range_i, 'rangei2': range_i2,
                                                         'rangei3': range_i3})
    else:
        messages.success(request, 'Relatório de atendimento salvo com sucesso!')
        return redirect('dashboard')


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
    print(form.errors)
    ordem_de_servico = form.save(commit=False)


    try:
        salvar_atividades_ceu(request.POST, ordem_de_servico)
        check_in_and_check_out_atividade(ordem_de_servico)
        salvar_locacoes_ceu(request.POST, ordem_de_servico)
        form.save()
    except:
        messages.error(request, 'Houve um erro inesperado ao salvar a ficha do evento, por favor tente mais tarde,'
                                'ou entre em contato com o desenvolvedor.')
        return redirect('dashboardPeraltas')
    else:

        if ordem_de_servico.tipo == 'Empresa':
            messages.success(request, f'Ficha do evento da empresa {ordem_de_servico.instituicao} salva com sucesso')
        else:
            messages.success(request, f'Ficha do evento do colégio {ordem_de_servico.instituicao} salva com sucesso')

        return redirect('dashboardPeraltas')


@login_required(login_url='login')
def fichaDeEvento(request):
    form = CadastroFichaDeEvento()

    # send_mail('TESTE', 'Mensagem de Teste',
    #           'no-reply@fundaceoceu.com',
    #           ['bruno.furlanetto@hotmail.com'],
    #           fail_silently=False)

    if request.method != 'POST':
        form_adicionais = CadastroInfoAdicionais()
        form_financeiro = CadastroResumoFinanceiro()
        form_app = CadastroCodigoApp()

        if request.user in User.objects.filter(groups__name='CEU'):
            grupo_usuario = 'CEU'
        else:
            grupo_usuario = 'Peraltas'

        return render(request, 'cadastro/ficha-de-evento.html', {'form': form,
                                                                 'formAdicionais': form_adicionais,
                                                                 'formFinanceiro': form_financeiro,
                                                                 'formApp': form_app,
                                                                 'grupo_usuario': grupo_usuario})

    if is_ajax(request):
        return JsonResponse(requests_ajax(request.POST))

    form = CadastroFichaDeEvento(request.POST)
    novo_evento = form.save(commit=False)
    print(novo_evento.check_in)
    novo_evento.refeicoes = pegar_refeicoes(request.POST)

    try:
        form.save()
    except:
        messages.error(request, 'Houve um erro inesperado, por favor tente mais tarde')
        return redirect('ficha_de_evento')
    else:
        messages.success(request, 'Ficha de evento salva com sucesso')
        return redirect('ficha_de_evento')


@login_required(login_url='login')
def listaCliente(request):
    form = CadastroCliente()
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
            messages.add_message(request, messages.ERROR, 'Campo busca não pode ficar vazio')
            return redirect('lista_cliente')

        clientes = ClienteColegio.objects.filter(cnpj=termo)

        paginacao = Paginator(clientes, 5)
        pagina = request.GET.get('page')
        clientes = paginacao.get_page(pagina)

        return render(request, 'cadastro/lista-cliente.html', {'clientes': clientes,
                                                               'form': form})

    if request.method != 'POST':
        return render(request, 'cadastro/lista-cliente.html', {'form': form,
                                                               'clientes': clientes})

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
    paginacao = Paginator(responsaveis, 5)
    pagina = request.GET.get('page')
    responsaveis = paginacao.get_page(pagina)

    # ---------------------------------------------
    if request.GET.get('cliente'):
        cliente = request.GET.get('cliente')

        if cliente is None or not cliente:
            messages.add_message(request, messages.ERROR, 'Campo busca não pode ficar vazio')
            return redirect('lista_responsaveis')

        responsaveis = Responsavel.objects.filter(responsavel_por=cliente)
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
                messages.success(request, 'Dados do responsável atualizada com sucesso!')
                return redirect('lista_responsaveis')

        else:
            messages.warning(request, form.errors)
            return redirect('lista_responsaveis')

    form = CadastroResponsavel(request.POST)

    if form.is_valid():

        try:
            form.save()
        except:
            messages.error(request, 'Houve um erro inesperado, tente novemente mais tarde!')
            return redirect('lista_responsaveis')
        else:
            messages.success(request, 'Novo responsável salvo com sucesso!')
            return redirect('lista_responsaveis')

    else:
        messages.warning(request, form.errors)
        return redirect('lista_responsaveis')
