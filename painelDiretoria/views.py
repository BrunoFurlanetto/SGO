from django.contrib.auth.decorators import login_required, permission_required
from django.http import JsonResponse
from django.shortcuts import render

from peraltas.models import Eventos, ProdutosPeraltas
from projetoCEU.utils import is_ajax


@login_required
@permission_required('painelDiretoria.view_painelDiretoria', login_url='dashboard')
def index(request):
    return render(request, 'painelDiretoria/index.html', {
        'relatorio_eventos': Eventos.preparar_relatorio_mes_mes(),
        'relatorio_produtos': Eventos.preparar_relatorio_produtos(),
        'produtos_peraltas': ProdutosPeraltas.objects.all()
    })


def infos_clientes_mes_estagios(request):
    if is_ajax(request) and request.method == 'GET':
        mes, ano = request.GET.get('mes_ano').split('/')
        estagio = request.GET.get('estagio')

        return JsonResponse(Eventos.preparar_relatorio_clientes_mes_estagios(estagio, mes, ano))
