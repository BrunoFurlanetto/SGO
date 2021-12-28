from datetime import datetime
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect
from cadastro.models import OrdemDeServico, Tipo
from django.views.decorators.csrf import csrf_exempt


@csrf_exempt
def dashboard(request):
    dados_iniciais = OrdemDeServico.objects.order_by('hora_atividade_1').filter(data_atendimento=datetime.now())
    ordem_de_servico = OrdemDeServico.objects.order_by('hora_atividade_1').filter(
                                                                data_atendimento=request.POST.get('data_selecionada'))
    tipos = []
    coordenadores = []
    equipe = []
    instituicoes = []
    dados = [tipos, instituicoes, coordenadores, equipe]

    for campo in ordem_de_servico:
        tipos.append(campo.tipo)
        instituicoes.append(campo.instituicao)
        coordenadores.append(campo.coordenador)
        equipe.append(campo.professor_2)
        equipe.append(campo.professor_3)
        equipe.append(campo.professor_4)

    if request.user.is_authenticated:

        if request.is_ajax() and request.method == 'POST':
            return HttpResponse(dados)

        return render(request, 'dashboard/dashboard.html', {'ordemDeServico': dados_iniciais})
    else:
        return redirect('login')
