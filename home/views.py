from django.shortcuts import render, redirect
from django.contrib import auth, messages
from django.contrib.auth.models import User
from django.urls import reverse


def index(request):
    next_url = request.GET.get('next') or request.POST.get('next') or reverse('dashboard')

    if request.user.is_authenticated:
        return redirect(next_url)

    if request.method != 'POST':
        return render(request, 'home/index.html', {'next': next_url})

    email = request.POST.get('email')
    senha = request.POST.get('senha')

    try:
        username = User.objects.get(email=email.lower()).username
        user = auth.authenticate(request, username=username, password=senha)
        if user is not None:
            auth.login(request, user)

            return redirect(next_url)
        else:
            messages.error(request, 'Email e/ou senha inválidos')
    except User.DoesNotExist:
        messages.error(request, 'Email e/ou senha inválidos')

    return render(request, 'home/index.html', {'next': next_url})


def logout(request):
    auth.logout(request)
    return redirect('login')


def manutencao(request):
    return render(request, 'home/manutencao.html')


def handler404(request, exception):
    return render(request, 'home/404.html')


def handler403(request, exception):
    return render(request, 'home/403.html', status=403)


def handler500(request):
    return render(request, 'home/500.html', status=500)
