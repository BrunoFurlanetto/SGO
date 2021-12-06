from django.shortcuts import render


def publico(request):
    return render(request, 'cadastro/publico.html')


def colegio(request):
    return render(request, 'cadastro/colegio.html')


def empresa(request):
    return render(request, 'cadastro/empresa.html')
