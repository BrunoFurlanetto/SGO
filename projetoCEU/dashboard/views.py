from datetime import datetime

from django.contrib.auth.models import User
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect
from cadastro.models import OrdemDeServico, Tipo
from django.views.decorators.csrf import csrf_exempt

from escala.models import Escala


@csrf_exempt
def dashboard(request):
    if not request.user.is_authenticated:
        return redirect('login')

    ver_icons = User.objects.filter(pk=request.user.id, groups__name='Colégio').exists()

    if ver_icons:
        return redirect('fichaAvaliacao')

    dados_iniciais = OrdemDeServico.objects.order_by('hora_atividade_1').filter(data_atendimento=datetime.now())
    ordem_de_servico = OrdemDeServico.objects.order_by('hora_atividade_1').filter(
                                                                data_atendimento=request.POST.get('data_selecionada'))
    escala = Escala.objects.filter(data=datetime.now())
    escalaDoDia = []

    for professor in escala:
        if professor.coordenador is not None:
            escalaDoDia.append(professor.coordenador)

        if professor.professor_2 is not None:
            escalaDoDia.append(professor.professor_2)

        if professor.professor_3 is not None:
            escalaDoDia.append(professor.professor_3)

        if professor.professor_4 is not None:
            escalaDoDia.append(professor.professor_4)

        if professor.professor_5 is not None:
            escalaDoDia.append(professor.professor_5)

    data = datetime.now()
    ids = []
    tipos = []
    coordenadores = []
    equipe = []
    instituicoes = []
    dados = [ids, tipos, instituicoes, coordenadores, equipe]

    for campo in ordem_de_servico:
        ids.append(campo.id)
        tipos.append(campo.tipo)
        instituicoes.append(campo.instituicao)
        coordenadores.append(campo.coordenador)
        equipe.append(campo.professor_2)
        equipe.append(campo.professor_3)
        equipe.append(campo.professor_4)

    if request.user.is_authenticated:

        if is_ajax(request) and request.method == 'POST':
            return HttpResponse(dados)

        return render(request, 'dashboard/dashboard.html', {'ordemDeServico': dados_iniciais, 'data': data,
                                                            'escala': escalaDoDia})
    else:
        return redirect('login')


def is_ajax(request):
    return request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest'