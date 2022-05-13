from datetime import datetime
from time import sleep

from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from unicodedata import normalize
from django.contrib import messages
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from cadastro.models import RelatorioDeAtendimentoPublicoCeu
from ceu.models import Atividades, Professores
from django.contrib.auth.models import Group
from dashboard.views import is_ajax
from fichaAvaliacao.funcoes import pegar_atividades_relatorio, pegar_professores_relatorio, pegar_dados_colegio, \
    pegar_dados_avaliador, salvar_avaliacoes_vendedor, salvar_avaliacoes_professores, salvar_avaliacoes_atividades
from fichaAvaliacao.models import FichaDeAvaliacaoForm, FichaDeAvaliacao


@login_required(login_url='login')
def fichaAvaliacao(request):
    if not User.objects.filter(pk=request.user.id, groups__name='Colégio'):
        return redirect('dashboard')

    formulario = FichaDeAvaliacaoForm()
    formulario.dados_colegio = pegar_dados_colegio(request.user.last_name)
    formulario.dados_avaliador = pegar_dados_avaliador(request.user.last_name)
    formulario.atividades = pegar_atividades_relatorio(request.user.last_name)
    formulario.professores = pegar_professores_relatorio(request.user.last_name)
    ver_icons = User.objects.filter(pk=request.user.id, groups__name='Colégio').exists()

    if request.method != 'POST':
        return render(request, 'fichaAvaliacao/fichaAvaliacao.html', {'ver': ver_icons, 'form': formulario})

    formulario = FichaDeAvaliacaoForm(request.POST)

    if formulario.is_valid():
        try:
            nova_avaliacao = formulario.save(commit=False)
            salvar_avaliacoes_vendedor(request.POST, nova_avaliacao)
            salvar_avaliacoes_atividades(request.POST, nova_avaliacao)
            salvar_avaliacoes_professores(request.POST, nova_avaliacao)
            formulario.save()
        except:
            messages.error(request, 'Houve um erro inesperado, por favor chame um professor!')
            return render(request, 'fichaAvaliacao/fichaAvaliacao.html', {'ver': ver_icons, 'form': formulario})
        else:
            return redirect('agradecimentos')
    else:
        messages.warning(request, formulario.errors)
        return render(request, 'fichaAvaliacao/fichaAvaliacao.html', {'ver': ver_icons, 'form': formulario})


@login_required(login_url='login')
def agradecimentos(request):
    if not request.user.is_authenticated:
        return redirect('login')
    elif not User.objects.filter(pk=request.user.id, groups__name='Colégio'):
        return redirect('dashboard')

    if request.method != 'POST':
        ver_icons = User.objects.filter(pk=request.user.id, groups__name='Colégio').exists()
        user = User.objects.get(pk=request.user.id)
        user.delete()
        return render(request, 'fichaAvaliacao/agradecimento.html', {'ver': ver_icons})


@login_required(login_url='login')
def entregues(request):
    fichas = FichaDeAvaliacao.objects.all().order_by('data_preenchimento')

    paginacao = Paginator(fichas, 10)
    pagina = request.GET.get('page')
    fichas = paginacao.get_page(pagina)

    if request.GET.get('colegio'):
        colegio = request.GET.get('colegio')

        if colegio is None or not colegio:
            messages.add_message(request, messages.ERROR, 'Campo busca não pode ficar vazio')
            return redirect('lista_responsaveis')

        fichas = FichaDeAvaliacao.objects.filter(instituicao__nome_fantasia__icontains=colegio)
        paginacao = Paginator(fichas, 10)
        pagina = request.GET.get('page')
        fichas = paginacao.get_page(pagina)

        return render(request, 'fichaAvaliacao/listaFichasEntregues.html', {'fichas': fichas})

    if request.method != 'POST':
        return render(request, 'fichaAvaliacao/listaFichasEntregues.html', {'fichas': fichas})


@login_required(login_url='login')
def verFicha(request, id_fichaDeAvaliacao):
    ficha = FichaDeAvaliacao.objects.get(id=int(id_fichaDeAvaliacao))
    ficha_form = FichaDeAvaliacaoForm(instance=ficha)
    atividades = []
    professores = []

    ficha_form.nota_agilidade_vendedor = ficha.avaliacao_vendedor['agilidade']
    ficha_form.nota_clareza_vendedor = ficha.avaliacao_vendedor['clareza_ideias']

    for i in range(1, len(ficha.avaliacoes_atividades) + 1):
        atividades.append(ficha.avaliacoes_atividades[f'atividade_{i}'])

    for i in range(1, len(ficha.avaliacoes_professores) + 1):
        professores.append(ficha.avaliacoes_professores[f'professor_{i}'])

    ficha_form.atividades = atividades
    ficha_form.professores = professores
    print(ficha_form.professores)

    return render(request, 'fichaAvaliacao/verFichaAvaliacao.html', {'form': ficha_form})
