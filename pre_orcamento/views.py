from django.shortcuts import render


def dashboard(request):
    usuario = request.user

    return render(request, 'pre_orcamento/dashoboard.html')
