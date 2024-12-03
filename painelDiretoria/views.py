from datetime import datetime, timedelta
from itertools import chain

from django.contrib.auth.decorators import login_required, permission_required, user_passes_test
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.decorators.http import require_GET

# from cozinha.models import RelatorioDia, Relatorio
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

    # Dicionário para agrupar escalas por data
    escalas_por_data = {}
    n_monitores = []
    n_coordenadores = []

    for escala in escalas:
        escala.coordenadores = []
        escala.monitores = []
        data = escala.check_in_cliente.date()

        if data not in escalas_por_data:
            escalas_por_data[data] = []

        for monitor in escala.monitores_acampamento.all():
            try:
                if monitor.nivel.coordenacao:
                    escala.coordenadores.append(monitor)
                else:
                    escala.monitores.append(monitor)
            except AttributeError:
                escala.monitores.append(monitor)

        n_coordenadores = escala.coordenadores if len(escala.coordenadores) > len(n_coordenadores) else n_coordenadores
        n_monitores = escala.monitores if len(escala.monitores) > len(n_monitores) else n_monitores
        escalas_por_data[data].append(escala)

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


def cozinha(request):
    # relatorios_dia = RelatorioDia.objects.all()
    # relatorios_evento = Relatorio.objects.all()
    dados_relatorios = []
    refecioes_eventos = []

    def criar_objeto_evento(refeicao, cliente, data, hora, participantes):
        cores = {
            'Café da Manhã': '#6610f2',
            'Lanche da Manhã': '#dc3545',
            'Almoço': '#fd7e14',
            'Lanche da Tarde': '#0dcaf0',
            'Jantar': '#f3cd0e',
            'Lanche da Noite': '#2cd32c',
        }
        inicio = datetime.combine(data, datetime.strptime(hora, "%H:%M").time())
        fim = inicio + timedelta(hours=1)

        return {
            'title': cliente.__str__(),
            'start': inicio.isoformat(),
            'end': fim.isoformat(),
            'color': cores[refeicao],
            'extendedProps': {
                'refeicao': refeicao,
                'adultos': participantes['adultos'],
                'criancas': participantes['criancas'],
                'monitoria': participantes['monitoria'],
                'total': participantes['total'],
            }
        }

    # Processar dados do RelatorioDia
    for relatorio in relatorios_dia:
        data = relatorio.data
        refecioes_eventos.append({
            'title': 'Refeições do dia',
            'start': relatorio.data.strftime('%Y-%m-%d'),
            'end': relatorio.data.strftime('%Y-%m-%d'),
            'url': reverse('edicao_relatorio_dia_cozinha', kwargs={
                'data_edicao': relatorio.data.strftime('%Y-%m-%d')
            }),
            'color': '#fcc607',
        })

        for refeicao, dados in [
            ("Café da Manhã", relatorio.dados_cafe_da_manha),
            ("Lanche da Manhã", relatorio.dados_lanche_da_manha),
            ("Almoço", relatorio.dados_almoco),
            ("Lanche da Tarde", relatorio.dados_lanche_da_tarde),
            ("Jantar", relatorio.dados_jantar),
            ("Lanche da Noite", relatorio.dados_lanche_da_noite),
        ]:
            if dados and "dados_grupos" in dados:
                for grupo in dados["dados_grupos"]:
                    for cliente in relatorio.grupos.all():
                        if cliente.id == grupo['grupo_id']:
                            cliente = cliente

                            break

                    evento = criar_objeto_evento(refeicao, cliente, data, grupo["hora"], grupo['participantes'])
                    dados_relatorios.append(evento)

    # Processar dados do Relatorio
    for relatorio in relatorios_evento:
        refecioes_eventos.append({
            'title': f'Refeições de {relatorio.grupo}',
            'start': relatorio.ficha_de_evento.check_in.strftime('%Y-%m-%d %H:%M'),
            'end': relatorio.ficha_de_evento.check_out.strftime('%Y-%m-%d %H:%M'),
            'url': reverse('edicao_relatorio_evento_cozinha', kwargs={
                'id_relatorio': relatorio.pk,
            }),
            'color': '#ff7474',
        })

        for refeicao, dados in [
            ("Café da Manhã", relatorio.dados_cafe_da_manha),
            ("Lanche da Manhã", relatorio.dados_lanche_da_manha),
            ("Almoço", relatorio.dados_almoco),
            ("Lanche da Tarde", relatorio.dados_lanche_da_tarde),
            ("Jantar", relatorio.dados_jantar),
            ("Lanche da Noite", relatorio.dados_lanche_da_noite),
        ]:
            if dados:
                for item in dados:
                    data = datetime.strptime(item["dia"], "%Y_%m_%d").date()
                    evento = criar_objeto_evento(refeicao, relatorio.grupo, data, item["hora"], item["participantes"])
                    dados_relatorios.append(evento)

    return render(request, 'painelDiretoria/cozinha.html', {
        'relatorios_refeicoes': dados_relatorios,
        'refeicoes_eventos': refecioes_eventos,
    })
