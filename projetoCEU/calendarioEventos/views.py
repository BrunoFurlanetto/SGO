from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.shortcuts import render, redirect

from cadastro.funcoes import is_ajax
from ordemDeServico.models import OrdemDeServico
from peraltas.models import FichaDeEvento, PreReserva, CadastroPreReserva, ClienteColegio


@login_required(login_url='login')
def eventos(request):
    ordens = OrdemDeServico.objects.all()
    fichas_de_evento = FichaDeEvento.objects.all()
    pre_reservas = PreReserva.objects.all()
    cadastro_de_pre_reservas = CadastroPreReserva()
    professor_ceu = False

    ver_ficha = User.objects.filter(pk=request.user.id, groups__name='Coordenador monitoria').exists() or \
                User.objects.filter(pk=request.user.id, groups__name='Administrativo Peraltas').exists() or \
                User.objects.filter(pk=request.user.id, groups__name='Comercial').exists()
    ver_pre_reserva = User.objects.filter(pk=request.user.id, groups__name='Comercial').exists()

    if request.user in User.objects.filter(groups__name='CEU') and request.user in User.objects.filter(
            groups__name='Professor'):
        professor_ceu = True

    if request.method != 'POST':
        return render(request, 'calendarioEventos/calendario_eventos.html',
                      {'eventos': ordens, 'fichas': fichas_de_evento,
                       'professor_ceu': professor_ceu, 'ver_ficha': ver_ficha,
                       'ver_pre_reserva': ver_pre_reserva, 'pre_reservas': pre_reservas,
                       'cadastro_pre_reserva': cadastro_de_pre_reservas})

    if is_ajax(request):
        if request.POST.get('cliente'):
            print(request.POST)
            cliente = ClienteColegio.objects.get(nome_fantasia=request.POST.get('cliente'))
            pre_reserva = PreReserva.objects.get(cliente=cliente)

            return JsonResponse({
                'qtd': pre_reserva.participantes,
                'vendedor': pre_reserva.vendedor.usuario.get_full_name(),
                'observacoes': pre_reserva.observacoes
            })
        else:
            print(request.POST)


    cadastro_de_pre_reservas = CadastroPreReserva(request.POST)

    if cadastro_de_pre_reservas.is_valid():
        cadastro_de_pre_reservas.save()

        return redirect('calendario_eventos')

