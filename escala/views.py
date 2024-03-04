from datetime import datetime, timedelta
from itertools import chain

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Q
from django.http import JsonResponse, HttpResponse, FileResponse
from django.shortcuts import render, redirect
from ceu.models import Professores
from escala.funcoes import contar_dias, verificar_mes_e_ano, verificar_dias, is_ajax, \
    pegar_clientes_data_selecionada, escalados_para_o_evento, \
    verificar_escalas, gerar_disponibilidade, pegar_disponiveis, \
    verificar_disponiveis, pegar_escalacoes, \
    pegar_disponiveis_intervalo, procurar_ficha_de_evento, transformar_disponibilidades, adicionar_dia, remover_dia, \
    pegar_dados_monitor_embarque, pegar_dados_monitor_biologo, salvar_ultima_pre_escala, juntar_emails_monitores
from escala.models import Escala, Disponibilidade, DiaLimite
from ordemDeServico.models import OrdemDeServico
from peraltas.models import DiaLimitePeraltas, ClienteColegio, FichaDeEvento, EscalaAcampamento, EscalaHotelaria, \
    Enfermeira
from peraltas.models import Monitor, DisponibilidadePeraltas
from projetoCEU import gerar_pdf
from projetoCEU.envio_de_emails import EmailSender
from projetoCEU.utils import email_error


@login_required(login_url='login')
def escala(request):
    escalas = Escala.objects.all()
    edita = request.user.has_perm('escala.add_escala')
    user_logado = request.user.get_full_name()

    # ------------------- Pegar somente professor disponivel no dia selecionado --------------------------
    if is_ajax(request):
        return JsonResponse(verificar_disponiveis(request.GET.get('data_selecionada')))

    if request.method != 'POST':
        return render(request, 'escala/escala.html', {
            'user_logado': user_logado,
            'escalas': escalas,
            'edita': edita
        })

    # ------------------------ Savando a nova escalaa -------------------------
    equipe = list(int(id_professor) for id_professor in request.POST.getlist('escalados') if id_professor != '')
    data_escala = datetime.strptime(request.POST.get('data_escala'), '%Y-%m-%d')

    try:
        if Escala.objects.filter(data_escala=data_escala).exists():
            escala_professores = Escala.objects.get(data_escala=data_escala)
            escala_professores.equipe = equipe
        else:
            escala_professores = Escala.objects.create(
                data_escala=data_escala,
                equipe=equipe,
                mes=data_escala.month,
                ano=data_escala.year
            )

        escala_professores.save()
    except Exception as e:
        messages.error(request, f'Houve um erro inesperado: {e}')

        return redirect('escala')
    else:
        messages.success(request, 'Escala salva com sucesso')

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
    monitores = enfermeiras = None

    if is_ajax(request):
        if request.method == 'GET':
            data_enviada = datetime.strptime(request.GET.get('data'), '%Y-%m-%d')
            hospedagem = FichaDeEvento.objects.filter(produto__brotas_eco=True).filter(
                check_in__date__lte=data_enviada,
                check_out__date__gte=data_enviada,
            )

            return JsonResponse({'hospedagem': len(hospedagem) > 0})

        monitor = Monitor.objects.get(pk=request.POST.get('id_monitor')) if request.POST.get('id_monitor') else None
        enfermeira = Enfermeira.objects.get(pk=request.POST.get('id_enfermeira')) if request.POST.get(
            'id_enfermeira') else None
        removido = request.POST.get('dia_removido', None)
        adicionado = request.POST.get('dia_adicionado', None)
        dia_adicionado = datetime.strptime(adicionado, '%Y-%m-%d') if adicionado is not None else None
        dia_removido = datetime.strptime(removido, '%Y-%m-%d') if removido is not None else None

        if request.POST.get('adicionar_dia'):
            adicionado = adicionar_dia(monitor, dia_adicionado, enfermeira)

            return HttpResponse(adicionado)

        if request.POST.get('alterar_dia'):
            remover_dia(monitor, dia_removido, enfermeira)
            adicionar_dia(monitor, dia_adicionado, enfermeira)

            return HttpResponse()

        if request.POST.get('remover_disponibilidade'):
            remover_dia(monitor, dia_removido, enfermeira)

            return HttpResponse()

    if request.method != "POST":
        coordenador_acampamento = request.user.has_perm('peraltas.add_escalaacampamento')
        coordenador_hotelaria = request.user.has_perm('peraltas.add_escalahotelaria')

        if coordenador_acampamento or coordenador_hotelaria:
            monitores = Monitor.objects.all().order_by('usuario__first_name')
            enfermeiras = Enfermeira.objects.all().order_by('usuario__first_name')
            disponibilidades = DisponibilidadePeraltas.objects.all()
        else:
            try:
                monitores = Monitor.objects.get(usuario=request.user)
            except Monitor.DoesNotExist:
                enfermeiras = Enfermeira.objects.get(usuario=request.user)
                disponibilidades = DisponibilidadePeraltas.objects.filter(enfermeira=enfermeiras)
            else:
                disponibilidades = DisponibilidadePeraltas.objects.filter(monitor=monitores)

        disponibilidades_peraltas = transformar_disponibilidades(disponibilidades,
                                                                 coordenador_hotelaria or coordenador_acampamento)

        return render(request, 'escala/disponibilidade-peraltas.html', {
            'coordenador_acampamento': coordenador_acampamento,
            'coordenador_hotelaria': coordenador_hotelaria,
            'disponibilidades_peraltas': disponibilidades_peraltas,
            'monitores': monitores,
            'enfermeiras': enfermeiras,
        })


@login_required(login_url='login')
def verEscalaPeraltas(request):
    coordenador_acampamento = request.user.has_perm('peraltas.add_escalaacampamento')
    coordenador_hotelaria = request.user.has_perm('peraltas.add_escalahotelaria')
    diretoria = User.objects.filter(pk=request.user.id, groups__name='Diretoria').exists()

    if request.GET.get('setor'):
        if request.GET.get('setor') == 'acampamento':
            setor = 'acampamento'
            escalas_acampamento = EscalaAcampamento.objects.all()
            escalas_hotelaria = None
        else:
            setor = 'hotelaria'
            escalas_acampamento = None
            escalas_hotelaria = EscalaHotelaria.objects.all()
    else:
        if coordenador_acampamento:
            setor = 'acampamento'
            escalas_acampamento = EscalaAcampamento.objects.all()
            escalas_hotelaria = None
        elif coordenador_hotelaria:
            setor = 'hotelaria'
            escalas_hotelaria = EscalaHotelaria.objects.all()
            escalas_acampamento = None
        else:
            setor = None
            escalas_hotelaria = EscalaHotelaria.objects.filter(monitores_escalados__usuario=request.user)

            escalas_acampamento_acampamento = EscalaAcampamento.objects.filter(
                monitores_acampamento__usuario=request.user
            )

            escalas_acampamento_embarque = EscalaAcampamento.objects.filter(
                monitores_embarque__usuario=request.user
            ).exclude(id__in=escalas_acampamento_acampamento)

            escalas_acampamento_tecnico = EscalaAcampamento.objects.filter(
                tecnicos__usuario=request.user
            ).exclude(id__in=escalas_acampamento_acampamento).exclude(id__in=escalas_acampamento_embarque)

            escalas_acampamento_enfermeira = EscalaAcampamento.objects.filter(enfermeiras__usuario=request.user)

            escalas_acampamento = list(chain(
                escalas_acampamento_acampamento,
                escalas_acampamento_embarque,
                escalas_acampamento_enfermeira,
                escalas_acampamento_tecnico
            ))

    if request.method != 'POST':
        if request.GET.get('gerar_pdf'):
            escala_acampamento = EscalaAcampamento.objects.get(pk=request.GET.get('id_escala'))
            gerar_pdf.dados_monitores(escala_acampamento)

            return FileResponse(
                open('temp/dados_monitores_escalados.pdf', 'rb'),
                content_type='application/pdf',
                as_attachment=True,
                filename=f'Dados monitores escalados.pdf'
            )

        if is_ajax(request):
            data = datetime.strptime(request.GET.get('data_escala'), '%Y-%m-%d')
            hotelaria = FichaDeEvento.objects.filter(produto__brotas_eco=True).filter(
                check_in__date__lte=data,
                check_out__date__gte=data,
            )

            return JsonResponse({'hotelaria': len(hotelaria) > 0})

        return render(request, 'escala/escala_peraltas.html', {
            'coordenador_acampamento': coordenador_acampamento,
            'coordenador_hotelaria': coordenador_hotelaria,
            'diretoria': diretoria,
            'escalas_hotelaria': escalas_hotelaria,
            'escalas_acampamento': escalas_acampamento,
            'setor': setor,
        })

    if is_ajax(request):
        return JsonResponse(escalados_para_o_evento(request.POST))

    if request.POST.get('id_escala'):
        escala_acampamento = EscalaAcampamento.objects.get(pk=request.POST.get('id_escala'))
        ficha = escala_acampamento.ficha_de_evento

        try:
            ordem = OrdemDeServico.objects.get(ficha_de_evento=escala_acampamento.ficha_de_evento)
        except OrdemDeServico.DoesNotExist:
            ordem = None

        if request.POST.get('escala_final'):
            try:
                escala_acampamento.pre_escala = False
                escala_acampamento.ultima_pre_escala = salvar_ultima_pre_escala(
                    None,
                    dados_escala_confirmada=escala_acampamento
                )
                escala_acampamento.save()
            except Exception as e:
                messages.error(request, f'Houve um erro inesperado: {e}.')
                return render(request, 'escala/escala_peraltas.html', {
                    'coordenador_acampamento': coordenador_acampamento,
                    'coordenador_hotelaria': coordenador_hotelaria,
                    'diretoria': diretoria,
                    'escalas_hotelaria': escalas_hotelaria,
                    'escalas_acampamento': escalas_acampamento,
                    'setor': setor,
                })
            else:
                ficha_de_evento = escala_acampamento.ficha_de_evento
                operacional = User.objects.filter(groups__name='Operacional')
                lista_emails = set()

                for colaborador in operacional:
                    lista_emails.add(colaborador.email)

                EmailSender(juntar_emails_monitores(escala_acampamento)).mensagem_cadastro_escala(ficha_de_evento)
                EmailSender(lista_emails).mensagem_cadastro_escala_operacional(ficha_de_evento, escala_acampamento)

                messages.success(request, 'Escala salva com sucesso!')
                return redirect('escalaPeraltas')

        try:
            escala_acampamento.delete()
        except Exception as e:
            messages.error(request, f'Houve um erro inesperado: {e}.')
            return render(request, 'escala/escala_peraltas.html', {
                'coordenador_acampamento': coordenador_acampamento,
                'coordenador_hotelaria': coordenador_hotelaria,
                'diretoria': diretoria,
                'escalas_hotelaria': escalas_hotelaria,
                'escalas_acampamento': escalas_acampamento,
                'setor': setor,
            })
        else:
            ficha.escala = False
            ficha.save()

            if ordem:
                ordem.escala = False
                ordem.save()

            messages.success(request, 'Escala excluída com sucesso!')
            return redirect('escalaPeraltas')


@login_required(login_url='login')
def escalarMonitores(request, setor, data, id_cliente=None):
    data_selecionada = datetime.strptime(data, '%Y-%m-%d').date()
    clientes_dia = pegar_clientes_data_selecionada(data_selecionada)
    diretoria = User.objects.filter(pk=request.user.id, groups__name='Diretoria').exists()
    escala_editada = None
    escalado = []
    disponiveis = []

    if is_ajax(request):
        if request.POST.get('id_monitor'):
            return JsonResponse(verificar_escalas(request.POST.get('id_monitor'), data_selecionada,
                                                  request.POST.get('cliente')))

        if request.POST.get('id_cliente'):
            return JsonResponse(gerar_disponibilidade(request.POST.get('id_cliente'), data_selecionada))

    if request.GET.get('gerar_pdf'):
        print(setor == 'acampamento')
        if setor == 'acampamento':
            escala_acampamento = EscalaAcampamento.objects.get(pk=request.GET.get('id_escala'))
            gerar_pdf.dados_monitores(escala_acampamento)

        if setor == 'hotelaria':
            escala_hotelaria = EscalaHotelaria.objects.get(pk=request.GET.get('id_escala'))
            gerar_pdf.dados_monitores_hotelaria(escala_hotelaria)

        return FileResponse(
            open('temp/dados_monitores_escalados.pdf', 'rb'),
            content_type='application/pdf',
            as_attachment=True,
            filename=f'Dados monitores escalados.pdf'
        )

    if request.method != 'POST':
        if setor == 'acampamento':
            if request.GET.get('cliente'):
                cliente = ClienteColegio.objects.get(id=request.GET.get('cliente'))
                inicio_evento = termino_evento = None
                ficha_de_evento, ordem_de_servico = procurar_ficha_de_evento(cliente, data_selecionada)

                if ordem_de_servico:
                    qtd_pagantes = ordem_de_servico.n_participantes
                else:
                    qtd_pagantes = ficha_de_evento.qtd_confirmada if ficha_de_evento.qtd_confirmada else 0

                if ordem_de_servico:
                    areas = []
                    inicio_evento = ordem_de_servico.check_in
                    termino_evento = ordem_de_servico.check_out
                    n_monitores = int(ordem_de_servico.n_participantes / 10)
                    # n_coordenadores =
                    monitores_embarque = pegar_dados_monitor_embarque(ordem_de_servico) if ordem_de_servico else None
                    monitores_biologo = pegar_dados_monitor_biologo(ordem_de_servico) if ordem_de_servico else None
                else:
                    inicio_evento = ficha_de_evento.check_in
                    termino_evento = ficha_de_evento.check_out
                    n_monitores = int(ficha_de_evento.qtd_convidada / 10)
                    # n_coordenadores =
                    monitores_embarque = monitores_biologo = None

                return render(request, 'escala/escalar_monitores.html', {
                    'clientes_dia': clientes_dia,
                    'diretoria': diretoria,
                    'data': data_selecionada.strftime('%d-%m-%Y'),
                    'setor': setor,
                    'biologo': ordem_de_servico.atividade_biologo if ordem_de_servico else False,
                    'qtd': ficha_de_evento.qtd_convidada,
                    'qtd_pagantes': qtd_pagantes,
                    'ficha_de_evento': ficha_de_evento,
                    'os': ordem_de_servico,
                    'monitores_embarque': monitores_embarque,
                    'monitores_biologo': monitores_biologo,
                    'enfermaria': ficha_de_evento.informacoes_adcionais.enfermaria,
                    'id_cliente': cliente.id,
                    'inicio': inicio_evento.astimezone().strftime('%Y-%m-%d %H:%M'),
                    'final': termino_evento.astimezone().strftime('%Y-%m-%d %H:%M'),
                    'disponiveis': gerar_disponibilidade(cliente.id, data_selecionada),
                    'n_monitores': n_monitores if n_monitores != 0 else 1,
                    # 'n_coordenadores': 1 if ordem_de_servico
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

                        if monitor['setor'] != 'enfermeira':
                            if monitor['id'] in escalados:
                                if Monitor.objects.get(pk=monitor['id']) in escala_editada.monitores_acampamento.all():
                                    tipo_escalacao.append(setor)

                                if Monitor.objects.get(pk=monitor['id']) in escala_editada.monitores_embarque.all():
                                    tipo_escalacao.append('embarque')

                                if Monitor.objects.get(pk=monitor['id']) in escala_editada.biologos.all():
                                    tipo_escalacao.append('biologo')

                                if Monitor.objects.get(pk=monitor['id']) in escala_editada.tecnicos.all():
                                    tipo_escalacao.append('tecnico')
                            else:
                                disponiveis.append(monitor)
                        else:
                            if Enfermeira.objects.get(pk=monitor['id']) in escala_editada.enfermeiras.all():
                                tipo_escalacao.append('enfermeira')
                            else:
                                disponiveis.append(monitor)

                        monitor['tipo_escalacao'] = tipo_escalacao
                        escalado.append(monitor)

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
                    n_monitores = int(ordem_de_servico.n_participantes / escala_editada.racional_monitores)
                else:
                    try:
                        ordem_de_servico = OrdemDeServico.objects.get(ficha_de_evento=ficha_de_evento)
                        n_monitores = int(ordem_de_servico.n_participantes / escala_editada.racional_monitores)
                    except OrdemDeServico.DoesNotExist:
                        ordem_de_servico = None
                        n_monitores = int(ficha_de_evento.qtd_convidada / escala_editada.racional_monitores)

                return render(request, 'escala/escalar_monitores.html', {
                    'inicio': check_in,
                    'diretoria': diretoria,
                    'final': check_out,
                    'id_cliente': id_cliente,
                    'biologo': ordem_de_servico.atividade_biologo if ordem_de_servico else False,
                    'qtd': ordem_de_servico.n_participantes if ordem_de_servico else ficha_de_evento.qtd_convidada,
                    'ficha_de_evento': ficha_de_evento,
                    'os': ordem_de_servico,
                    'embarque': ficha_de_evento.informacoes_adcionais.transporte,
                    'enfermaria': ficha_de_evento.informacoes_adcionais.enfermaria,
                    'cliente': escala_editada.cliente.nome_fantasia,
                    'data': data_selecionada,
                    'setor': setor,
                    'disponiveis': disponiveis,
                    'escalados': escalado,
                    'id_escala': escala_editada.id,
                    'observacoes': escala_editada.observacoes,
                    'pre_escala': escala_editada.pre_escala,
                    'n_monitores': n_monitores if n_monitores != 0 else 1,
                })

            return render(request, 'escala/escalar_monitores.html', {
                'clientes_dia': clientes_dia,
                'data': data_selecionada,
                'setor': setor,
            })

        if setor == 'hotelaria':
            disponibilidades_peraltas = DisponibilidadePeraltas.objects.filter(
                dias_disponiveis__icontains=data_selecionada.strftime('%d/%m/%Y')
            )

            try:
                escala_hotelaria = EscalaHotelaria.objects.get(data=data_selecionada)
            except EscalaHotelaria.DoesNotExist:
                return render(request, 'escala/escalar_monitores.html', {
                    'data': data_selecionada,
                    'diretoria': diretoria,
                    'setor': setor,
                    'disponiveis': pegar_disponiveis_intervalo(
                        data_selecionada,
                        data_selecionada,
                        disponibilidades_peraltas
                    )
                })
            except Exception as e:
                email_error(request.user.get_full_name(), e, __name__)
                messages.error(request, 'Ocorreu um erro inesperado, tente novamente mais tarde!')
                return redirect('dashboard')
            else:
                disponiveis_dia = pegar_disponiveis_intervalo(
                    data_selecionada,
                    data_selecionada,
                    disponibilidades_peraltas
                )

                for monitor_teste in disponiveis_dia:
                    if monitor_teste['setor'] != 'enfermeira':
                        if Monitor.objects.get(pk=monitor_teste['id']) in escala_hotelaria.monitores_escalados.all():
                            monitor_teste['tipo_escalacao'] = setor
                            escalado.append(monitor_teste)
                        elif Monitor.objects.get(pk=monitor_teste['id']) in escala_hotelaria.coordenadores.all():
                            monitor_teste['tipo_escalacao'] = 'coordenadores'
                            escalado.append(monitor_teste)
                        elif Monitor.objects.get(pk=monitor_teste['id']) in escala_hotelaria.tecnicos_hotelaria.all():
                            monitor_teste['tipo_escalacao'] = 'tecnico'
                            escalado.append(monitor_teste)
                        else:
                            disponiveis.append(monitor_teste)

            return render(request, 'escala/escalar_monitores.html', {
                'data': data_selecionada,
                'diretoria': diretoria,
                'setor': setor,
                'disponiveis': disponiveis,
                'escalados': escalado,
                'pre_escala': escala_hotelaria.pre_escala,
                'id_escala': escala_hotelaria.id,
            })
    # ----------------------------------------- Salvando as escalas ----------------------------------------------------
    if setor == 'acampamento':
        editando_escala = nova_escala = None

        try:
            cliente = ClienteColegio.objects.get(id=int(request.POST.get('cliente')))
            check_in = datetime.strptime(request.POST.get('check_in'), '%Y-%m-%dT%H:%M')
            check_out = datetime.strptime(request.POST.get('check_out'), '%Y-%m-%dT%H:%M')
            ficha_de_evento, ordem = procurar_ficha_de_evento(cliente, check_in.date())

            if request.POST.get('id_escala') != '':
                editando_escala = EscalaAcampamento.objects.get(id=int(request.POST.get('id_escala')))
                editando_escala.monitores_acampamento.set(request.POST.getlist('id_monitores[]'))
                editando_escala.monitores_embarque.set(request.POST.getlist('id_monitores_embarque[]'))
                editando_escala.biologos.set(request.POST.getlist('id_biologos[]'))
                editando_escala.enfermeiras.set(request.POST.getlist('id_enfermeiras[]'))
                editando_escala.tecnicos.set(request.POST.getlist('id_tecnicos[]'))
                editando_escala.pre_escala = request.POST.get('pre_escala') == 'true'
                editando_escala.observacoes = request.POST.get('observacoes')

                if request.POST.get('pre_escala') == 'false' and not editando_escala.ultima_pre_escala:
                    editando_escala.ultima_pre_escala = salvar_ultima_pre_escala(request.POST)

                editando_escala.save()
            else:
                nova_escala = EscalaAcampamento.objects.create(
                    cliente=cliente,
                    check_in_cliente=check_in,
                    check_out_cliente=check_out
                )
                nova_escala.monitores_acampamento.set(request.POST.getlist('id_monitores[]'))
                nova_escala.monitores_embarque.set(request.POST.getlist('id_monitores_embarque[]'))
                nova_escala.biologos.set(request.POST.getlist('id_biologos[]'))
                nova_escala.enfermeiras.set(request.POST.getlist('id_enfermeiras[]'))
                nova_escala.tecnicos.set(request.POST.getlist('id_tecnicos[]'))
                nova_escala.ficha_de_evento = ficha_de_evento
                nova_escala.observacoes = request.POST.get('observacoes')

                if request.POST.get('pre_escala') == 'false':
                    nova_escala.ultima_pre_escala = salvar_ultima_pre_escala(request.POST)

                nova_escala.pre_escala = request.POST.get('pre_escala') == 'true'
                nova_escala.save()
        except Exception as e:
            print(e, 'ue')
            messages.error(request, f'Houve um erro inesperado ({e}), por favor tente mais tarde!')
            return redirect('escalaPeraltas')
        else:
            ficha_de_evento.escala = True
            ficha_de_evento.save()
            escala_salva = nova_escala if nova_escala else editando_escala

            if ordem:
                ordem.escala = True
                ordem.save()

            if escala_salva.pre_escala:
                EmailSender(
                    juntar_emails_monitores(escala_salva)
                ).mensagem_pre_escala_monitoria(ficha_de_evento)
            else:
                operacional = User.objects.filter(groups__name='Operacional')
                lista_emails = set()

                for colaborador in operacional:
                    lista_emails.add(colaborador.email)

                EmailSender(juntar_emails_monitores(escala_salva)).mensagem_cadastro_escala(ficha_de_evento)
                EmailSender(lista_emails).mensagem_cadastro_escala_operacional(ficha_de_evento, escala_salva)
            print('FOi')
            messages.success(request, f'Escala para {cliente.nome_fantasia} salva com sucesso!')
            return redirect('dashboard')
    else:
        try:
            escala_dia = {}
            segundo_incio = len(request.POST.getlist('id_coordenadores[]', [1]))

            for posicao, id_monitor in enumerate(request.POST.getlist('id_coordenadores[]'), start=1):
                escala_dia[posicao] = int(id_monitor)

            for posicao, id_monitor in enumerate(request.POST.getlist('id_monitores[]'), start=segundo_incio + 1):
                escala_dia[posicao] = int(id_monitor)

            if request.POST.get('id_escala'):
                escala_hotelaria = EscalaHotelaria.objects.get(id=request.POST.get('id_escala'))
                escala_hotelaria.monitores_hotelaria = escala_dia
                escala_hotelaria.monitores_escalados.set(list(map(int, request.POST.getlist('id_monitores[]'))))
                escala_hotelaria.coordenadores.set(list(map(int, request.POST.getlist('id_coordenadores[]'))))
                escala_hotelaria.tecnicos_hotelaria.set(list(map(int, request.POST.getlist('id_tecnicos[]'))))

                if request.POST.get('pre_escala') == 'false' and not escala_hotelaria.ultima_pre_escala:
                    escala_hotelaria.ultima_pre_escala = salvar_ultima_pre_escala(request.POST)

                escala_hotelaria.pre_escala = request.POST.get('pre_escala') == 'true'
                escala_hotelaria.save()
            else:
                nova_escala = EscalaHotelaria.objects.create(data=data_selecionada, monitores_hotelaria=escala_dia)
                nova_escala.monitores_escalados.set(list(map(int, request.POST.getlist('id_monitores[]'))))
                nova_escala.coordenadores.set(list(map(int, request.POST.getlist('id_coordenadores[]'))))
                nova_escala.tecnicos_hotelaria.set(list(map(int, request.POST.getlist('id_tecnicos[]'))))

                if request.POST.get('pre_escala') == 'false':
                    nova_escala.ultima_pre_escala = salvar_ultima_pre_escala(request.POST)

                nova_escala.pre_escala = request.POST.get('pre_escala', 'true') == 'true'
                nova_escala.save()
        except Exception as e:
            print(e)
            messages.error(request, f'Houve um erro inesperado, ({e}) por favor tente mais tarde!')
            return redirect('dashboard')
        else:
            print('Ué')
            messages.success(
                request, f'Escala para {datetime.strftime(data_selecionada, "%d/%m/%Y")} salva com sucesso!'
            )
            return redirect('dashboard')


@login_required(login_url='login')
def visualizarDisponibilidadePeraltas(request):
    disponibilidades = DisponibilidadePeraltas.objects.all()
    disponiveis_peraltas = pegar_disponiveis(disponibilidades, 'peraltas')
    coordenador_hotelaria = request.user.has_perm('peraltas.add_escalahotelaria')
    coordenador_acampamento = request.user.has_perm('peraltas.add_escalaacampamento')

    if is_ajax(request):
        data = datetime.strptime(request.GET.get('data_escala'), '%Y-%m-%d')
        hotelaria = FichaDeEvento.objects.filter(produto__brotas_eco=True).filter(
            check_in__date__lte=data,
            check_out__date__gte=data,
        )

        return JsonResponse({'hotelaria': len(hotelaria) > 0})

    if request.GET.get('setor'):
        if request.GET.get('setor') == 'acampamento':
            eventos_ordem_de_servico = OrdemDeServico.objects.all()
            fichas_de_evento = FichaDeEvento.objects.filter(os=False, pre_reserva=False)
            eventos_hospedagem = None
            setor = 'acampamento'

            for evento in eventos_ordem_de_servico:
                evento.check_out += timedelta(days=1)

            for ficha in fichas_de_evento:
                ficha.check_out += timedelta(days=1)
        else:
            eventos_ordem_de_servico = fichas_de_evento = None
            eventos_hospedagem = FichaDeEvento.objects.filter(produto__brotas_eco=True)
            setor = 'hotelaria'

            for evento in eventos_hospedagem:
                evento.check_out += timedelta(days=1)
    else:
        if coordenador_acampamento:
            eventos_ordem_de_servico = OrdemDeServico.objects.all()
            fichas_de_evento = FichaDeEvento.objects.filter(os=False, pre_reserva=False)
            eventos_hospedagem = None
            setor = 'acampamento'

            for evento in eventos_ordem_de_servico:
                evento.check_out += timedelta(days=1)

            for ficha in fichas_de_evento:
                ficha.check_out += timedelta(days=1)
        else:
            eventos_ordem_de_servico = fichas_de_evento = None
            eventos_hospedagem = FichaDeEvento.objects.filter(produto__brotas_eco=True)
            setor = 'hotelaria'

            for evento in eventos_hospedagem:
                evento.check_out += timedelta(days=1)

    return render(request, 'escala/calendario_disponibilidade_peraltas.html', {
        'disponiveis_peraltas': disponiveis_peraltas,
        'eventos': eventos_ordem_de_servico,
        'fichas_de_evento': fichas_de_evento,
        'hopedagem': eventos_hospedagem,
        'setor': setor,
        'coordenador_hotelaria': coordenador_hotelaria,
        'coordenador_acampamento': coordenador_acampamento,
    })


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
