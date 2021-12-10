from django.shortcuts import render, redirect
from .models import FormularioOrdem, OrdemDeServico, Professores


def publico(request):
    if not request.user.is_authenticated:
        return redirect('login')

    professores = Professores.objects.all()
    os = OrdemDeServico.objects.all()

    if request.method != 'POST':
        return render(request, 'cadastro/publico.html', {'os': os, 'professores': professores})


def colegio(request):
    if not request.user.is_authenticated:
        return redirect('login')


def empresa(request):
    if not request.user.is_authenticated:
        return redirect('login')

    if request.method != 'POST':
        return render(request, 'cadastro/empresa.html')
