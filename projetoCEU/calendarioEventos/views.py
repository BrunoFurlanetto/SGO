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
    pre_reservas = PreReserva.objects.filter(ficha_evento=False)
    cadastro_de_pre_reservas = CadastroPreReserva()
    professor_ceu = False

    comercial = User.objects.filter(pk=request.user.id, groups__name='Comercial').exists()

    if request.user in User.objects.filter(groups__name='CEU') and request.user in User.objects.filter(
            groups__name='Professor'):
        professor_ceu = True

    if request.method != 'POST':
        return render(request, 'calendarioEventos/calendario_eventos.html',
                      {'eventos': ordens, 'fichas': fichas_de_evento,
                       'professor_ceu': professor_ceu, 'comercial': comercial,
                       'pre_reservas': pre_reservas, 'cadastro_pre_reserva': cadastro_de_pre_reservas})

    if is_ajax(request):
        cliente = ClienteColegio.objects.get(nome_fantasia=request.POST.get('cliente'))
        pre_reserva = PreReserva.objects.get(cliente=cliente)

        return JsonResponse({
            'qtd': pre_reserva.participantes,
            'id': pre_reserva.id,
            'vendedor': pre_reserva.vendedor.usuario.get_full_name(),
            'confirmado': pre_reserva.agendado,
            'observacoes': pre_reserva.observacoes
        })
    print(request.POST)
    if request.POST.get('id_pre_reserva'):
        pre_reserva = PreReserva.objects.get(id=int(request.POST.get('id_pre_reserva')))
        pre_reserva.agendado = True
        pre_reserva.save()

        return redirect('calendario_eventos')

    cadastro_de_pre_reservas = CadastroPreReserva(request.POST)

    if cadastro_de_pre_reservas.is_valid():
        cadastro_de_pre_reservas.save()

        return redirect('calendario_eventos')

