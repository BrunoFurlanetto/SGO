from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render

from peraltas.models import PerfilsParticipantes, ProdutosPeraltas
from pre_orcamento.models import PreCadastroFormulario, CadastroPreOrcamento


@login_required(login_url='login')
def dashboard(request):
    return render(request, 'pre_orcamento/dashoboard.html')


@login_required(login_url='login')
def nova_previa(request):
    pre_cadastro = PreCadastroFormulario()
    previa = CadastroPreOrcamento()
    series = PerfilsParticipantes.objects.all().order_by('fase', 'ano')
    produtos_peraltas = ProdutosPeraltas.objects.all().exclude(brotas_eco=True)

    return render(request, 'pre_orcamento/nova_previa.html', {
        'pre_cadastro': pre_cadastro,
        'previa': previa,
        'series': series,
        'produtos_peraltas': produtos_peraltas,
    })


def validar_pacotes(request):
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
