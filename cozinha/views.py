from datetime import datetime, timedelta
from itertools import chain
from time import sleep

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.decorators.http import require_POST

from cozinha.models import HorarioRefeicoes, RegistroVisualizacoes, CardapioForms, Cardapio
from cozinha.utils import filtrar_reservas_por_dia, filtrar_reservas_por_hotcodigo, filtrar_refeicoes
# from cozinha.models import Relatorio, RelatorioDia
from peraltas.models import FichaDeEvento, EscalaAcampamento


@login_required(login_url='login')
def dashboard(request):
    eventos = FichaDeEvento.objects.filter(
        pre_reserva=False
    )
    hotelaria = FichaDeEvento.objects.filter(
        pre_reserva=True,
        agendado=True,
        produto__brotas_eco=True
    )
    eventos_totais = list(chain(eventos, hotelaria))
    dados_eventos = []

    for evento in eventos_totais:
        dados_eventos.append({
            'title': f'Refeições de {evento.cliente}',
            'start': evento.check_in.astimezone().strftime('%Y-%m-%d %H:%M'),
            'end': evento.check_out.astimezone().strftime('%Y-%m-%d %H:%M'),
            'url': reverse('visualizar_relatorio_evento_cozinha', kwargs={
                'id_evento': evento.pk,
            }),
            'color': '#ff7474',
        })

    return render(request, 'cozinha/dashboard_cozinha.html', {
        'relatorios_refeicoes': dados_eventos,
    })


def salvar_visualizacao_cozinheiro(request):
    try:
        RegistroVisualizacoes.objects.get_or_create(
            usuario=request.user,
            data_refeicoes=datetime.strptime(request.POST.get('data_refeicoes'), '%Y-%m-%d').date(),
            defaults={
                'usuario': request.user,
                'data_refeicoes': datetime.strptime(request.POST.get('data_refeicoes'), '%Y-%m-%d'),
            }
        )
    except Exception as e:
        messages.error(request, f'Houve um erro inesperado ao salvar a sua visualização ({e}), por favor tente novamente mais tarde!')
        return redirect('dashboard')

    messages.success(request, 'Visualização das refeições salva com sucesso!')
    return redirect('dashboard')


# def verificar_relatorios_dia(request, data):
#     data_formatada = datetime.strptime(data, '%Y-%m-%d').date()
#
#     if RelatorioDia.objects.filter(data=data_formatada).exists():
#         return redirect('edicao_relatorio_dia_cozinha', data_formatada.strftime('%Y-%m-%d'))
#     else:
#         return redirect(reverse('cadastro_relatorio_dia_cozinha') + f'?data={data_formatada}')
#
#
# @login_required(login_url='login')
# def cadastro_relatorio_evento_cozinha(request):
#     relatorios_feitos = [relatorio.ficha_de_evento.id for relatorio in Relatorio.objects.all()]
#     fichas_de_evento = FichaDeEvento.objects.filter(
#         check_in__gte=datetime.today(),
#         pre_reserva=False,
#     ).exclude(pk__in=relatorios_feitos).order_by('check_in')
#     dados_evento = None
#
#     if request.method == 'GET' and request.GET.get('fichas_de_evento'):
#         ficha_de_evento = fichas_de_evento.get(pk=request.GET.get('fichas_de_evento'))
#         data = ficha_de_evento.check_in
#         datas = []
#         numero_monitores = 0
#
#         while data <= ficha_de_evento.check_out:
#             datas.append(data)
#             data += timedelta(days=1)
#
#         if ficha_de_evento.escala:
#             escala = EscalaAcampamento.objects.get(ficha_de_evento_id=ficha_de_evento.id)
#             numero_monitores = len(escala.monitores_acampamento.all())
#
#         dados_evento = {
#             'datas': datas,
#             'check_in': ficha_de_evento.check_in.strftime('%d/%m/%Y %H:%M'),
#             'check_out': ficha_de_evento.check_out.strftime('%d/%m/%Y %H:%M'),
#             'grupo': ficha_de_evento.cliente,
#             'tipo_evento': ficha_de_evento.produto,
#             'criancas': ficha_de_evento.numero_criancas(),
#             'adultos': ficha_de_evento.numero_adultos(),
#             'monitores': numero_monitores,
#             'total': ficha_de_evento.numero_criancas() + ficha_de_evento.numero_adultos() + numero_monitores,
#         }
#
#     return render(request, 'cozinha/cadastro_relatorio_cozinha.html', {
#         'fichas_de_evento': fichas_de_evento,
#         'dados_evento': dados_evento,
#     })


def ver_relatorio_evento_cozinha(request, id_evento):
    evento = FichaDeEvento.objects.get(pk=id_evento)
    numero_monitores = 0

    if evento.escala:
        numero_monitores = len(EscalaAcampamento.objects.get(ficha_de_evento__id=evento.id).monitores_acampamento.all())

    dados_evento = {
        'monitores': numero_monitores,
        'grupo': evento.cliente,
        'tipo_evento': evento.produto,
        'check_in': evento.check_in.strftime('%d/%m/%Y %H:%m'),
        'check_out': evento.check_out.strftime('%d/%m/%Y %H:%m'),
        'id_ficha': evento.id,
        'obs': evento.observacoes_refeicoes,
    }

    datas = []
    data = evento.check_in

    while data <= evento.check_out:
        datas.append(data)
        data += timedelta(days=1)

    dados_evento['datas'] = datas

    if evento.produto.brotas_eco:
        dados_evento['refeicoes_data'] = {
            evento.check_in.date(): ['cafe_manha', 'almoco', 'jantar']
        }
    else:
        dados_evento['refeicoes_data'] = {
            datetime.strptime(data, '%Y-%m-%d').date(): refeicoes for data, refeicoes in evento.refeicoes.items()
        }

    if evento.produto.brotas_eco:
        quantidades, adultos, criancas = filtrar_refeicoes(evento.check_in.date())
        dados_evento['contagem'] = quantidades
        dados_evento['adultos'] = adultos
        dados_evento['criancas'] = criancas
        dados_evento['total'] = adultos + criancas
    else:
        dados_evento['criancas'] = evento.numero_criancas()
        dados_evento['adultos'] = evento.numero_adultos()
        dados_evento['total'] = evento.numero_criancas() + evento.numero_adultos() + numero_monitores

    return render(request, 'cozinha/cadastro_relatorio_cozinha.html', {
        'dados_evento': dados_evento,
        'horario_refeicoes': HorarioRefeicoes.horarios(),
    })


# def salvar_evento(request):
#     ficha_de_evento = FichaDeEvento.objects.get(pk=request.POST.get('id_ficha'))
#     print(request.POST)
#     try:
#         # Tenta recuperar o relatório existente com base na ficha_de_evento
#         relatorio, criado = Relatorio.objects.get_or_create(
#             ficha_de_evento=ficha_de_evento,
#             defaults={
#                 'grupo': ficha_de_evento.cliente,
#                 'tipo_evento': ficha_de_evento.produto,
#                 'pax_adulto': int(request.POST.get('adultos')),
#                 'pax_crianca': int(request.POST.get('criancas')),
#                 'pax_monitoria': int(request.POST.get('monitoria')),
#             }
#         )
#
#         if not criado:
#             relatorio.pax_adulto = int(request.POST.get('adultos'))
#             relatorio.pax_crianca = int(request.POST.get('criancas'))
#             relatorio.pax_monitoria = int(request.POST.get('monitoria'))
#             relatorio.dados_cafe_da_manha = relatorio.dados_lanche_da_manha = relatorio.dados_almoco = None
#             relatorio.dados_lanche_da_tarde = relatorio.dados_jantar = relatorio.dados_lanche_da_noite = None
#             # Atualize outros campos mutáveis, se necessário
#     except Exception as e:
#         messages.error(request, f'Erro ao salvar o relatório ({e}). Tente novamente mais tarde.')
#         return redirect('dashboard')
#     else:
#         # Atualiza as refeições independentemente de ser um novo ou existente
#         refeicoes = Relatorio.dividir_refeicoes(request.POST)
#         relatorio.salvar_refeicoes(refeicoes)
#         relatorio.save()
#
#         if criado:
#             messages.success(request, 'Relatório criado com sucesso!')
#         else:
#             messages.success(request, 'Relatório atualizado com sucesso!')
#
#         return redirect('dashboard')


# @login_required(login_url='login')
# def cadastro_relatorio_dia_cozinha(request):
#     eventos = data = relatorios = None
#
#     if request.method == 'GET' and request.GET.get('data'):
#         data = datetime.strptime(request.GET.get('data'), '%Y-%m-%d').date()
#         criancas = adultos = monitoria = geral = 0
#         relatorios_evento = Relatorio.objects.filter(
#             ficha_de_evento__check_in__date__lte=data,
#             ficha_de_evento__check_out__date__gte=data,
#         )
#         relatorios = [relatorio.relatorio_refeicoes_dia(data) for relatorio in relatorios_evento]
#         eventos = FichaDeEvento.objects.filter(
#             check_in__date__lte=data,
#             check_out__date__gte=data,
#             pre_reserva=False,
#         ).exclude(pk__in=[relatorio.ficha_de_evento.id for relatorio in relatorios_evento]).order_by('check_in')
#
#     return render(request, 'cozinha/cadastro_relatorio_cozinha_dia.html', {
#         'eventos': eventos,
#         'relatorios': relatorios,
#         'data': data,
#     })

@login_required(login_url='login')
def ver_relatorio_dia_cozinha(request, data):
    data_datetime = datetime.strptime(data, '%Y-%m-%d').date()
    formulario_cardapio = CardapioForms(
        initial={
            'data_refeicao': data_datetime,
            'cadastrado_por': request.user.pk,
        })
    link_cardapio = None

    try:
        cardapio = Cardapio.objects.get(data_refeicao=data_datetime)
    except Cardapio.DoesNotExist:
        ...
    else:
        formulario_cardapio = CardapioForms(instance=cardapio)
        link_cardapio = cardapio.cardapio

    return render(request, 'cozinha/cadastro_relatorio_cozinha_dia.html', {
        'eventos': FichaDeEvento.separar_refeicoes(data_datetime),
        'data': data_datetime,
        'horarios_refeicoes': HorarioRefeicoes.horarios(),
        'visto': RegistroVisualizacoes.objects.filter(usuario=request.user, data_refeicoes=data_datetime).exists(),
        'formulario_cardapio': formulario_cardapio,
        'link_cardapio': link_cardapio,
    })


@require_POST
def cadastro_cardapio(request):
    form = CardapioForms(request.POST, request.FILES)
    print(request.POST, request.FILES)
    if form.is_valid():
        data_refeicao = form.cleaned_data['data_refeicao']
        novo_cardapio = form.cleaned_data['cardapio']

        try:
            cardapio_existente = Cardapio.objects.get(data_refeicao=data_refeicao)
        except Cardapio.DoesNotExist:
            form.save()
        else:
            cardapio_existente.cardapio.delete(save=False)  # Deleta o arquivo antigo
            cardapio_existente.cardapio = novo_cardapio
            cardapio_existente.save()

        return redirect('dashboard')  # Redirecione para onde for necessário


# def salvar_relatorio_dia(request, data_refeicoes):
#     refeicoes, id_eventos, ids_grupos = RelatorioDia.processar_refeicoes(request.POST)
#     data = datetime.strptime(data_refeicoes, '%Y-%m-%d').date()
#     data_formatada = data.strftime('%d/%m/%Y')
#     id_relatorio = request.POST.get('id_relatorio')
#     relatorios_evento = Relatorio.objects.filter(
#         ficha_de_evento__check_in__date__lte=data,
#         ficha_de_evento__check_out__date__gte=data,
#     )
#
#     try:
#         if id_relatorio:  # Caso um id_relatorio tenha sido enviado, tentamos editar o relatório existente
#             relatorio = RelatorioDia.objects.get(id=id_relatorio)  # Busca o relatório pelo id
#             relatorio.data = datetime.strptime(data_refeicoes, '%Y-%m-%d').date()
#             relatorio.dados_cafe_da_manha = refeicoes['dados_cafe_da_manha']
#             relatorio.dados_lanche_da_manha = refeicoes['dados_lanche_da_manha']
#             relatorio.dados_almoco = refeicoes['dados_almoco']
#             relatorio.dados_lanche_da_tarde = refeicoes['dados_lanche_da_tarde']
#             relatorio.dados_jantar = refeicoes['dados_jantar']
#             relatorio.dados_lanche_da_noite = refeicoes['dados_lanche_da_noite']
#         else:  # Caso contrário, cria um novo relatório
#             relatorio = RelatorioDia.objects.create(
#                 data=datetime.strptime(data_refeicoes, '%Y-%m-%d').date(),
#                 dados_cafe_da_manha=refeicoes['dados_cafe_da_manha'],
#                 dados_lanche_da_manha=refeicoes['dados_lanche_da_manha'],
#                 dados_almoco=refeicoes['dados_almoco'],
#                 dados_lanche_da_tarde=refeicoes['dados_lanche_da_tarde'],
#                 dados_jantar=refeicoes['dados_jantar'],
#                 dados_lanche_da_noite=refeicoes['dados_lanche_da_noite'],
#             )
#
#         # Atualizar ou adicionar os eventos e grupos relacionados
#         relatorio.fichas_de_evento.clear()  # Limpa os eventos atuais
#         relatorio.fichas_de_evento.add(*id_eventos)  # Adiciona os novos eventos
#         relatorio.grupos.clear()  # Limpa os grupos atuais
#         relatorio.grupos.add(*ids_grupos)  # Adiciona os novos grupos
#
#         # Salvar o objeto, caso tenha sido editado
#         relatorio.save()
#
#     except RelatorioDia.DoesNotExist:
#         messages.error(request, 'Relatório não encontrado. Por favor, verifique os dados e tente novamente.')
#         return redirect('dashboard')
#     except Exception as e:
#         messages.error(request, f'Erro ao salvar ou editar o relatório do dia ({e}). Por favor tente mais tarde!')
#         return redirect('dashboard')
#     else:
#         messages.success(request, f'Relatório das refeições do dia {data_formatada} salvo(a) com sucesso!')
#         return redirect('dashboard')

