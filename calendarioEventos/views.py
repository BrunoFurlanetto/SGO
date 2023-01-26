from datetime import datetime

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect

import cadastro.funcoes
from cadastro.funcoes import is_ajax
from calendarioEventos.funcoes import gerar_lotacao
from ordemDeServico.models import OrdemDeServico
from peraltas.models import FichaDeEvento, CadastroPreReserva, ClienteColegio, RelacaoClienteResponsavel
from projetoCEU.utils import verificar_grupo, email_error


@login_required(login_url='login')
def eventos(request):
    fichas_de_evento = FichaDeEvento.objects.filter(pre_reserva=False)
    pre_reservas = FichaDeEvento.objects.filter(pre_reserva=True)
    cadastro_de_pre_reservas = CadastroPreReserva()
    clientes = ClienteColegio.objects.all()
    ordens = OrdemDeServico.objects.all()
    professor_ceu = request.user.has_perm('cadastro.add__relatoriodeatendimentopublicoceu')
    comercial = request.user.has_perm('peraltas.add_prereserva')

    if is_ajax(request):
        if request.method == 'GET':
            if request.GET.get('mes'):
                return JsonResponse(gerar_lotacao(request.GET.get('mes'), request.GET.get('ano')))

            consulta_pre_reservas = FichaDeEvento.objects.filter(agendado=False)
            consulta_fichas_de_evento = FichaDeEvento.objects.filter(os=False)
            tamanho = len(consulta_pre_reservas) + len(consulta_fichas_de_evento)

            return HttpResponse(tamanho)

        if request.POST.get('id_cliente'):
            cliente = ClienteColegio.objects.get(pk=request.POST.get('id_cliente'))
            relacoes = RelacaoClienteResponsavel.objects.get(cliente=cliente)

            return JsonResponse({'responsaveis': [responsavel.id for responsavel in relacoes.responsavel.all()]})

        if request.POST.get('id_produto'):
            return JsonResponse(cadastro.funcoes.requests_ajax(request.POST))

        if not request.POST.get('cnpj'):
            cliente = ClienteColegio.objects.get(nome_fantasia=request.POST.get('cliente'))
        else:
            cliente = ClienteColegio.objects.get(cnpj=request.POST.get('cnpj'))

        check_in = datetime.strptime(request.POST.get('check_in'), '%Y-%m-%d %H:%M')
        check_out = datetime.strptime(request.POST.get('check_out'), '%Y-%m-%d %H:%M')
        pre_reserva = FichaDeEvento.objects.get(
            cliente=cliente,
            check_in=check_in,
            check_out=check_out,
            pre_reserva=True
        )

        if request.POST.get('excluir'):
            try:
                pre_reserva.delete()
            except Exception as e:
                messages.error(request, f'Pré reserva não excluida: f{e}')
                return redirect('calendario_eventos')
            else:
                return redirect('calendario_eventos')

        return JsonResponse({
            'id': pre_reserva.id,
            'cliente': pre_reserva.cliente.id,
            'responavel_evento': pre_reserva.responsavel_evento.id,
            'produto': pre_reserva.produto.id,
            'obs_edicao': pre_reserva.obs_edicao_horario,
            'qtd': pre_reserva.qtd_convidada,
            'vendedor': pre_reserva.vendedora.id,
            'editar': pre_reserva.vendedora.usuario.id == request.user.id,
            'confirmado': pre_reserva.agendado,
            'observacoes': pre_reserva.observacoes
        })

    if request.method != 'POST':
        return render(request, 'calendarioEventos/calendario_eventos.html', {
            'eventos': ordens,
            'fichas': fichas_de_evento,
            'professor_ceu': professor_ceu,
            'comercial': comercial,
            'pre_reservas': pre_reservas,
            'cadastro_pre_reserva': cadastro_de_pre_reservas,
            'clientes': clientes
        })

    if request.POST.get('id_pre_reserva'):
        pre_reserva = FichaDeEvento.objects.get(pk=request.POST.get('id_pre_reserva'))

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

        try:
            editar_pre_reserva = CadastroPreReserva(request.POST, instance=pre_reserva)
            edicao = editar_pre_reserva.save(commit=False)
            edicao.pre_reserva = True
            editar_pre_reserva.save()
        except Exception as e:
            email_error(request.user.get_full_name(), e, __name__)
            messages.warning(request, 'Pré agendamento não alterado!')
            messages.error(request, 'Houve um erro inesperado, tente novamente mais tarde!')
        finally:
            return redirect('calendario_eventos')

    cadastro_de_pre_reservas = CadastroPreReserva(request.POST)
    nova_pre_reserva = cadastro_de_pre_reservas.save(commit=False)
    nova_pre_reserva.pre_reserva = True

    if cadastro_de_pre_reservas.is_valid():
        cadastro_de_pre_reservas.save()

        return redirect('calendario_eventos')
    else:
        messages.warning(request, f'{cadastro_de_pre_reservas.errors}')
        return redirect('calendario_eventos')
