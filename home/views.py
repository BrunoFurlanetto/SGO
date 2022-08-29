from django.shortcuts import render, redirect
from django.contrib import auth, messages
from django.contrib.auth.models import User

from projetoCEU.utils import email_error


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
    except User.DoesNotExist:
        messages.error(request, 'Email e/ou senha inválidos')
        return render(request, 'home/index.html')
    except Exception as e:
        email_error(usuario='unknown', erro=e, view=__name__)
        messages.error(request, 'Email e/ou senha inválidos')
        return render(request, 'home/index.html')
    else:
        return redirect('dashboard')


def logout(request):
    auth.logout(request)
    return redirect('login')




