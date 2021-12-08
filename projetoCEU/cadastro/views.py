from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required


def publico(request):
    if request.user.is_authenticated:
        return render(request, 'cadastro/publico.html')
    else:
        return redirect('login')


def colegio(request):
    if request.user.is_authenticated:
        return render(request, 'cadastro/colegio.html')
    else:
        return redirect('login')


def empresa(request):
    if request.user.is_authenticated:
        return render(request, 'cadastro/empresa.html')
    else:
        return redirect('login')
