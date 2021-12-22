from datetime import datetime

from django.shortcuts import render, redirect

from cadastro.models import OrdemDeServico


def dashboard(request):
    ordemDeServico = OrdemDeServico.objects.order_by('data_atendimento') # .order_by('hora_atividade_1').filter(data_atendimento=datetime.now())

    if request.user.is_authenticated:
        return render(request, 'dashboard/dashboard.html', {'ordemDeServico': ordemDeServico})
    else:
        return redirect('login')

