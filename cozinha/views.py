from datetime import datetime, timedelta
from time import sleep

from django.contrib import messages
from django.shortcuts import render, redirect

from cozinha.models import Relatorio
from peraltas.models import FichaDeEvento, EscalaAcampamento


def cadastro_relatorio_cozinha(request):
    fichas_de_evento = FichaDeEvento.objects.filter(
        check_in__gte=datetime.today(),
        pre_reserva=False,
    ).order_by('check_in')
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
