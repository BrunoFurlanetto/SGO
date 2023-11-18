import locale
from datetime import datetime, timedelta
from datetime import datetime
from itertools import chain

from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from ceu.models import Professores
from cadastro.models import RelatorioDeAtendimentoPublicoCeu, RelatorioDeAtendimentoColegioCeu, \
    RelatorioDeAtendimentoEmpresaCeu
from painelAdm.funcoes import contar_atividades, contar_horas, contar_diaria, verificar_anos, is_ajax, pegar_mes, \
    pegar_atividades, contar_atividades_professor
from projetoCEU.utils import verificar_grupo


@login_required(login_url='login')
def painelGeral(request):
    consulta = RelatorioDeAtendimentoPublicoCeu.objects.all().order_by('-data_atendimento')[:200]
    anos = verificar_anos(consulta)
    professores = Professores.objects.all()
    grupos = verificar_grupo(request.user.groups.all())

    if request.method != 'POST':
        professores = Professores.objects.all()
        ordens_mes_anterior = RelatorioDeAtendimentoPublicoCeu.objects.filter(
            data_atendimento__month=datetime.now().month - 1)
        ordens_meses_ano_atual = RelatorioDeAtendimentoPublicoCeu.objects.filter(
            data_atendimento__year=datetime.now().year)
        mes_anterior = pegar_mes(ordens_mes_anterior)
        meses = pegar_mes(ordens_meses_ano_atual).split(', ')

        if len(mes_anterior) > 0:
            meses.remove(mes_anterior)

        for professor in professores:
            professor.n_atividades = contar_atividades(professor)
            # professor.n_horas = contar_horas(professor)
            # professor.n_diaria = contar_diaria(professor)

        return render(request, 'paineladm/painelGeral.html', {'professores': professores, 'anos': anos,
                                                              'mesAnterior': mes_anterior,
                                                              'meses': meses,
                                                              'grupos': grupos})

    if is_ajax(request) and request.method == 'POST':

        if request.POST.get('grafico') == '0':
            # ---- Parte que irá pegar os meses do ano selecionadao ----
            ano = request.POST.get('ano')
            consulta_2 = RelatorioDeAtendimentoPublicoCeu.objects.filter(data_atendimento__year=ano)
            meses = pegar_mes(consulta_2)
            return HttpResponse(meses)

        if request.POST.get('grafico') == '2':
            mes = request.POST.get('mes')
            ano = request.POST.get('ano')
            ordens_mes_e_ano_selecionado = RelatorioDeAtendimentoPublicoCeu.objects.filter(
                data_atendimento__year=ano).filter(
                data_atendimento__month=mes)
            atividades = pegar_atividades(ordens_mes_e_ano_selecionado)
            return JsonResponse({'dados': atividades})

        if request.POST.get('grafico') == '3':
            professor_selecionado = Professores.objects.get(pk=request.POST.get('id_professor'))
            ordens_prof = RelatorioDeAtendimentoPublicoCeu.objects.filter(Q(coordenador=professor_selecionado) |
                                                                          Q(professor_2=professor_selecionado) |
                                                                          Q(professor_3=professor_selecionado) |
                                                                          Q(professor_4=professor_selecionado)).order_by(
                '-data_atendimento')[:300]

            atividades_realizadas = contar_atividades_professor(professor_selecionado, ordens_prof)
            return JsonResponse({'dados': atividades_realizadas})


@login_required(login_url='login')
def resumo_ceu(request):
    locale.setlocale(locale.LC_TIME, 'pt_BR')
    relatorios_publico = RelatorioDeAtendimentoPublicoCeu.objects.all()[:200]
    relatorios_colegio = RelatorioDeAtendimentoColegioCeu.objects.all()[:200]
    relatorios_empresa = RelatorioDeAtendimentoEmpresaCeu.objects.all()[:200]
    relatorios = list(chain(relatorios_publico, relatorios_colegio, relatorios_empresa))
    datas_relatorio = []
    meses_relatorios = []
    dados_atividades = []

    for relatorio in relatorios:
        if relatorio.data_hora_salvo.date() not in datas_relatorio:

            try:
                datas_relatorio.append(relatorio.check_in.date())
            except AttributeError:
                datas_relatorio.append(relatorio.data_hora_salvo.date())

    datas_relatorio = sorted(datas_relatorio, reverse=True)

    for data in datas_relatorio:
        if {'mes': data.month, 'ano': data.year} not in meses_relatorios:
            meses_relatorios.append({'mes': data.month, 'ano': data.year})

    for data in meses_relatorios:
        participantes_mes = n_atividades = 0
        horas_locacoes = timedelta()
        relatorios_colegio_mes = RelatorioDeAtendimentoColegioCeu.objects.filter(
            check_in__month=data['mes'],
            check_in__year=data['ano']
        )
        relatorios_empresa_mes = RelatorioDeAtendimentoEmpresaCeu.objects.filter(
            check_in__month=data['mes'],
            check_in__year=data['ano']
        )
        relatorios_publico_mes = RelatorioDeAtendimentoPublicoCeu.objects.filter(
            data_atendimento__month=data['mes'],
            data_atendimento__year=data['ano']
        )
        relatorios_mes = list(chain(relatorios_publico_mes, relatorios_empresa_mes, relatorios_colegio_mes))

        for relatorio_mes in relatorios_mes:
            try:
                participantes_mes += relatorio_mes.participantes_confirmados if relatorio_mes.participantes_confirmados else 0
                n_atividades = len(relatorio_mes.atividades) if relatorio_mes.atividades else 0
                horas_locacoes += relatorio_mes.horas_totais_locacoes if relatorio_mes.horas_totais_locacoes else timedelta()
                print(horas_locacoes, relatorio_mes.horas_totais_locacoes, data['mes'])
            except AttributeError:
                ...

        total_seconds = horas_locacoes.total_seconds()
        horas, remainder = divmod(total_seconds, 3600)
        minutos, segundos = divmod(remainder, 60)
        dados_atividades.append({
            'mes': datetime(1, data['mes'], 1).strftime('%B').capitalize(),
            'ano': data['ano'],
            'participantes': participantes_mes,
            'n_atividades': n_atividades,
            'horas_locadas': f'{int(horas):02}:{int(minutos):02}'
        })

    print(dados_atividades)
    return render(request, 'painelAdm/resumo_ceu.html', {
        'dados_atividades': dados_atividades
    })
