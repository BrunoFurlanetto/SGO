from datetime import datetime, timedelta
from time import sleep

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.shortcuts import render, redirect

from cozinha.models import Relatorio, RelatorioDia
from peraltas.models import FichaDeEvento, EscalaAcampamento


@login_required(login_url='login')
def cadastro_relatorio_evento_cozinha(request):
    relatorios_feitos = [relatorio.ficha_de_evento.id for relatorio in Relatorio.objects.all()]
    fichas_de_evento = FichaDeEvento.objects.filter(
        check_in__gte=datetime.today(),
        pre_reserva=False,
    ).exclude(pk__in=relatorios_feitos).order_by('check_in')
    dados_evento = None

    if request.method == 'GET' and request.GET.get('fichas_de_evento'):
        ficha_de_evento = fichas_de_evento.get(pk=request.GET.get('fichas_de_evento'))
        data = ficha_de_evento.check_in
        datas = []
        numero_monitores = 0

        while data <= ficha_de_evento.check_out:
            datas.append(data)
            data += timedelta(days=1)

        if ficha_de_evento.escala:
            escala = EscalaAcampamento.objects.get(ficha_de_evento_id=ficha_de_evento.id)
            numero_monitores = len(escala.monitores_acampamento.all())

        dados_evento = {
            'datas': datas,
            'check_in': ficha_de_evento.check_in.strftime('%d/%m/%Y %H:%M'),
            'check_out': ficha_de_evento.check_out.strftime('%d/%m/%Y %H:%M'),
            'grupo': ficha_de_evento.cliente,
            'tipo_evento': ficha_de_evento.produto,
            'criancas': ficha_de_evento.numero_criancas(),
            'adultos': ficha_de_evento.numero_adultos(),
            'monitores': numero_monitores,
            'total': ficha_de_evento.numero_criancas() + ficha_de_evento.numero_adultos() + numero_monitores,
        }

    return render(request, 'cozinha/cadastro_relatorio_cozinha.html', {
        'fichas_de_evento': fichas_de_evento,
        'dados_evento': dados_evento,
    })


def salvar_evento(request):
    ficha_de_evento = FichaDeEvento.objects.get(pk=request.POST.get('id_ficha'))

    try:
        relatorio = Relatorio(
            ficha_de_evento=ficha_de_evento,
            grupo=ficha_de_evento.cliente,
            tipo_evento=ficha_de_evento.produto,
            pax_adulto=int(request.POST.get('adultos')),
            pax_crianca=int(request.POST.get('criancas')),
            pax_monitoria=int(request.POST.get('monitoria')),
        )
    except Exception as e:
        messages.error(request, f'Erro ao salvar o relatório ({e}). Tente novamente mais tarde.')
    else:
        refeicoes = Relatorio.dividir_refeicoes(request.POST)
        relatorio.salvar_refeicoes(refeicoes)
        relatorio.save()

        return redirect('dashboard')


@login_required(login_url='login')
def cadastro_relatorio_dia_cozinha(request):
    eventos = data = relatorios = None

    if request.method == 'GET' and request.GET.get('data'):
        data = datetime.strptime(request.GET.get('data'), '%Y-%m-%d').date()
        criancas = adultos = monitoria = geral = 0
        relatorios_evento = Relatorio.objects.filter(
            ficha_de_evento__check_in__date__lte=data,
            ficha_de_evento__check_out__date__gte=data,
        )
        relatorios = [relatorio.relatorio_refeicoes_dia(data) for relatorio in relatorios_evento]
        eventos = FichaDeEvento.objects.filter(
            check_in__date__lte=data,
            check_out__date__gte=data,
            pre_reserva=False,
        ).exclude(pk__in=[relatorio.ficha_de_evento.id for relatorio in relatorios_evento]).order_by('check_in')

    return render(request, 'cozinha/cadastro_relatorio_cozinha_dia.html', {
        'eventos': eventos,
        'relatorios': relatorios,
        'data': data,
    })


def salvar_relatorio_dia(request, data_refeicoes):
    refeicoes, id_eventos, ids_grupos = RelatorioDia.processar_refeicoes(request.POST)
    data_formatada = datetime.strptime(data_refeicoes, '%Y-%m-%d').date().strftime('%d/%m/%Y')
    print(ids_grupos, id_eventos)
    try:
        relatorio = RelatorioDia.objects.create(
            data=datetime.strptime(data_refeicoes, '%Y-%m-%d').date(),
            dados_cafe_da_manha=refeicoes['dados_cafe_da_manha'],
            dados_lanche_da_manha=refeicoes['dados_lanche_da_manha'],
            dados_almoco=refeicoes['dados_almoco'],
            dados_lanche_da_tarde=refeicoes['dados_lanche_da_tarde'],
            dados_jantar=refeicoes['dados_jantar'],
            dados_lanche_da_noite=refeicoes['dados_lanche_da_noite'],
        )
        relatorio.fichas_de_evento.add(*id_eventos)
        relatorio.grupos.add(*ids_grupos)
    except Exception as e:
        messages.error(request, f'Erro ao salvar o relatório do dia ({e}). Por favor tente mais tarde!')
        return redirect('dashboard')
    else:
        messages.success(request, f'Relatório das refeições do dia {data_formatada} salva com sucesso!')
        return redirect('dashboard')
