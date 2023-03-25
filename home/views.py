from django.shortcuts import render, redirect
from django.contrib import auth, messages
from django.contrib.auth.models import User
from django.contrib.auth.forms import PasswordResetForm


def index(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method != 'POST':
        return render(request, 'home/index.html')

    email = request.POST.get('email')
    senha = request.POST.get('senha')

    try:
        username = User.objects.get(email=email.lower()).username
        user = auth.authenticate(request, username=username, password=senha)
        auth.login(request, user)
    except Exception as e:
        messages.error(request, 'Email e/ou senha inválidos')
        return render(request, 'home/index.html')
    else:
        return redirect('dashboard')


def logout(request):
    auth.logout(request)
    return redirect('login')


def manutencao(request):
    return render(request, 'home/manutencao.html')


def handler404(request, exception):
    return render(request, 'home/404.html')


def handler500(request, exception):
    return render(request, 'home/500.html', status=500)
