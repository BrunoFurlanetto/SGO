from django.shortcuts import render, redirect

from cadastro.models import OrdemDeServico


def dashboard(request):
    ordemDeServico = OrdemDeServico.objects.all()

    if request.user.is_authenticated:
        return render(request, 'dashboard/dashboard.html', {'ordemDeServico': ordemDeServico})
    else:
        return redirect('login')

