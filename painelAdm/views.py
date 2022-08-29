from datetime import datetime
from datetime import datetime

from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from ceu.models import Professores
from cadastro.models import RelatorioDeAtendimentoPublicoCeu
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
        ordens_mes_anterior = RelatorioDeAtendimentoPublicoCeu.objects.filter(data_atendimento__month=datetime.now().month - 1)
        ordens_meses_ano_atual = RelatorioDeAtendimentoPublicoCeu.objects.filter(data_atendimento__year=datetime.now().year)
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
            ordens_mes_e_ano_selecionado = RelatorioDeAtendimentoPublicoCeu.objects.filter(data_atendimento__year=ano).filter(
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
