from time import sleep
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect

from ordemDeServico.models import CadastroOrdemDeServico
from .funcoes import is_ajax, analisar_tabela_atividade, verificar_tabela, indice_formulario
from .funcoes import juntar_professores, verificar_atividades, verificar_locacoes, entradas_e_saidas, somar_horas
from cadastro.models import RelatorioPublico
from ceu.models import Professores, Atividades, Locaveis
from .funcoesPublico import salvar_atividades, salvar_equipe


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

    ordem_colegio = OrdemDeServicoColegio()
    atividades, horas = indice_formulario(ordem_colegio, 'atividade_')
    locacoes, exclusao = indice_formulario(ordem_colegio, 'locacao_', n=2)
    entradas, saidas = entradas_e_saidas(ordem_colegio)
    professores = Professores.objects.all()
    range_j = range(1, 5)
    range_i = range(0, 3)
    range_i2 = range(3, 6)

    if request.method != 'POST':
        return render(request, 'cadastro/colegio.html', {'formulario': ordem_colegio, 'atividades': atividades,
                                                         'horas': horas, 'professores': professores,
                                                         'entradas': entradas, 'saidas': saidas,
                                                         'locacoes': locacoes, 'rangej': range_j, 'rangei': range_i,
                                                         'rangei2': range_i2})

    ordem_colegio = OrdemDeServicoColegio(request.POST)

    try:
        os = ordem_colegio.save(commit=False)
        os.tipo = Tipo.objects.get(tipo='Colégio')
        verificar_atividades(request.POST, os)
        verificar_locacoes(request.POST, os)
        somar_horas(request.POST, os)
        os.save()
    except:
        messages.error(request, 'Houve algum erro desconhecido, por favor, verifique se todos os campos estão'
                                'preenchidos corretamente!')
        ordem_colegio = OrdemDeServicoColegio(request.POST)
        return render(request, 'cadastro/colegio.html', {'formulario': ordem_colegio, 'atividades': atividades,
                                                         'horas': horas, 'professores': professores,
                                                         'entradas': entradas, 'saidas': saidas,
                                                         'locacoes': locacoes, 'rangej': range_j, 'rangei': range_i,
                                                         'rangei2': range_i2})
    else:
        messages.success(request, 'Relatório de atendimento salvo com sucesso!')
        return redirect('dashboard')


@login_required(login_url='login')
def empresa(request):

    ordem_empresa = OrdemDeServicoEmpresa()
    atividades, horas = indice_formulario(ordem_empresa, 'atividade_')
    locacoes, exclusao = indice_formulario(ordem_empresa, 'locacao_', n=3)
    entradas, saidas = entradas_e_saidas(ordem_empresa)
    professores = Professores.objects.all()
    range_j = range(1, 5)
    range_i = range(0, 3)
    range_i2 = range(3, 6)
    range_i3 = range(6, 9)

    if request.method != 'POST':
        return render(request, 'cadastro/empresa.html', {'formulario': ordem_empresa, 'atividades': atividades,
                                                         'horas': horas, 'professores': professores,
                                                         'locacoes': locacoes, 'entradas': entradas, 'saidas': saidas,
                                                         'rangej': range_j, 'rangei': range_i, 'rangei2': range_i2,
                                                         'rangei3': range_i3})

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

    if is_ajax(request) and request.method == 'POST':

        if request.POST.get('tipo') == 'Colégio':
            atividades_bd = Atividades.objects.all()
            atividades = {}

            for atividade in atividades_bd:
                atividades[atividade.id] = atividade.atividade

            return JsonResponse({'dados': atividades})

        if request.POST.get('tipo') == 'Empresa':
            locaveis_bd = Locaveis.objects.filter(locavel=True)
            locaveis = {}

            for estrutura in locaveis_bd:
                locaveis[estrutura.id] = estrutura.estrutura

            return JsonResponse(locaveis)

        if request.POST.get('atividade'):
            atividade_selecionada = Atividades.objects.get(id=request.POST.get('atividade'))
            limtacoes = []

            for limite in atividade_selecionada.limitacao.all():
                limtacoes.append(limite.limitacao)

            return JsonResponse({'limitacoes': limtacoes,
                                 'participantes_minimo': atividade_selecionada.numero_de_participantes_minimo,
                                 'participantes_maximo': atividade_selecionada.numero_de_participantes_maximo})

        if request.POST.get('local'):
            local_selecionado = Locaveis.objects.get(id=request.POST.get('local'))

            return JsonResponse({'lotacao': local_selecionado.lotacao})

    if request.method != 'POST':
        return render(request, 'cadastro/ordem_de_servico.html', {'form': form})
