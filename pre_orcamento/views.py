from itertools import chain

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render

from ceu.models import Atividades, TipoAtividadesCeu
from peraltas.models import PerfilsParticipantes, ProdutosPeraltas, AtividadesEco, TipoAtividadePeraltas
from pre_orcamento.models import PreCadastroFormulario, CadastroPreOrcamento
from pre_orcamento.utils import ranqueamento_atividades
from projetoCEU.utils import is_ajax


@login_required(login_url='login')
def dashboard(request):
    return render(request, 'pre_orcamento/dashoboard.html')


@login_required(login_url='login')
def nova_previa(request):
    pre_cadastro = PreCadastroFormulario()
    previa = CadastroPreOrcamento()
    series = PerfilsParticipantes.objects.all().order_by('fase', 'ano')
    produtos_peraltas = ProdutosPeraltas.objects.all().exclude(brotas_eco=True)
    temas_ceu = TipoAtividadesCeu.objects.all()
    temas_peraltas = TipoAtividadePeraltas.objects.all()

    return render(request, 'pre_orcamento/nova_previa.html', {
        'pre_cadastro': pre_cadastro,
        'previa': previa,
        'series': series,
        'produtos_peraltas': produtos_peraltas,
        'temas_ceu': temas_ceu,
        'temas_peraltas': temas_peraltas
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
        ids_serie = list(map(int, request.POST.getlist('serie_grupo[]')))
        ids_pacotes = list(map(int, request.POST.getlist('tipo_pacote[]')))
        ids_temas_ceu = list(map(int, [tema.replace('c_', '') for tema in request.POST.getlist('temas_interesse[]') if 'c_' in tema]))
        ids_temas_peraltas = list(map(int, [tema.replace('p_', '') for tema in request.POST.getlist('temas_interesse[]') if 'p_' in tema]))
        match_atividades_ceu = None

        match_atividades_eco = AtividadesEco.objects.filter(
            serie__in=ids_serie,
            # tipo_pacote__in=ids_pacotes  TODO: Retirar do comentário assim que conseguir essa relação,
            intencao_atividade=request.POST.get('intencao'),
            tipo_atividade__in=ids_temas_peraltas,
        ).distinct()
        print(match_atividades_eco)
        if request.POST.get('intencao') == 'estudo':
            match_atividades_ceu = Atividades.objects.filter(
                serie__in=ids_serie,
                tipo_pacote__in=ids_pacotes,
                tema_atividade__in=ids_temas_ceu,
            ).distinct()

        atividades_ranqueadas = ranqueamento_atividades(
            match_atividades_ceu,
            match_atividades_eco,
            ids_serie,
            ids_temas_ceu,
            ids_temas_peraltas,
            ids_pacotes
        )
        print(atividades_ranqueadas)
        return JsonResponse(atividades_ranqueadas)
