from datetime import datetime, timedelta
from itertools import chain

from django.contrib.auth.decorators import login_required, permission_required, user_passes_test
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.decorators.http import require_GET

from ordemDeServico.models import OrdemDeServico
# from cozinha.models import RelatorioDia, Relatorio
from painelDiretoria.models import Metas
from peraltas.models import Eventos, ProdutosPeraltas, EscalaAcampamento
from pesquisasSatisfacao.models import CoordenacaoAvaliandoMonitoria, MonitorAvaliandoCoordenacao, AvaliacaoCorporativo, \
    AvaliacaoColegio
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
        check_out_cliente__date__lte=(datetime.today() + timedelta(days=7)).date(),
    ).order_by('check_in_cliente')
    grupos = [('Grupo', 'cliente'), ('Tipo', 'ficha_de_evento.produto'),
              ('Participantes', 'ficha_de_evento.qtd_convidada')]

    # Dicionário para agrupar escalas por data
    escalas_por_data = {}
    n_monitores = []
    n_coordenadores = []

    for escala in escalas:
        escala.monitores = []
        data = escala.check_in_cliente.date()

        if escala.ficha_de_evento.os:
            ordem = OrdemDeServico.objects.get(ficha_de_evento=escala.ficha_de_evento)
            escala.escala_coordenadores = ordem.monitor_responsavel

        if data not in escalas_por_data:
            escalas_por_data[data] = []

        for monitor in escala.monitores_acampamento.all():
            if len(escala.escala_coordenadores.all()) > 0:
                try:
                    if monitor not in escala.escala_coordenadores.all():
                        escala.monitores.append(monitor)
                except AttributeError:
                    escala.monitores.append(monitor)
            else:
                escala.monitores.append(monitor)

        n_coordenadores = escala.escala_coordenadores.all() if len(escala.escala_coordenadores.all()) > 0 else n_coordenadores
        n_monitores = escala.monitores if len(escala.monitores) > len(n_monitores) else n_monitores
        escalas_por_data[data].append(escala)
    print(n_coordenadores)
    acumulado_relacao, acumulado_diarias = Metas.acumulado_dias(escalas)

    return render(request, 'painelDiretoria/estatisticas_monitoria.html', {
        'escalas_por_data': escalas_por_data,  # Passa o dicionário para o template
        'grupos': grupos,
        'n_escalas': len(escalas),
        'metas': Metas.objects.all().last(),
        'acumulado_relacao': acumulado_relacao,
        'acumulado_diarias': acumulado_diarias,
        'max_monitores': range(0, len(n_monitores)),
        'max_coordenadores': range(0, len(n_coordenadores)),
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


def avaliacoes(request):
    avaliacoes_monitores = CoordenacaoAvaliandoMonitoria.objects.all()
    avaliacoes_coordenadores = MonitorAvaliandoCoordenacao.objects.all()
    avaliacoes_colegio = AvaliacaoColegio.objects.all()
    avaliacoes_corporativo = AvaliacaoCorporativo.objects.all()
    avaliacoes_clientes = list(chain(avaliacoes_colegio, avaliacoes_corporativo))

    return render(request, 'painelDiretoria/avaliacoes.html', {
        'avaliacoes_monitores': avaliacoes_monitores,
        'avaliacoes_coordenadores': avaliacoes_coordenadores,
        'avaliacoes_clientes': avaliacoes_clientes,
    })
