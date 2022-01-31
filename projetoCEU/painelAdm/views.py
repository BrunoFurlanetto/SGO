from django.shortcuts import render


def painelGeral(request):
    return render(request, 'paineladm/painelGeral.html')
