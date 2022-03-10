from django.shortcuts import render, redirect
from django.contrib import auth, messages
from django.contrib.auth.models import User


def index(request):
    if request.user.is_authenticated:
        if User.objects.filter(pk=request.user.id, groups__name='CEU').exists():
            return redirect('dashboardCeu')
        elif User.objects.filter(pk=request.user.id, groups__name='Peraltas').exists():
            return redirect('dashboardPeraltas')
        elif User.objects.filter(pk=request.user.id, groups__name='Colégio').exists():
            return redirect('fichaAvaliacao')

    if request.method != 'POST':
        return render(request, 'home/index.html')

    email = request.POST.get('email')
    senha = request.POST.get('senha')

    try:
        username = User.objects.get(email=email.lower()).username
        user = auth.authenticate(request, username=username, password=senha)
        auth.login(request, user)

        if User.objects.filter(pk=request.user.id, groups__name='CEU').exists():
            return redirect('dashboardCeu')
        elif User.objects.filter(pk=request.user.id, groups__name='Peraltas').exists():
            return redirect('dashboardPeraltas')
        elif User.objects.filter(pk=request.user.id, groups__name='Colégio').exists():
            return redirect('fichaAvaliacao')
    except:
        messages.error(request, 'Email e/ou senha inválidos')
        return render(request, 'home/index.html')


def logout(request):
    auth.logout(request)
    return redirect('login')




