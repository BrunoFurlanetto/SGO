from django.shortcuts import render


def ficha_financeira(request):
    return render(request, 'financeiro/ficha_financeira.html')
