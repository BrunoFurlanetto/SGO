from datetime import datetime

from django.http import HttpResponse
from django.shortcuts import render, redirect
from cadastro.models import Professores, OrdemDeServico
from painelAdm.funcoes import contar_atividades, contar_horas, contar_diaria, verificar_anos, is_ajax, pegar_mes


def painelGeral(request):
    if not request.user.is_authenticated:
        return redirect('login')

    consulta = OrdemDeServico.objects.all().order_by('-data_atendimento')[:200]
    anos = verificar_anos(consulta)

    if request.method != 'POST':
        professores = Professores.objects.all()
        ordens_mes_anterior = OrdemDeServico.objects.filter(data_atendimento__month=datetime.now().month-1)
        ordens_meses_ano_atual = OrdemDeServico.objects.filter(data_atendimento__year=datetime.now().year)
        mes_anterior = pegar_mes(ordens_mes_anterior)
        meses = pegar_mes(ordens_meses_ano_atual).split(', ')
        # meses.remove(mes_anterior)

        for professor in professores:
            professor.n_atividades = contar_atividades(professor)
            professor.n_horas = contar_horas(professor)
            professor.n_diaria = contar_diaria(professor)

        return render(request, 'paineladm/painelGeral.html', {'professores': professores, 'anos': anos,
                                                              'mesAnterior': mes_anterior,
                                                              'meses': meses})

    if is_ajax(request) and request.method == 'POST':
        ano = request.POST.get('ano')
        consulta_2 = OrdemDeServico.objects.filter(data_atendimento__year=ano)
        meses = pegar_mes(consulta_2)
        return HttpResponse(meses)
