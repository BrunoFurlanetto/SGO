from django.contrib.auth.decorators import login_required, permission_required, user_passes_test
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.views.decorators.http import require_GET

from peraltas.models import Eventos, ProdutosPeraltas
from projetoCEU.utils import is_ajax


@login_required
@permission_required('peraltas.view_eventos', raise_exception=True)
def index(request):
    return render(request, 'painelDiretoria/index.html', {
        'relatorio_eventos': Eventos.preparar_relatorio_mes_mes(),
        'relatorio_produtos': Eventos.preparar_relatorio_produtos(),
        'produtos_peraltas': ProdutosPeraltas.objects.all(),
        'campos_cadastro_eventos': Eventos.campos_cadastro_eventos()
    })


@login_required
@require_GET
def infos_clientes_mes_estagios(request):
    if is_ajax(request):
        mes, ano = request.GET.get('mes_ano').split('/')
        estagio = request.GET.get('estagio')
        campos = request.GET.getlist('campos[]')

        return JsonResponse(Eventos.preparar_relatorio_clientes_mes_estagios(estagio, mes, ano, campos))
    else:
        return redirect('dashboard')


@login_required
@require_GET
def infos_produtos_estagios(request):
    if is_ajax(request):
        mes = Eventos.numero_mes(request.GET.get('mes_ano').split('/')[0])
        ano = request.GET.get('mes_ano').split('/')[1]
        dados_produtos_trabalhados = {}

        dados_produto = Eventos.preparar_relatorio_produtos(
            pesquisar_seis_meses=False,
            mes_check_in=mes,
            ano_check_in=ano
        )

        dados_produtos_trabalhados['produtos'] = dados_produto['produtos']
        soma_dos_produtos = [0] * len(list(dados_produto['relatorio_mes_mes'][0]['estagios'].values())[0])

        for estagio in dados_produto['relatorio_mes_mes'][0]['estagios'].values():
            for i, valor in enumerate(estagio):
                soma_dos_produtos[i] += valor

        dados_produtos_trabalhados['valores'] = soma_dos_produtos
        dados_estagio = Eventos.peparar_relatorio_estagio(mes, ano)

        return JsonResponse({'dados_produto': dados_produtos_trabalhados, 'dados_estagio': dados_estagio})
    else:
        return redirect('dashboard')
