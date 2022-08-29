from datetime import datetime
from itertools import chain

from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from django.http import FileResponse, JsonResponse

from ceu.funcoes import criar_pdf_relatorio, pegar_dados_evento, pegar_escalas
from ceu.models import Professores
from dashboard.funcoes import is_ajax
from ordemDeServico.models import OrdemDeServico
from projetoCEU.utils import verificar_grupo


@login_required(login_url='login')
def resumo_financeiro_ceu(request):
    if request.method != 'POST':
        return render(request, 'ceu/resumo_financeiro_ceu.html')


@login_required(login_url='login')
def detector_de_bombas(request):
    grupos = verificar_grupo(request.user.groups.all())
    professores = Professores.objects.all()

    if request.method == 'GET':
        if request.GET.get('data_inicio'):
            data_inicio = datetime.strptime(request.GET.get('data_inicio'), '%Y-%m-%d')
            data_final = datetime.strptime(request.GET.get('data_final'), '%Y-%m-%d')

            ordens_intervalo = (OrdemDeServico.objects
                                .filter(escala_ceu=True)
                                .filter(check_in__date__gte=data_inicio, check_in__date__lte=data_final)
                                )

            return render(request, 'ceu/detector_de_bombas.html', {'grupos': grupos,
                                                                   'eventos': ordens_intervalo,
                                                                   'pesquisado': True,
                                                                   'professores': professores
                                                                   })

    if is_ajax(request):
        print(request.POST)
        atividades_eventos = pegar_dados_evento(request.POST)
        escalas = pegar_escalas(request.POST)
        return JsonResponse({'atividades_eventos': atividades_eventos, 'escalas': escalas})

    if request.method != 'POST':
        return render(request, 'ceu/detector_de_bombas.html', {'grupos': grupos})
