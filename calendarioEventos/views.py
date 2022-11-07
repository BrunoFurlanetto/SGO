from datetime import datetime

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect

from cadastro.funcoes import is_ajax
from ordemDeServico.models import OrdemDeServico
from peraltas.models import FichaDeEvento, PreReserva, CadastroPreReserva, ClienteColegio
from projetoCEU.utils import verificar_grupo, email_error


@login_required(login_url='login')
def eventos(request):
    ordens = OrdemDeServico.objects.all()
    fichas_de_evento = FichaDeEvento.objects.all()
    pre_reservas = PreReserva.objects.filter(ficha_evento=False)
    cadastro_de_pre_reservas = CadastroPreReserva()
    clientes = ClienteColegio.objects.all()
    professor_ceu = False
    grupos = verificar_grupo(request.user.groups.all())

    comercial = User.objects.filter(pk=request.user.id, groups__name='Comercial').exists()

    if request.user in User.objects.filter(groups__name='CEU') and request.user in User.objects.filter(
            groups__name='Professor'):
        professor_ceu = True

    if is_ajax(request):

        if request.method == 'GET':
            consulta_pre_reservas = PreReserva.objects.filter(agendado=False)
            consulta_fichas_de_evento = FichaDeEvento.objects.filter(os=False)
            tamanho = len(consulta_pre_reservas) + len(consulta_fichas_de_evento)

            return HttpResponse(tamanho)

        cliente = ClienteColegio.objects.get(nome_fantasia=request.POST.get('cliente'))
        check_in = datetime.strptime(request.POST.get('check_in'), '%Y-%m-%d %H:%M')
        check_out = datetime.strptime(request.POST.get('check_out'), '%Y-%m-%d %H:%M')
        pre_reserva = PreReserva.objects.get(cliente=cliente, check_in=check_in, check_out=check_out)

        if request.POST.get('excluir'):
            try:
                pre_reserva.delete()
            except Exception as e:
                messages.error(request, f'Pré reserva não excluida: f{e}')
                return redirect('calendario_eventos')
            else:
                return redirect('calendario_eventos')

        return JsonResponse({
            'qtd': pre_reserva.participantes,
            'cliente': pre_reserva.cliente.id,
            'id': pre_reserva.id,
            'vendedor': pre_reserva.vendedor.id,
            'confirmado': pre_reserva.agendado,
            'observacoes': pre_reserva.observacoes
        })

    if request.method != 'POST':
        return render(request, 'calendarioEventos/calendario_eventos.html',
                      {'eventos': ordens, 'fichas': fichas_de_evento,
                       'professor_ceu': professor_ceu, 'comercial': comercial,
                       'pre_reservas': pre_reservas, 'cadastro_pre_reserva': cadastro_de_pre_reservas,
                       'clientes': clientes,
                       'grupos': grupos})

    if request.POST.get('editar') or request.POST.get('confirmar_agendamento'):

        pre_reserva = PreReserva.objects.get(id=int(request.POST.get('id_pre_reserva')))

        if request.POST.get('confirmar_agendamento'):
            try:
                pre_reserva.agendado = True
                pre_reserva.save()
            except Exception as e:
                email_error(request.user.get_full_name(), e, __name__)
                messages.warning(request, f'Pré agendamento não confirmado!')
                messages.error(request, f'{e}')
            finally:
                return redirect('calendario_eventos')

        if request.POST.get('editar'):
            try:
                editar_pre_reserva = CadastroPreReserva(request.POST, instance=pre_reserva)
                editar_pre_reserva.save()
            except Exception as e:
                email_error(request.user.get_full_name(), e, __name__)
                messages.warning(request, 'Pré agendamento não alterado!')
                messages.error(request, 'Houve um erro inesperado, tente novamente mais tarde!')
            finally:
                return redirect('calendario_eventos')

    cadastro_de_pre_reservas = CadastroPreReserva(request.POST)
    nova_pre_reserva = cadastro_de_pre_reservas.save(commit=False)

    cliente_salvar = ClienteColegio.objects.get(id=int(request.POST.get('clientes')))
    nova_pre_reserva.cliente = cliente_salvar

    if cadastro_de_pre_reservas.is_valid():
        cadastro_de_pre_reservas.save()

        return redirect('calendario_eventos')
    else:
        messages.warning(request, f'{cadastro_de_pre_reservas.errors}')
        return redirect('calendario_eventos')

