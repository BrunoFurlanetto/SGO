from time import sleep
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from .models import OrdemDeServico, Professores, Atividades, Tipo
import datetime


def publico(request):
    if not request.user.is_authenticated:
        return redirect('login')

    if request.method != 'POST':
        return render(request, 'cadastro/publico.html')

    # --- TESTES PARA A EXISTÊNCIA DAS ATIVIDADES E JÁ CHAMAR FUNÇÃO PRA JUNTAR OS PROFESSORES
    # --- DAS ATIVIDADES EXISTÊNTES.

    return redirect('dashboard')


def colegio(request):
    if not request.user.is_authenticated:
        return redirect('login')

    if request.method != 'POST':
        return render(request, 'cadastro/colegio.html')

    # --- TESTES PARA A EXISTÊNCIA DAS ATIVIDADES E JÁ CHAMAR FUNÇÃO PRA JUNTAR OS PROFESSORES
    # --- DAS ATIVIDADES EXISTÊNTES.

    return redirect('dashboard')


def empresa(request):
    if not request.user.is_authenticated:
        return redirect('login')

    if request.method != 'POST':
        return render(request, 'cadastro/empresa.html')

    # --- TESTES PARA EXISTÊNCIA DE ALGUMA ATIVIDADE E JÁ CHAMAR FUNÇÃO PRA JUNTAR OS PROFESSORES
    # --- DAS ATIVIDADES EXISTÊNTES.

    # --- PRIMEIRA ENTRADA E SAIDA DA EMPRESA NO CEU, PEGAR HORÁRIOS DE ENTRADAS E SAÍDAS,
    # --- FAZER CONTA DE HORAS DA PRIMEIRA LOCAÇÃO, TUDO COM FUNCÕES

    return redirect('dashboard')
