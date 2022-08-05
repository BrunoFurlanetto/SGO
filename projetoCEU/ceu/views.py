from itertools import chain

from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from django.http import FileResponse, JsonResponse

from ceu.funcoes import criar_pdf_relatorio, pegar_dados_evento
from dashboard.funcoes import is_ajax
from ordemDeServico.models import OrdemDeServico
from projetoCEU.utils import verificar_grupo


@login_required(login_url='login')
def resumo_financeiro_ceu(request):
    if request.method != 'POST':
        return render(request, 'ceu/resumo_financeiro_ceu.html')


@login_required(login_url='login')
def detector_de_bombas(request):
    grupos = verificar_grupo(request.user.groups.all())
    ordens_locacoes = OrdemDeServico.objects.filter(relatorio_ceu_entregue=False).exclude(locacao_ceu=None)
    ordens_atividades = OrdemDeServico.objects.filter(relatorio_ceu_entregue=False).exclude(atividades_ceu=None)
    ordens = list(chain(ordens_locacoes, ordens_atividades))

    if is_ajax(request):
        return JsonResponse(pegar_dados_evento(int(request.POST.get('id_cliente')),
                                               ordens))

    if request.method != 'POST':
        return render(request, 'ceu/detector_de_bombas.html', {'grupos': grupos,
                                                               'eventos': ordens})
