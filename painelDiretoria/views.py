from datetime import datetime, timedelta

from django.contrib.auth.decorators import login_required, permission_required, user_passes_test
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.views.decorators.http import require_GET

from painelDiretoria.models import Metas
from peraltas.models import Eventos, ProdutosPeraltas, EscalaAcampamento
from projetoCEU.utils import is_ajax


@login_required
@permission_required('peraltas.ver_relatorios_eventos', raise_exception=True)
def index(request):
    return render(request, 'painelDiretoria/index.html', {
        'relatorio_eventos': Eventos.preparar_relatorio_mes_mes(),
        'relatorio_produtos': Eventos.preparar_relatorio_produtos(),
        'produtos_peraltas': ProdutosPeraltas.objects.all(),
        'campos_cadastro_eventos': Eventos.campos_cadastro_eventos()
    })


@permission_required('painelDiretoria.ver_estatisticas_monitoria', raise_exception=True)
def estatisticas_monitoria(request):
    escalas = EscalaAcampamento.objects.filter(
        check_in_cliente__date__gte=datetime.today().date(),
        check_out_cliente__date__lte=(datetime.today() + timedelta(days=6)).date(),
    ).order_by('check_in_cliente')
    grupos = [('Grupo', 'cliente'), ('Tipo', 'ficha_de_evento.produto'),
              ('Participantes', 'ficha_de_evento.qtd_convidada')]
    niveis_coordenacao = set()
    niveis_monitoria = set()

    # Dicionário para agrupar escalas por data
    escalas_por_data = {}

    for escala in escalas:
        data = escala.check_in_cliente.date()
        if data not in escalas_por_data:
            escalas_por_data[data] = []
        escalas_por_data[data].append(escala)

        for monitor in escala.monitores_acampamento.all():
            if monitor.nivel.coordenacao:
                niveis_coordenacao.add((monitor.nivel.nivel, monitor.nivel.id))
            else:
                niveis_monitoria.add((monitor.nivel.nivel, monitor.nivel.id))

    acumulado_relacao, acumulado_diarias = Metas.acumulado_dias(escalas)

    return render(request, 'painelDiretoria/estatisticas_monitoria.html', {
        'escalas_por_data': escalas_por_data,  # Passa o dicionário para o template
        'niveis_coordenacao': sorted(list(niveis_coordenacao)),
        'niveis_monitoria': sorted(list(niveis_monitoria)),
        'grupos': grupos,
        'n_escalas': len(escalas),
        'metas': Metas.objects.all().first(),
        'acumulado_relacao': acumulado_relacao,
        'acumulado_diarias': acumulado_diarias,
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
