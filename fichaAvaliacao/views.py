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
    professores = formulario.professores = pegar_professores_relatorio(id_ordem)
    formulario.dados_colegio = pegar_dados_colegio(id_ordem)
    formulario.dados_avaliador = pegar_dados_avaliador(id_ordem)
    formulario.atividades = pegar_atividades_relatorio(id_ordem)

    if request.method != 'POST':
        return render(request, 'fichaAvaliacao/fichaAvaliacao.html', {
            'form': formulario,
            'atividades': atividades_bd,
            'professores': professores_bd
        })


def salvar_ficha(request):
    formulario = FichaDeAvaliacaoForm(request.POST)

    if formulario.is_valid():
        nova_avaliacao = formulario.save(commit=False)
        professores = formulario.professores = pegar_professores_relatorio(int(request.POST.get('ordem_de_servico')))
        salvar_avaliacoes_vendedor(request.POST, nova_avaliacao)
        salvar_avaliacoes_atividades(request.POST, nova_avaliacao)
        salvar_avaliacoes_professores(request.POST, nova_avaliacao, professores)

        try:
            formulario.save()
        except Exception as e:
            email_error(request.user.get_full_name(), e, __name__)
            messages.error(request, 'Houve um erro inesperado, por favor chame um professor!')
            return render(request, 'fichaAvaliacao/fichaAvaliacao.html', {
                'form': formulario,
            })
        else:
            ordem_colegio = OrdemDeServico.objects.get(pk=request.POST.get('ordem_de_servico'))
            relatorio_colegio = RelatorioDeAtendimentoColegioCeu.objects.get(ordem=ordem_colegio)
            ordem_colegio.ficha_avaliacao = True
            relatorio_colegio.ficha_avaliacao = True
            ordem_colegio.save()
            relatorio_colegio.save()

            return redirect('agradecimentos')
    else:
        messages.warning(request, formulario.errors)
        return render(request, 'fichaAvaliacao/fichaAvaliacao.html', {
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
    eventos_sem_avaliacao = OrdemDeServico.objects.filter(nao_respondeu_avaliacao_ceu=True).order_by('-id')
    grupos = verificar_grupo(request.user.groups.all())

    # Paginação para fichas
    paginacao_fichas = Paginator(fichas, 10)
    pagina_fichas = request.GET.get('page_fichas')
    fichas_paginadas = paginacao_fichas.get_page(pagina_fichas)

    # Paginação para eventos sem avaliação
    paginacao_eventos = Paginator(eventos_sem_avaliacao, 10)
    pagina_eventos = request.GET.get('page_eventos')
    eventos_paginados = paginacao_eventos.get_page(pagina_eventos)

    if request.GET.get('colegio'):
        colegio = request.GET.get('colegio')

        if colegio is None or not colegio:
            messages.add_message(request, messages.ERROR, 'Campo busca não pode ficar vazio')
            return redirect('lista_responsaveis')

        fichas = FichaDeAvaliacao.objects.filter(instituicao__nome_fantasia__icontains=colegio)
        paginacao_fichas = Paginator(fichas, 10)
        pagina_fichas = request.GET.get('page_fichas')
        fichas_paginadas = paginacao_fichas.get_page(pagina_fichas)

        return render(request, 'fichaAvaliacao/listaFichasEntregues.html', {
            'fichas': fichas_paginadas,
            'eventos_sem_avaliacao': eventos_paginados,
            'grupos': grupos
        })

    if request.method != 'POST':
        return render(request, 'fichaAvaliacao/listaFichasEntregues.html', {
            'fichas': fichas_paginadas,
            'eventos_sem_avaliacao': eventos_paginados,
            'grupos': grupos
        })


@login_required(login_url='login')
def salvar_nao_avaliacao(request):
    ordem = OrdemDeServico.objects.get(pk=int(request.POST.get('id_ordem_avaliacao_nao_respondida')))

    try:
        ordem.nao_respondeu_avaliacao_ceu = True
        ordem.motivo_nao_responder_ceu = request.POST.get('motivo_nao_avaliacao')
        ordem.ficha_avaliacao = True
        ordem.save()
    except Exception as e:
        messages.error(request, f'Houve um erro inesperado ao salvar ({e}). Por favor, tente novamente mais tarde!')
        return redirect('dashboardCeu')

    messages.success(request, f'Motivo de não avaliação do cliente salva com sucesso!')
    return redirect('dashboardCeu')
