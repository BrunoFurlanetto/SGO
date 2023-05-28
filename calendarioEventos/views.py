from datetime import datetime

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.db.models import Q
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect

import cadastro.funcoes
from cadastro.funcoes import is_ajax
from calendarioEventos.funcoes import gerar_lotacao
from ordemDeServico.models import OrdemDeServico
from peraltas.models import FichaDeEvento, CadastroPreReserva, ClienteColegio, RelacaoClienteResponsavel, \
    EventosCancelados, Eventos, Vendedor
from projetoCEU.envio_de_emails import EmailSender
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
    diretoria = User.objects.filter(pk=request.user.id, groups__name='Diretoria').exists()

    if is_ajax(request):
        if request.method == 'GET':
            if request.GET.get('mes'):
                return JsonResponse(gerar_lotacao(int(request.GET.get('mes')), int(request.GET.get('ano'))))

            if request.GET.get('data'):
                if not User.objects.filter(pk=request.user.id, groups__name='Diretoria').exists():
                    return JsonResponse({
                        'exclusividade': FichaDeEvento.objects.filter(
                            check_in__date__lte=datetime.strptime(request.GET.get('data'), '%Y-%m-%d'),
                            check_out__date__gte=datetime.strptime(request.GET.get('data'), '%Y-%m-%d'),
                            exclusividade=True,
                        ).exclude(check_out__date=datetime.strptime(request.GET.get('data'), '%Y-%m-%d')).exists()
                    })
                else:
                    return JsonResponse({'exclusividade': False})

            if request.GET.get('check_in'):
                fichas_intervalo = [
                    FichaDeEvento.objects.filter(
                        check_in__lte=datetime.strptime(request.GET.get('check_in'), '%Y-%m-%dT%H:%M'),
                        check_out__gte=datetime.strptime(request.GET.get('check_in'), '%Y-%m-%dT%H:%M')
                    ).exclude(cliente__id=int(request.GET.get('id_cliente'))).exists(), FichaDeEvento.objects.filter(
                        check_in__gte=datetime.strptime(request.GET.get('check_in'), '%Y-%m-%dT%H:%M'),
                        check_in__lte=datetime.strptime(request.GET.get('check_out'), '%Y-%m-%dT%H:%M')
                    ).exclude(cliente__id=int(request.GET.get('id_cliente'))).exists()
                ]

                return JsonResponse({'eventos': True in fichas_intervalo})

            consulta_pre_reservas = FichaDeEvento.objects.filter(agendado=False)
            consulta_fichas_de_evento = FichaDeEvento.objects.filter(os=False)
            tamanho = len(consulta_pre_reservas) + len(consulta_fichas_de_evento)

            return HttpResponse(tamanho)

        if request.POST.get('id_cliente'):
            cliente = ClienteColegio.objects.get(pk=request.POST.get('id_cliente'))

            try:
                relacoes = RelacaoClienteResponsavel.objects.get(cliente=cliente)
            except RelacaoClienteResponsavel.DoesNotExist:
                return JsonResponse({'responsaveis': []})
            else:
                return JsonResponse({'responsaveis': [responsavel.id for responsavel in relacoes.responsavel.all()]})

        if request.POST.get('id_produto'):
            return JsonResponse(cadastro.funcoes.requests_ajax(request.POST))

        pre_reserva = FichaDeEvento.objects.get(pk=request.POST.get('id_pre_reserva'))

        if request.POST.get('excluir'):
            try:
                EventosCancelados.objects.create(
                    cliente=pre_reserva.cliente.__str__(),
                    cnpj_cliente=pre_reserva.cliente.cnpj,
                    estagio_evento='pre_reserva' if not pre_reserva.agendado else 'reserva_confirmada',
                    atendente=pre_reserva.vendedora.usuario.get_full_name(),
                    produto_contratado=pre_reserva.produto,
                    produto_corporativo_contratado=pre_reserva.produto_corporativo,
                    data_entrada=pre_reserva.data_preenchimento,
                    data_saida=datetime.now().date(),
                    motivo_cancelamento=request.POST.get('motivo_cancelamento')
                )
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
            'produto_corporativo': pre_reserva.produto_corporativo.id if pre_reserva.produto_corporativo else None,
            'obs_edicao': pre_reserva.obs_edicao_horario,
            'exclusividade': pre_reserva.exclusividade,
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
            'diretoria': diretoria,
            'pre_reservas': pre_reservas,
            'cadastro_pre_reserva': cadastro_de_pre_reservas,
            'clientes': clientes
        })

    if request.POST.get('id_pre_reserva'):
        pre_reserva = FichaDeEvento.objects.get(pk=request.POST.get('id_pre_reserva'))

        if request.POST.get('confirmar_agendamento'):
            try:
                pre_reserva.agendado = True
                pre_reserva.data_preenchimento = datetime.today().date()
                pre_reserva.save()
            except Exception as e:
                email_error(request.user.get_full_name(), e, __name__)
                messages.warning(request, f'Pré agendamento não confirmado!')
                messages.error(request, f'{e}')
            else:
                supervisao = Vendedor.objects.filter(supervisor=True)
                lista_emails = [vendedora.usuario.email for vendedora in supervisao]
                EmailSender(lista_emails).mensagem_confirmacao_evento(
                    pre_reserva.check_in, pre_reserva.check_out, pre_reserva.cliente, pre_reserva.vendedora
                )
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

    # Esse if está aqui devido a existência de um bug no envio do formulário todo: Verificar se ainda está com bug!
    if 'exclusividade' in request.POST:
        nova_pre_reserva.exclusividade = True

    if cadastro_de_pre_reservas.is_valid():
        pre_reserva_dcadastrada = cadastro_de_pre_reservas.save()
        Eventos.objects.create(ficha_de_evento=pre_reserva_dcadastrada).save()

        return redirect('calendario_eventos')
    else:
        messages.warning(request, f'{cadastro_de_pre_reservas.errors}')
        return redirect('calendario_eventos')
