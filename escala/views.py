import json
from datetime import datetime, timedelta
from itertools import chain

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect
from ceu.models import Professores
from escala.funcoes import contar_dias, verificar_mes_e_ano, verificar_dias, is_ajax, \
    alterar_dia_limite_peraltas, pegar_clientes_data_selecionada, monitores_disponiveis, escalados_para_o_evento, \
    verificar_escalas, gerar_disponibilidade, teste_monitores_nao_escalados_acampamento, \
    teste_monitores_nao_escalados_hotelaria, verificar_setor_de_disponibilidade, pegar_disponiveis, \
    retornar_dados_grupo, verificar_disponiveis, verificar_disponiveis_grupo, salvar_escala, pegar_escalacoes, \
    pegar_disponiveis_intervalo, procurar_ficha_de_evento
from escala.models import Escala, Disponibilidade, DiaLimite, FormularioEscalaCeu
from ordemDeServico.models import OrdemDeServico
from peraltas.models import DiaLimiteAcampamento, DiaLimiteHotelaria, ClienteColegio, FichaDeEvento, EscalaAcampamento, \
    EscalaHotelaria
from peraltas.models import Monitor, DisponibilidadeAcampamento, DisponibilidadeHotelaria
from projetoCEU.utils import verificar_grupo, email_error


@login_required(login_url='login')
def escala(request):
    escalas = Escala.objects.all()
    edita = request.user.has_perm('escala.add_escala')
    user_logado = request.user.get_full_name()

    # ------------------- Pegar somente professor disponivel no dia selecionado --------------------------
    if is_ajax(request):
        return JsonResponse(verificar_disponiveis(request.GET.get('data_selecionada')))

    if request.method != 'POST':
        return render(request, 'escala/escala.html', {'user_logado': user_logado,
                                                      'escalas': escalas, 'edita': edita})

    # ------------------------ Savando a nova escalaa -------------------------
    equipe = {}
    data_escala = datetime.strptime(request.POST.get('data_escala'), '%Y-%m-%d')

    for i in range(1, 6):
        if i == 1:
            equipe['coordenador'] = int(request.POST.get('coordenador'))
        elif i > 1 and request.POST.get(f'professor_{i}') != '':
            equipe[f'professor_{i}'] = request.POST.get(f'professor_{i}')

    try:
        nova_escala = Escala.objects.create(
            data_escala=data_escala,
            equipe=equipe,
            mes=data_escala.month,
            ano=data_escala.year
        )
        nova_escala.save()
    except Exception as e:
        messages.error(request, f'Houve um erro inesperado: {e}')
        return redirect('escala')
    else:
        return redirect('escala')


@login_required(login_url='login')
def disponibilidade(request):
    dia_limite, p = DiaLimite.objects.get_or_create(id=1, defaults={'dia_limite': 25})

    if request.method != 'POST':
        antes_dia = True if datetime.now().day < dia_limite.dia_limite else False
        coordenador = request.user.has_perm('escala.add_escala')
        professores = Professores.objects.all()

        return render(request, 'escala/disponibilidade.html', {'antes_dia': antes_dia, 'dia_limite': dia_limite,
                                                               'professores': professores, 'coordenador': coordenador})

    if is_ajax(request):
        try:
            dia_limite.dia_limite = request.POST.get('novo_dia')
            dia_limite.save()
        except Exception as e:
            email_error(request.user.get_full_name(), e, __name__)
            return JsonResponse({'tipo': 'error',
                                 'mensagem': 'Houve um erro inesperado, tente novamente mais tarde!'})
        else:
            return JsonResponse({'tipo': 'sucesso',
                                 'mensagem': 'Dia limite alterado com sucesso!'})

    professor = Professores.objects.get(usuario=request.user)

    if request.POST.get('professor') is not None and request.POST.get('professor') != '':
        professor = Professores.objects.get(id=int(request.POST.get('professor')))

    dias = verificar_dias(request.POST.get('datas_disponiveis'), Professores.objects.get(usuario=professor.usuario))

    if dias[0]:
        n_dias = contar_dias(dias[0])
        mes_e_ano_cadastro = verificar_mes_e_ano(dias[0])
    else:
        n_dias = 0
        mes_e_ano_cadastro = verificar_mes_e_ano(dias[1])

    ja_cadastrado = Disponibilidade.objects.filter(professor=professor, mes=mes_e_ano_cadastro[0],
                                                   ano=mes_e_ano_cadastro[1])

    try:
        if ja_cadastrado:
            if dias[0]:
                for cadastro in ja_cadastrado:
                    ja_cadastrado.update(dias_disponiveis=cadastro.dias_disponiveis + ', ' + dias[0],
                                         n_dias=cadastro.n_dias + n_dias)

                    if dias[1]:
                        messages.warning(request, f'dias {dias[1]} não cadastrados por já estar na base de dados"')
                    messages.success(request, 'Disponibilidade atualizada com sucesso')
                    return redirect('dashboard')
            else:
                messages.warning(request, 'Todos os dias selecionados já estão salvos na base de dados!')
                return redirect('dashboard')

        else:
            dias_disponiveis = Disponibilidade(professor=professor, mes=mes_e_ano_cadastro[0],
                                               ano=mes_e_ano_cadastro[1], n_dias=n_dias, dias_disponiveis=dias[0])
            dias_disponiveis.save()
            messages.success(request, 'Disponibilidade salva com sucesso')
            return redirect('dashboard')
    except Exception as e:
        email_error(request.user.get_full_name(), e, __name__)
        messages.error(request, 'Houve um erro inesperado, tente novamente mais tarde!')
        return redirect('dashboard')


@login_required(login_url='login')
def disponibilidadePeraltas(request):
    dia_limite_acampamento, p = DiaLimiteAcampamento.objects.get_or_create(id=1, defaults={'dia_limite_acampamento': 25})
    dia_limite_hotelaria, p = DiaLimiteHotelaria.objects.get_or_create(id=1, defaults={'dia_limite_hotelaria': 25})

    if request.method != "POST":
        antes_dia_limite_acampamento = True if datetime.now().day < dia_limite_acampamento.dia_limite_acampamento else False
        antes_dia_limite_hotelaria = True if datetime.now().day < dia_limite_hotelaria.dia_limite_hotelaria else False

        coordenador_acampamento = request.user.has_perm('peraltas.add_escalaacampamento')
        coordenador_hotelaria = request.user.has_perm('peraltas.add_escalahotelaria')
        monitores = Monitor.objects.all()

        return render(request, 'escala/disponibilidade-peraltas.html', {
            'coordenador_acampamento': coordenador_acampamento,
            'coordenador_hotelaria': coordenador_hotelaria,
            'dia_limite_acampamento': dia_limite_acampamento.dia_limite_acampamento,
            'dia_limite_hotelaria': dia_limite_hotelaria.dia_limite_hotelaria,
            'monitores': monitores,
            'antes_dia_limite_acampamento': antes_dia_limite_acampamento,
            'antes_dia_limite_hotelaria': antes_dia_limite_hotelaria,
        })

    if is_ajax(request):
        if request.POST.get('novo_dia'):
            return JsonResponse(alterar_dia_limite_peraltas(request.POST))

        if request.POST.get('monitor') is not None and request.POST.get('monitor') != '':
            monitor = Monitor.objects.get(id=int(request.POST.get('monitor')))
        else:
            monitor = Monitor.objects.get(usuario=request.user)

        dias = verificar_dias(request.POST.get('datas_disponiveis'),
                              Monitor.objects.get(usuario=monitor.usuario),
                              peraltas=request.POST.get('peraltas'))

        if dias[0]:
            n_dias = contar_dias(dias[0])
            mes_e_ano_cadastro = verificar_mes_e_ano(dias[0])
        else:
            n_dias = 0
            mes_e_ano_cadastro = verificar_mes_e_ano(dias[1])

        if request.POST.get('peraltas') == 'acampamento':
            ja_cadastrado = DisponibilidadeAcampamento.objects.filter(monitor=monitor,
                                                                      mes=mes_e_ano_cadastro[0],
                                                                      ano=mes_e_ano_cadastro[1])
        else:
            ja_cadastrado = DisponibilidadeHotelaria.objects.filter(monitor=monitor,
                                                                    mes=mes_e_ano_cadastro[0],
                                                                    ano=mes_e_ano_cadastro[1])

        try:
            if ja_cadastrado:
                if dias[0]:
                    for cadastro in ja_cadastrado:
                        ja_cadastrado.update(dias_disponiveis=cadastro.dias_disponiveis + ', ' + dias[0],
                                             n_dias=cadastro.n_dias + n_dias)

                        if dias[1]:
                            if dias[2]:
                                msg = f'Dias {dias[1]} não cadastrados, por já estarem na base de dados ou exceder o limite de dias por mês!'
                                return JsonResponse({'tipo': 'sucesso',
                                                     'mensagem': msg})
                            else:
                                msg = f'dias {dias[1]} já estão na base de dados. Disponibilidade atualizada com sucesso'
                                return JsonResponse({'tipo': 'sucesso',
                                                     'mensagem': msg})
                        else:
                            return JsonResponse({'tipo': 'sucesso',
                                                 'mensagem': 'Disponibilidade salva com sucesso!'})
                else:
                    if dias[2]:
                        return JsonResponse({
                            'tipo': 'aviso',
                            'mensagem': 'Todos os dias selecionados já estão salvos na base de dados!'
                        })
                    else:
                        return JsonResponse({
                            'tipo': 'aviso',
                            'mensagem': f'Número máximo de dias já cadastrado na base de dados (22 dias por mês).'
                        })
            else:
                if request.POST.get('peraltas') == 'acampamento':
                    dias_disponiveis = DisponibilidadeAcampamento(
                        monitor=monitor,
                        mes=mes_e_ano_cadastro[0],
                        ano=mes_e_ano_cadastro[1],
                        n_dias=n_dias,
                        dias_disponiveis=dias[0]
                    )
                else:
                    dias_disponiveis = DisponibilidadeHotelaria(
                        monitor=monitor,
                        mes=mes_e_ano_cadastro[0],
                        ano=mes_e_ano_cadastro[1],
                        n_dias=n_dias,
                        dias_disponiveis=dias[0]
                    )

                dias_disponiveis.save()
                return JsonResponse({'tipo': 'sucesso',
                                     'mensagem': 'Disponibilidade salva com sucesso'})
        except Exception as e:
            email_error(request.user.get_full_name(), e, __name__)
            return JsonResponse({'tipo': 'erro',
                                 'mensagem': 'Houve um erro inesperado, tente novamente mais tarde!'})


@login_required(login_url='login')
def verEscalaPeraltas(request):
    escalas_hotelaria = EscalaHotelaria.objects.all()
    escalas_acampamento = EscalaAcampamento.objects.all()
    coordenador_acampamento = request.user.has_perm('peraltas.add_escalaacampamento')
    coordenador_hotelaria = request.user.has_perm('peraltas.add_escalahotelaria')

    if request.method != 'POST':
        return render(request, 'escala/escala_peraltas.html', {'coordenador_acampamento': coordenador_acampamento,
                                                               'coordenador_hotelaria': coordenador_hotelaria,
                                                               'escalas_hotelaria': escalas_hotelaria,
                                                               'escalas_acampamento': escalas_acampamento})

    if is_ajax(request):
        return JsonResponse(escalados_para_o_evento(request.POST))


@login_required(login_url='login')
def escalarMonitores(request, setor, data, id_cliente=None):
    data_selecionada = datetime.strptime(data, '%d-%m-%Y').date()
    clientes_dia = pegar_clientes_data_selecionada(data_selecionada)
    escala_editada = None
    escalado = []
    disponiveis = []

    if request.method != 'POST':
        if setor == 'acampamento':
            if request.GET.get('cliente'):
                cliente = ClienteColegio.objects.get(id=request.GET.get('cliente'))
                inicio_evento = termino_evento = None
                ficha_de_evento,  ordem_de_servico = procurar_ficha_de_evento(cliente, data_selecionada)

                if ordem_de_servico:
                    inicio_evento = ordem_de_servico.check_in
                    termino_evento = ordem_de_servico.check_out
                else:
                    inicio_evento = ficha_de_evento.check_in
                    termino_evento = ficha_de_evento.check_out

                return render(request, 'escala/escalar_monitores.html', {
                    'clientes_dia': clientes_dia,
                    'data': data_selecionada,
                    'setor': setor,
                    'biologo': ficha_de_evento.informacoes_adcionais.biologo,
                    'embarque': ficha_de_evento.informacoes_adcionais.transporte,
                    'enfermaria': ficha_de_evento.informacoes_adcionais.enfermaria,
                    'id_cliente': cliente.id,
                    'inicio': inicio_evento.astimezone().strftime('%Y-%m-%d %H:%M'),
                    'final': termino_evento.astimezone().strftime('%Y-%m-%d %H:%M'),
                    'disponiveis': gerar_disponibilidade(cliente.id, data_selecionada)
                })

            if id_cliente:
                try:
                    escala_editada = EscalaAcampamento.objects.get(
                        cliente__id=int(id_cliente),
                        check_in_cliente__date__lte=data_selecionada,
                        check_out_cliente__date__gte=data_selecionada
                    )
                except EscalaAcampamento.DoesNotExist:
                    ...
                else:
                    escalados = pegar_escalacoes(escala_editada)
                    teste_disponiveis = gerar_disponibilidade(id_cliente, data_selecionada, True)

                    for monitor in teste_disponiveis:
                        tipo_escalacao = []

                        if monitor['id'] in escalados:
                            if monitor['setor'] != 'enfermeira':
                                for teste_monitor in escala_editada.monitores_acampamento.all():
                                    if monitor['id'] == teste_monitor.id:
                                        tipo_escalacao.append(setor)

                                for teste_monitor in escala_editada.monitores_embarque.all():
                                    if monitor['id'] == teste_monitor.id:
                                        tipo_escalacao.append('embarque')
                            else:
                                for teste_monitor in escala_editada.enfermeiras.all():
                                    if monitor['id'] == teste_monitor.id:
                                        tipo_escalacao.append('enfermeira')

                            monitor['tipo_escalacao'] = tipo_escalacao
                            escalado.append(monitor)
                        else:
                            disponiveis.append(monitor)

                check_in = escala_editada.check_in_cliente.astimezone().strftime('%Y-%m-%d %H:%M')
                check_out = escala_editada.check_out_cliente.astimezone().strftime('%Y-%m-%d %H:%M')

                try:
                    ficha_de_evento = FichaDeEvento.objects.get(
                        cliente_id=id_cliente,
                        check_in__date__lte=data_selecionada,
                        check_out__date__gte=data_selecionada,
                    )
                except FichaDeEvento.DoesNotExist:
                    ordem_de_servico = OrdemDeServico.objects.get(
                        ficha_de_evento__cliente__id=id_cliente,
                        check_in__date__lte=data_selecionada,
                        check_out__date__gte=data_selecionada,
                    )

                    ficha_de_evento = ordem_de_servico.ficha_de_evento

                return render(request, 'escala/escalar_monitores.html', {
                    'inicio': check_in,
                    'final': check_out,
                    'id_cliente': id_cliente,
                    'biologo': ficha_de_evento.informacoes_adcionais.biologo,
                    'embarque': ficha_de_evento.informacoes_adcionais.transporte,
                    'enfermaria': ficha_de_evento.informacoes_adcionais.enfermaria,
                    'cliente': escala_editada.cliente.nome_fantasia,
                    'data': data_selecionada,
                    'setor': setor,
                    'disponiveis': disponiveis,
                    'escalados': escalado,
                    'id_escala': escala_editada.id
                })

            return render(request, 'escala/escalar_monitores.html', {
                'clientes_dia': clientes_dia,
                'data': data_selecionada,
                'setor': setor,
            })

        if setor == 'hotelaria':
            disponibilidades_acampamento = DisponibilidadeAcampamento.objects.filter(
                dias_disponiveis__icontains=data_selecionada.strftime('%d/%m/%Y')
            )

            disponibilidades_hotelaria = DisponibilidadeHotelaria.objects.filter(
                dias_disponiveis__icontains=data_selecionada.strftime('%d/%m/%Y')
            )

            disponiveis_bd = list(chain(disponibilidades_acampamento, disponibilidades_hotelaria))

            try:
                escala_hotelaria = EscalaHotelaria.objects.get(data=data_selecionada)
            except EscalaHotelaria.DoesNotExist:
                return render(request, 'escala/escalar_monitores.html', {
                    'data': data_selecionada,
                    'setor': setor,
                    'disponiveis': pegar_disponiveis_intervalo(data_selecionada, data_selecionada, disponiveis_bd)
                })
            except Exception as e:
                email_error(request.user.get_full_name(), e, __name__)
                messages.error(request, 'Ocorreu um erro inesperado, tente novamente mais tarde!')
                return redirect('dashboard')
            else:
                disponiveis_dia = pegar_disponiveis_intervalo(data_selecionada, data_selecionada, disponiveis_bd)

                for monitor_teste in disponiveis_dia:
                    if monitor_teste['id'] in escala_hotelaria.monitores_hotelaria.values():
                        monitor_teste['tipo_escalacao'] = setor
                        escalado.append(monitor_teste)
                    else:
                        disponiveis.append(monitor_teste)

            return render(request, 'escala/escalar_monitores.html', {
                    'data': data_selecionada,
                    'setor': setor,
                    'disponiveis': disponiveis,
                    'escalados': escalado,
                    'id_escala': escala_hotelaria.id
                })

    if is_ajax(request):
        if request.POST.get('id_monitor'):
            return JsonResponse(verificar_escalas(request.POST.get('id_monitor'), data_selecionada,
                                                  request.POST.get('cliente')))

        if request.POST.get('id_cliente'):
            return JsonResponse(gerar_disponibilidade(request.POST.get('id_cliente'), data_selecionada))
    # ----------------------------------------- Salvando as escalas ----------------------------------------------------
    if setor == 'acampamento':
        try:
            cliente = ClienteColegio.objects.get(id=int(request.POST.get('cliente')))
            check_in = datetime.strptime(request.POST.get('check_in'), '%Y-%m-%dT%H:%M')
            check_out = datetime.strptime(request.POST.get('check_out'), '%Y-%m-%dT%H:%M')
            ficha_de_evento, ordem = procurar_ficha_de_evento(cliente, check_in.date())

            if request.POST.get('id_escala') != '':
                editando_escala = EscalaAcampamento.objects.get(id=int(request.POST.get('id_escala')))
                editando_escala.monitores_acampamento.set(request.POST.getlist('id_monitores[]'))
                editando_escala.monitores_embarque.set(request.POST.getlist('id_monitores_embarque[]'))
                editando_escala.enfermeiras.set(request.POST.getlist('id_enfermeiras[]'))
                editando_escala.save()
            else:
                nova_escala = EscalaAcampamento.objects.create(cliente=cliente,
                                                               check_in_cliente=check_in,
                                                               check_out_cliente=check_out)
                nova_escala.monitores_acampamento.set(request.POST.getlist('id_monitores[]'))
                nova_escala.monitores_embarque.set(request.POST.getlist('id_monitores_embarque[]'))
                nova_escala.enfermeiras.set(request.POST.getlist('id_enfermeiras[]'))
                nova_escala.ficha_de_evento = ficha_de_evento
                nova_escala.save()
        except Exception as e:
            email_error(request.user.get_full_name(), e, __name__)
            messages.error(request, 'Houve um erro inesperado, por favor tente mais tarde!')
            return redirect('escalaPeraltas')
        else:
            ficha_de_evento.escala = True
            ficha_de_evento.save()

            if ordem:
                ordem.escala = True
                ordem.save()

            messages.success(request, f'Escala para {cliente.nome_fantasia} salva com sucesso!')
            return HttpResponse()
    else:
        try:
            escala_dia = {}

            for posicao, id_monitor in enumerate(request.POST.getlist('id_monitores[]'), start=1):
                escala_dia[posicao] = int(id_monitor)

            if request.POST.get('id_escala'):
                escala_hotelaria = EscalaHotelaria.objects.get(id=request.POST.get('id_escala'))
                escala_hotelaria.monitores_hotelaria = escala_dia
                escala_hotelaria.save()
            else:
                nova_escala = EscalaHotelaria.objects.create(data=data_selecionada, monitores_hotelaria=escala_dia)
                nova_escala.save()

        except Exception as e:
            email_error(request.user.get_full_name(), e, __name__)
            messages.error(request, 'Houve um erro inesperado, por favor tente mais tarde!')
            return render(request, 'escala/escalar_monitores.html', {
                'clientes_dia': clientes_dia,
                'data': data_selecionada,
                'setor': setor
            })
        else:
            messages.success(
                request, f'Escala para {datetime.strftime(data_selecionada, "%d/%m/%Y")} salva com sucesso!'
            )
            return redirect('escalaPeraltas')


@login_required(login_url='login')
def editarEscalaMonitores(request, cliente, data):
    data_selecionada = datetime.strptime(data, '%d-%m-%Y').date()
    nome_fantasia_cliente = json.dumps(cliente, ensure_ascii=False).replace('"', '')
    cliente_evento = ClienteColegio.objects.get(nome_fantasia=nome_fantasia_cliente)
    ficha_evento_cliete = FichaDeEvento.objects.get(cliente=cliente_evento)
    disponiveis_hotelaria, disponiveis_acampamento = monitores_disponiveis(data_selecionada)
    id_escalados = []

    if ficha_evento_cliete.os:
        ordem_cliente = OrdemDeServico.objects.get(ficha_de_evento__cliente=cliente_evento)
        evento = {'check_in': (ordem_cliente.check_in - timedelta(hours=3)).strftime('%Y-%m-%dT%H:%M'),
                  'check_out': (ordem_cliente.check_out - timedelta(hours=3)).strftime('%Y-%m-%dT%H:%M')}
        escalados = EscalaAcampamento.objects.get(cliente=cliente_evento, check_in_cliente=ordem_cliente.check_in,
                                                  check_out_cliente=ordem_cliente.check_out)
    else:
        evento = {'check_in': (ficha_evento_cliete.check_in - timedelta(hours=3)).strftime('%Y-%m-%dT%H:%M'),
                  'check_out': (ficha_evento_cliete.check_out - timedelta(hours=3)).strftime('%Y-%m-%dT%H:%M')}
        escalados = EscalaAcampamento.objects.get(cliente=cliente_evento, check_in_cliente=ficha_evento_cliete.check_in,
                                                  check_out_cliente=ficha_evento_cliete.check_out)

    restante_acampamento, id_escalados = teste_monitores_nao_escalados_acampamento(disponiveis_acampamento,
                                                                                   escalados, id_escalados)
    restante_hotelaria, id_escalados = teste_monitores_nao_escalados_hotelaria(disponiveis_hotelaria,
                                                                               escalados, id_escalados)
    escalados_evento = verificar_setor_de_disponibilidade(escalados, disponiveis_acampamento, disponiveis_hotelaria)

    if request.method != 'POST':
        return render(request, 'escala/editar_escala_monitoria.html', {'cliente': cliente_evento,
                                                                       'evento': evento,
                                                                       'restante_acampamento': restante_acampamento,
                                                                       'restante_hotelaria': restante_hotelaria,
                                                                       'escalados': escalados_evento,
                                                                       'id_escalados': id_escalados})

    if is_ajax(request):
        return JsonResponse(verificar_escalas(request.POST.get('id_monitor'), data_selecionada,
                                              request.POST.get('cliente')))

    if request.POST.get('acao') == 'Sim':
        ficha_evento_cliete.escala = False
        ficha_evento_cliete.save()

        if ficha_evento_cliete.os:
            ordem_cliente = OrdemDeServico.objects.get(ficha_de_evento__cliente=cliente_evento)
            ordem_cliente.escala = False
            ordem_cliente.save()

        try:
            escalados.delete()
        except Exception as e:
            email_error(request.user.get_full_name(), e, __name__)
            messages.error(request, 'Houve um erro inesperado, por favor tente novamente mais tarde')
            return redirect('escalaPeraltas')
        else:
            messages.success(request, 'Escala excluida com sucesso!')
            return redirect('escalaPeraltas')

    try:
        escalados.monitores_acampamento.clear()
        escalados.monitores_acampamento.set(request.POST.get('monitores_escalados').split(','))
    except Exception as e:
        email_error(request.user.get_full_name(), e, __name__)
        messages.error(request, 'Houve um erro inesperado, por favor tente mais tarde')
        return redirect('escalaPeraltas')
    else:
        messages.success(request, 'Escala atualizada com sucesso')
        return redirect('escalaPeraltas')


@login_required(login_url='login')
def editarEscalaHotelaria(request, data):
    data_selecionada = datetime.strptime(data, '%d-%m-%Y').date()
    disponiveis_hotelaria, disponiveis_acampamento = monitores_disponiveis(data_selecionada)
    escalados = EscalaHotelaria.objects.get(data=data_selecionada)
    id_escalados = []

    restante_acampamento, id_escalados = teste_monitores_nao_escalados_acampamento(disponiveis_acampamento,
                                                                                   escalados, id_escalados)
    restante_hotelaria, id_escalados = teste_monitores_nao_escalados_hotelaria(disponiveis_hotelaria,
                                                                               escalados, id_escalados)
    escalados_para_hoje = verificar_setor_de_disponibilidade(escalados, disponiveis_acampamento, disponiveis_hotelaria)

    if request.method != 'POST':
        return render(request, 'escala/editar_escala_hotelaria.html', {'data': data_selecionada,
                                                                       'escalados': escalados_para_hoje,
                                                                       'id_escalados': id_escalados,
                                                                       'restante_acampamento': restante_acampamento,
                                                                       'restante_hotelaria': restante_hotelaria})

    if is_ajax(request):
        return JsonResponse(verificar_escalas(request.POST.get('id_monitor'), data_selecionada,
                                              request.POST.get('cliente')))

    if request.POST.get('acao') == 'Sim':

        try:
            escalados.delete()
        except Exception as e:
            email_error(request.user.get_full_name(), e, __name__)
            messages.error(request, 'Houve um erro inesperado, por favor tente novamente mais tarde')
            return redirect('escalaPeraltas')
        else:
            messages.success(request, 'Escala excluida com sucesso!')
            return redirect('escalaPeraltas')

    try:
        escalados.monitores_hotelaria.clear()
        escalados.monitores_hotelaria.set(request.POST.get('monitores_escalados').split(','))
    except Exception as e:
        email_error(request.user.get_full_name(), e, __name__)
        messages.error(request, 'Houve um erro inesperado, tente novamente mais tarde!')
        return redirect('escapaPeraltas')
    else:
        messages.success(request, 'Escala atualizada com sucesso!')
        return redirect('escalaPeraltas')


@login_required(login_url='login')
def visualizarDisponibilidadePeraltas(request):
    coordenador_acampamento = request.user.has_perm('peraltas.add_escalaacampamento')
    coordenador_hotelaria = request.user.has_perm('peraltas.add_escalahotelaria')

    if coordenador_hotelaria or coordenador_acampamento:
        disponibilidades_hotelaria = DisponibilidadeHotelaria.objects.all()
        disponibilidades_acampamento = DisponibilidadeAcampamento.objects.all()
        eventos_ordem_de_servico = OrdemDeServico.objects.all()
        fichas_de_evento = FichaDeEvento.objects.filter(os=False)

        for evento in eventos_ordem_de_servico:
            evento.check_out += timedelta(days=1)

        for ficha in fichas_de_evento:
            ficha.check_out += timedelta(days=1)
    else:
        eventos_ordem_de_servico = fichas_de_evento = None
        disponibilidades_hotelaria = DisponibilidadeHotelaria.objects.filter(monitor__usuario=request.user)
        disponibilidades_acampamento = DisponibilidadeAcampamento.objects.filter(monitor__usuario=request.user)

    disponiveis_hotelaria = pegar_disponiveis(disponibilidades_hotelaria, 'hotelaria')
    disponiveis_acampamento = pegar_disponiveis(disponibilidades_acampamento, 'acampamento')

    return render(request, 'escala/calendario_disponibilidade_peraltas.html',
                  {'disponiveis_hotelaria': disponiveis_hotelaria,
                   'disponiveis_acampamento': disponiveis_acampamento,
                   'eventos': eventos_ordem_de_servico,
                   'fichas_de_evento': fichas_de_evento,
                   'coordenador_hotelaria': coordenador_hotelaria,
                   'coordenador_acampamento': coordenador_acampamento})


@login_required(login_url='login')
def visualizarDisponibilidadeCeu(request):
    disponiveis_ceu = Disponibilidade.objects.all()
    eventos = OrdemDeServico.objects.all()

    for evento in eventos:
        if evento.atividades_ceu:
            evento.check_out_ceu += timedelta(days=1)

    disponiveis = pegar_disponiveis(disponiveis_ceu, 'ceu')

    return render(request, 'escala/calendario_disponibilidade_ceu.html', {'disponiveis': disponiveis,
                                                                          'eventos': eventos})
