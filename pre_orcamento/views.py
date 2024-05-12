from itertools import chain

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render, redirect

from ceu.models import Atividades
from peraltas.models import PerfilsParticipantes, ProdutosPeraltas, AtividadesEco, Disciplinas, IntencaoAtividade
from pre_orcamento.models import PreCadastroFormulario, CadastroPreOrcamento, PreCadastro, PreOrcamento
from pre_orcamento.utils import ranqueamento_atividades
from projetoCEU.utils import is_ajax


@login_required(login_url='login')
def dashboard(request):
    previas_colaborador = PreOrcamento.objects.filter(colaborador=request.user.id).order_by('-validade')
    previas_aberta = previas_colaborador.filter(status__status__icontains='aberto')
    clientes_colaborador = [previa.cliente for previa in previas_aberta]

    return render(request, 'pre_orcamento/dashoboard.html', {
        'clientes_colaborador': set(clientes_colaborador),
        'previas_aberta': previas_aberta,
    })


@login_required(login_url='login')
def nova_previa(request):
    pre_cadastro = PreCadastroFormulario()
    previa = CadastroPreOrcamento()
    series = PerfilsParticipantes.objects.all().order_by('fase', 'ano')
    produtos_peraltas = ProdutosPeraltas.objects.all().exclude(brotas_eco=True)
    disciplinas = Disciplinas.objects.all()
    intencoes = IntencaoAtividade.objects.all()

    return render(request, 'pre_orcamento/nova_previa.html', {
        'pre_cadastro': pre_cadastro,
        'previa': previa,
        'series': series,
        'produtos_peraltas': produtos_peraltas,
        'disciplinas': disciplinas,
        'intencoes': intencoes,
    })


def validar_pacotes(request):
    if is_ajax(request):
        n_dias = int(request.POST.get('dias')) - 1
        produtos_base = ProdutosPeraltas.objects.filter(n_dias=n_dias).exclude(brotas_eco=True)
        produtos_dia = [produto.id for produto in produtos_base]
        produtos_dia.append(ProdutosPeraltas.objects.get(produto__icontains='all party').id)

        if n_dias == 0:
            produtos_dia.append(ProdutosPeraltas.objects.get(produto__icontains='ceu').id)
            produtos_dia.append(ProdutosPeraltas.objects.get(produto__icontains='visita técnica').id)
        elif n_dias >= 2:
            produtos_dia.append(ProdutosPeraltas.objects.get(produto__icontains='ac 3 dias ou mais').id)

        return JsonResponse({'id_pacotes_validos': produtos_dia})


def sugerir_atividades(request):
    if is_ajax(request):
        print(request.POST)
        ids_serie = list(map(int, request.POST.getlist('serie_grupo[]')))
        ids_pacotes = list(map(int, request.POST.getlist('tipo_pacote[]')))
        ids_temas_interesse = list(map(int, request.POST.getlist('temas_interesse[]')))
        match_atividades_ceu = None

        match_atividades_eco = AtividadesEco.objects.filter(
            serie__in=ids_serie,
            tipo_pacote__in=ids_pacotes,
            intencao_atividade=int(request.POST.get('intencao')),
            disciplinas__in=ids_temas_interesse,
        ).exclude(nome_atividade_eco__icontains='inglês').distinct()

        match_atividades_ceu = Atividades.objects.filter(
            serie__in=ids_serie,
            tipo_pacote__in=ids_pacotes,
            intencao_atividade=int(request.POST.get('intencao')),
            disciplinas__in=ids_temas_interesse,
            ).exclude(atividade__icontains='inglês').distinct()

        atividades_ranqueadas = ranqueamento_atividades(
            match_atividades_ceu,
            match_atividades_eco,
            ids_serie,
            ids_temas_interesse,
            ids_pacotes
        )
        print(atividades_ranqueadas)
        return JsonResponse(atividades_ranqueadas)


def salvar_previa(request):
    cliente, _ = PreCadastro.objects.get_or_create(cnpj=request.POST.get('cnpj'), defaults={
        'nome_colegio': request.POST.get('nome_colegio'),
        'cnpj': request.POST.get('cnpj'),
        'nome_responsavel': request.POST.get('nome_responsavel'),
        'telefone_responsavel': request.POST.get('telefone_responsavel'),
    })

    dados_cadastro = PreOrcamento.tratar_cadastro(request.POST, cliente, request.user)
    previa = CadastroPreOrcamento(dados_cadastro)

    try:
        previa.save()
    except Exception as e:
        messages.error(request, f'Houve um erro durante o salvamento da prévia ({e}). Por favor tente novamente mais tarde.')

        return redirect('dashboard_pre_orcamento')
    else:
        messages.success(request, 'Prévia salva com sucesso!')

        return redirect('dashboard_pre_orcamento')
