from django.shortcuts import render


def ordem(request):
    return render(request, 'cadastro/ordem_servico')
