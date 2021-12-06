from django.shortcuts import render

from cadastro.models import Professores, Tipo, Atividades


def dashboard(request):
    professor = Professores.objects.all
    tipo = Tipo.objects.all
    atividade = Atividades.objects.all

    return render(request, 'dashboard/dashboard.html',
                  {'professor': professor, 'tipo': tipo, 'atividade': atividade})


def publico(request):
    return render(request, 'dashboard/publico.html')
