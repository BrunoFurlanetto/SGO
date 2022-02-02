from django.shortcuts import render, redirect

from cadastro.models import Professores
from painelAdm.funcoes import contar_atividades, contar_horas, contar_diaria


def painelGeral(request):
    if not request.user.is_authenticated:
        return redirect('login')

    professores = Professores.objects.all()

    for professor in professores:
        professor.n_atividades = contar_atividades(professor)
        professor.n_horas = contar_horas(professor)
        professor.n_diaria = contar_diaria(professor)

    return render(request, 'paineladm/painelGeral.html', {'professores': professores})
