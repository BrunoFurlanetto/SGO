from django.shortcuts import render


def eventos(request):
    return render(request, 'calendarioEventos/calendario_eventos.html')
