from datetime import datetime
from io import BytesIO
from time import sleep

import qrcode
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.urls import reverse
from unicodedata import normalize
from django.contrib import messages
from django.contrib.auth.models import User
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from cadastro.models import RelatorioDeAtendimentoPublicoCeu, RelatorioDeAtendimentoColegioCeu
from ceu.models import Atividades, Professores
from django.contrib.auth.models import Group
from dashboard.views import is_ajax
from fichaAvaliacao.funcoes import pegar_atividades_relatorio, pegar_professores_relatorio, pegar_dados_colegio, \
    pegar_dados_avaliador, salvar_avaliacoes_vendedor, salvar_avaliacoes_professores, salvar_avaliacoes_atividades
from fichaAvaliacao.models import FichaDeAvaliacaoForm, FichaDeAvaliacao
from ordemDeServico.models import OrdemDeServico
from peraltas.models import ClienteColegio
from projetoCEU.utils import verificar_grupo, email_error


@login_required(login_url='login')
def ver_fichaAvaliacao(request, id_ficha):
    atividades_bd = Atividades.objects.all()
    professores_bd = Professores.objects.all()
    ficha = FichaDeAvaliacao.objects.get(pk=id_ficha)
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

    return render(request, 'fichaAvaliacao/fichaAvaliacao.html', {
        'form': ficha_form,
        'avaliacao': ficha,
        'atividades': atividades_bd,
        'professores': professores_bd
    })


def cadastrar_nova_ficha(request, id_ordem):
    atividades_bd = Atividades.objects.all()
    professores_bd = Professores.objects.all()
    ordem = OrdemDeServico.objects.get(pk=id_ordem)
    formulario = FichaDeAvaliacaoForm(initial=FichaDeAvaliacao.dados_iniciais(ordem))
    formulario.dados_colegio = pegar_dados_colegio(id_ordem)
    formulario.dados_avaliador = pegar_dados_avaliador(id_ordem)
    formulario.atividades = pegar_atividades_relatorio(id_ordem)

    if request.method != 'POST':
        return render(request, 'fichaAvaliacao/fichaAvaliacao.html', {
            'form': formulario,
            'atividades': atividades_bd,
            'professores': professores_bd
        })


def salvar_ficha(request, id_ordem):
    formulario = FichaDeAvaliacaoForm(request.POST)
    professores = formulario.professores = pegar_professores_relatorio(id_ordem)

    if formulario.is_valid():
        nova_avaliacao = formulario.save(commit=False)
        salvar_avaliacoes_vendedor(request.POST, nova_avaliacao)
        salvar_avaliacoes_atividades(request.POST, nova_avaliacao)
        salvar_avaliacoes_professores(request.POST, nova_avaliacao, professores)
        formulario.save()
        try:
            pass
        except Exception as e:
            email_error(request.user.get_full_name(), e, __name__)
            messages.error(request, 'Houve um erro inesperado, por favor chame um professor!')
            return render(request, 'fichaAvaliacao/fichaAvaliacao.html', {
                'form': formulario,
            })
        else:
            ordem_colegio = OrdemDeServico.objects.get(pk=request.user.username)
            relatorio_colegio = RelatorioDeAtendimentoColegioCeu.objects.get(ordem=ordem_colegio)
            ordem_colegio.ficha_avaliacao = True
            relatorio_colegio.ficha_avaliacao = True
            ordem_colegio.save()
            relatorio_colegio.save()

            return redirect('agradecimentos')
    else:
        messages.warning(request, formulario.errors)
        return render(request, 'fichaAvaliacao/fichaAvaliacao.html', {
            'ver': ver_icons,
            'form': formulario
        })


def gerar_qrcode(request):
    link = request.GET.get('link', '').strip()

    if not link:
        return JsonResponse({'error': 'Nenhum link fornecido'}, status=400)

    # Criando QR Code com configurações personalizadas
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    base_url = request.build_absolute_uri('/')
    qr.add_data(f'{base_url}{link[1:]}')
    qr.make(fit=True)

    # Criando a imagem do QR Code
    img = qr.make_image(fill="black", back_color="white").convert("RGB")  # Conversão para Pillow

    buffer = BytesIO()
    img.save(buffer, "PNG")  # Agora aceita "PNG"
    buffer.seek(0)

    response = HttpResponse(buffer.getvalue(), content_type="image/png")
    response["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"

    return response


@login_required(login_url='login')
def agradecimentos(request):
    if not request.user.is_authenticated:
        return redirect('login')
    elif not User.objects.filter(pk=request.user.id, groups__name='Colégio'):
        return redirect('dashboard')

    if request.method != 'POST':
        ver_icons = User.objects.filter(pk=request.user.id, groups__name='Colégio').exists()
        grupos = verificar_grupo(request.user.groups.all())
        user = User.objects.get(pk=request.user.id)
        user.delete()
        return render(request, 'fichaAvaliacao/agradecimento.html', {'ver': ver_icons,
                                                                     'grupos': grupos})


@login_required(login_url='login')
def entregues(request):
    fichas = FichaDeAvaliacao.objects.order_by('-id').all()
    grupos = verificar_grupo(request.user.groups.all())

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
        return render(request, 'fichaAvaliacao/listaFichasEntregues.html', {'fichas': fichas,
                                                                            'grupos': grupos})
