from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect


@login_required(login_url='login')
def resumo_financeiro_ceu(request):
    if request.method != 'POST':
        return render(request, 'ceu/resumo_financeiro_ceu.html')
