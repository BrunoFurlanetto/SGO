import json
from datetime import datetime, timezone, timedelta
from itertools import chain

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from ceu.models import Professores
from escala.funcoes import escalar, contar_dias, verificar_mes_e_ano, verificar_dias, is_ajax, \
    alterar_dia_limite_peraltas, pegar_clientes_data_selecionada, monitores_disponiveis, escalados_para_o_evento, \
    verificar_escalas, gerar_disponibilidade, teste_monitores_nao_escalados_acampamento, \
    teste_monitores_nao_escalados_hotelaria, verificar_setor_de_disponibilidade, pegar_disponiveis, \
    retornar_dados_grupo, verificar_disponiveis, verificar_disponiveis_grupo
from escala.models import Escala, Disponibilidade, DiaLimite, FormularioEscalaCeu
from ordemDeServico.models import OrdemDeServico
from peraltas.models import DiaLimiteAcampamento, DiaLimiteHotelaria, ClienteColegio, FichaDeEvento, EscalaAcampamento, \
    EscalaHotelaria
from peraltas.models import Monitor, DisponibilidadeAcampamento, DisponibilidadeHotelaria
from projetoCEU.utils import verificar_grupo, email_error


@login_required(login_url='login')
def escala(request):
    escalas = Escala.objects.all()
    ver_icons = User.objects.filter(pk=request.user.id, groups__name='Colégio').exists()
    edita = User.objects.filter(pk=request.user.id, groups__name='Coordenador pedagógico').exists()
    grupos = verificar_grupo(request.user.groups.all())
    user_logado = request.user.get_full_name()

    if request.method != 'POST':
        return render(request, 'escala/escala.html', {'user_logado': user_logado,
                                                      'escalas': escalas,
                                                      'ver': ver_icons, 'edita': edita,
                                                      'grupos': grupos})

    # ------------------- Pegar somente professor disponivel no dia selecionado --------------------------
    if is_ajax(request) and request.method == 'POST':
        atividades_grupo = []
        locacoes_grupo = []
        escala_grupo = Escala.objects.get(cliente__nome_fantasia=request.POST.get('grupo'),
                                          check_in_grupo=request.POST.get('check_in'),
                                          check_out_grupo=request.POST.get('check_out'))

        ordem_grupo = OrdemDeServico.objects.get(escala_ceu=True,
                                                 instituicao=request.POST.get('grupo'),
                                                 check_in_ceu=request.POST.get('check_in'),
                                                 check_out_ceu=request.POST.get('check_out'))

        if ordem_grupo.atividades_ceu:
            for atividade in ordem_grupo.atividades_ceu:

                if ordem_grupo.atividades_ceu[atividade]['atividade'] not in atividades_grupo:
                    atividades_grupo.append(ordem_grupo.atividades_ceu[atividade]['atividade'])
        else:
            for espaco in ordem_grupo.locacao_ceu:

                if ordem_grupo.locacao_ceu[espaco]['espaco'] not in locacoes_grupo:
                    locacoes_grupo.append(ordem_grupo.locacao_ceu[espaco]['espaco'])

        return JsonResponse({'escalados': escala_grupo.separar_equipe(), 'atividades': atividades_grupo,
                             'locacoes': locacoes_grupo})


@login_required(login_url='login')
def disponibilidade(request):
    dia_limite = DiaLimite.objects.get(id=1)
    grupos = verificar_grupo(request.user.groups.all())

    if request.method != 'POST':
        antes_dia = True if datetime.now().day < dia_limite.dia_limite else False
        coordenador = User.objects.filter(pk=request.user.id, groups__name='Coordenador pedagógico').exists()
        professores = Professores.objects.all()

        return render(request, 'escala/disponibilidade.html', {'antes_dia': antes_dia, 'dia_limite': dia_limite,
                                                               'professores': professores, 'coordenador': coordenador,
                                                               'grupos': grupos})

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

    professor = Professores.objects.get(usuario__first_name=request.user.first_name)

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
def MontarEscalaCeu(request, data_enviada=None):
    grupos = verificar_grupo(request.user.groups.all())
    form_escala = FormularioEscalaCeu()

    if data_enviada:
        ordens = (OrdemDeServico.objects
                  .filter(escala_ceu=False)
                  .filter(check_in__date=data_enviada)
                  .exclude(atividades_ceu=None, locacao_ceu=None))
    else:
        ordens = (OrdemDeServico.objects
                  .filter(escala_ceu=False)
                  .filter(check_in__month=datetime.now().month)
                  .exclude(atividades_ceu=None, locacao_ceu=None))

    if is_ajax(request):
        if request.POST.get('grupo'):
            grupo = retornar_dados_grupo(ordens, request.POST.get('grupo'))
            return JsonResponse({'check_in': grupo.check_in_ceu,
                                 'check_out': grupo.check_out_ceu})

        if request.POST.get('data'):
            return JsonResponse({'disponiveis': verificar_disponiveis(request.POST.get('data'))})

        if request.POST.get('check_in'):
            return JsonResponse(
                verificar_disponiveis_grupo(request.POST.get('check_in'), request.POST.get('check_out')))

    if request.method != 'POST':
        return render(request, 'escala/escalar_professores.html', {'grupos': grupos,
                                                                   'data': data_enviada,
                                                                   'formulario': form_escala,
                                                                   'ordens': ordens})

    form_escala = FormularioEscalaCeu(request.POST)
    nova_escala = form_escala.save(commit=False)

    if form_escala.is_valid():
        try:
            nova_escala.equipe = {'professores_escalados': list(map(int, request.POST.getlist("equipe_escalada")))}

            if nova_escala.tipo_escala == 1:
                check_in_publico = request.POST.get('data_publico') + ' 20:30'
                check_out_publico = request.POST.get('data_publico') + ' 23:00'
                nova_escala.check_in_grupo = datetime.strptime(check_in_publico, '%Y-%m-%d %H:%M')
                nova_escala.check_out_grupo = datetime.strptime(check_out_publico, '%Y-%m-%d %H:%M')

            form_escala.save()
        except Exception as e:
            email_error(request.user.get_full_name(), e, __name__)
            messages.error(request, f'Houve um erro inesperado, tente novamente mais tarde! {e}')
            return redirect('dashboard')
        else:
            ordem = OrdemDeServico.objects.get(ficha_de_evento__cliente__id=int(request.POST.get('cliente')))
            ordem.escala_ceu = True
            ordem.save()

            messages.success(request, f'Escala para o vento de {ordem.instituicao} salva com sucesso!')
            return redirect('visualizarDisponibilidadeCeu')
    else:
        messages.warning(request, form_escala.errors)
        return render(request, 'escala/escalar_professores.html', {'grupos': grupos,
                                                                   'data': data_enviada,
                                                                   'formulario': form_escala,
                                                                   'ordens': ordens})

    return redirect('visualizarDisponibilidadeCeu')


@login_required(login_url='login')
def disponibilidadePeraltas(request):
    dia_limite_acampamento = DiaLimiteAcampamento.objects.get(id=1)
    dia_limite_hotelaria = DiaLimiteHotelaria.objects.get(id=1)
    grupos = verificar_grupo(request.user.groups.all())

    if request.method != "POST":
        antes_dia_limite_acampamento = True if datetime.now().day < dia_limite_acampamento.dia_limite_acampamento else False
        antes_dia_limite_hotelaria = True if datetime.now().day < dia_limite_hotelaria.dia_limite_hotelaria else False

        coordenador_acampamento = User.objects.filter(pk=request.user.id, groups__name='Coordenador monitoria').exists()
        coordenador_hotelaria = User.objects.filter(pk=request.user.id, groups__name='Coordenador hotelaria').exists()
        monitores = Monitor.objects.all()

        return render(request, 'escala/disponibilidade-peraltas.html', {
            'coordenador_acampamento': coordenador_acampamento,
            'coordenador_hotelaria': coordenador_hotelaria,
            'dia_limite_acampamento': dia_limite_acampamento.dia_limite_acampamento,
            'dia_limite_hotelaria': dia_limite_hotelaria.dia_limite_hotelaria,
            'monitores': monitores,
            'antes_dia_limite_acampamento': antes_dia_limite_acampamento,
            'antes_dia_limite_hotelaria': antes_dia_limite_hotelaria,
            'grupos': grupos
        })

    if is_ajax(request):
        if request.POST.get('novo_dia'):
            return JsonResponse(alterar_dia_limite_peraltas(request.POST))

        monitor = Monitor.objects.get(usuario=request.user)

        if request.POST.get('monitor') is not None and request.POST.get('monitor') != '':
            monitor = Monitor.objects.get(id=int(request.POST.get('monitor')))

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
                            msg = f'dias {dias[1]} já estão na base de dados. Disponibilidade atualizada com sucesso'
                            return JsonResponse({'tipo': 'sucesso',
                                                 'mensagem': msg})
                        else:
                            return JsonResponse({'tipo': 'sucesso',
                                                 'mensagem': 'Disponibilidade salva com sucesso!'})
                else:
                    return JsonResponse({'tipo': 'aviso',
                                         'mensagem': 'Todos os dias selecionados já estão salvos na base de dados!'})

            else:

                if request.POST.get('peraltas') == 'acampamento':
                    dias_disponiveis = DisponibilidadeAcampamento(monitor=monitor,
                                                                  mes=mes_e_ano_cadastro[0],
                                                                  ano=mes_e_ano_cadastro[1],
                                                                  n_dias=n_dias,
                                                                  dias_disponiveis=dias[0])
                else:
                    dias_disponiveis = DisponibilidadeHotelaria(monitor=monitor,
                                                                mes=mes_e_ano_cadastro[0],
                                                                ano=mes_e_ano_cadastro[1],
                                                                n_dias=n_dias,
                                                                dias_disponiveis=dias[0])

                dias_disponiveis.save()
                return JsonResponse({'tipo': 'sucesso',
                                     'mensagem': 'Disponibilidade salva com sucesso'})
        except Exception as e:
            email_error(request.user.get_full_name(), e, __name__)
            return JsonResponse({'tipo': 'erro',
                                 'mensagem': 'Houve um erro inesperado, tente novamente mais tarde!'})


@login_required(login_url='login')
def verEscalaPeraltas(request):
    coordenador_hotelaria = coordenador_acampamento = False
    setor = ''
    escalas_hotelaria = EscalaHotelaria.objects.all()
    escalas_acampamento = EscalaAcampamento.objects.all()
    grupos = verificar_grupo(request.user.groups.all())

    if is_ajax(request):
        return JsonResponse(escalados_para_o_evento(request.POST))

    if User.objects.filter(pk=request.user.id, groups__name='Coordenador monitoria').exists():
        setor = 'acampamento'
        coordenador_acampamento = True

    if User.objects.filter(pk=request.user.id, groups__name='Coordenador hotelaria').exists():
        setor = 'hotelaria'
        coordenador_hotelaria = True

    return render(request, 'escala/escala_peraltas.html', {'setor': setor,
                                                           'coordenador_acampamento': coordenador_acampamento,
                                                           'coordenador_hotelaria': coordenador_hotelaria,
                                                           'escalas_hotelaria': escalas_hotelaria,
                                                           'escalas_acampamento': escalas_acampamento,
                                                           'grupos': grupos})


@login_required(login_url='login')
def escalarMonitores(request, setor, data):
    data_selecionada = datetime.strptime(data, '%d-%m-%Y').date()
    grupos = verificar_grupo(request.user.groups.all())

    try:
        escalas = EscalaHotelaria.objects.get(data=data_selecionada)
    except EscalaHotelaria.DoesNotExist:
        ...
    except Exception as e:
        email_error(request.user.get_full_name(), e, __name__)
        messages.error(request, 'Ocorreu um erro inesperado, tente novamente mais tarde!')
        return redirect('dashboard')
    else:
        if setor == 'hotelaria' and escalas:
            return redirect('editar_escala_hotelaria', data)

    clientes_dia = pegar_clientes_data_selecionada(data_selecionada)
    monitores_disponiveis_hotelaria, monitores_disponiveis_acampamento = monitores_disponiveis(data_selecionada)

    if request.method != 'POST':
        return render(request, 'escala/escalar_monitores.html', {
            'clientes_dia': clientes_dia,
            'data': data_selecionada,
            'setor': setor,
            'monitores_hotelaria': monitores_disponiveis_hotelaria,
            'monitores_acampamento': monitores_disponiveis_acampamento,
            'grupos': grupos})

    if is_ajax(request):
        if request.POST.get('id_monitor'):
            return JsonResponse(verificar_escalas(request.POST.get('id_monitor'), data_selecionada,
                                                  request.POST.get('cliente')))

        if request.POST.get('id_cliente'):
            return JsonResponse(gerar_disponibilidade(request.POST.get('id_cliente')))

    if setor == 'acampamento':
        try:
            cliente = ClienteColegio.objects.get(id=int(request.POST.get('cliente')))
            evento_cliente = FichaDeEvento.objects.get(escala=False, cliente=cliente)

            if evento_cliente.os:
                evento_cliente = OrdemDeServico.objects.get(ficha_de_evento__cliente=cliente)

            nova_escala = EscalaAcampamento.objects.create(cliente=cliente,
                                                           check_in_cliente=evento_cliente.check_in,
                                                           check_out_cliente=evento_cliente.check_out)
            nova_escala.monitores_acampamento.set(request.POST.get('monitores_escalados').split(','))

            nova_escala.save()
        except Exception as e:
            email_error(request.user.get_full_name(), e, __name__)
            messages.error(request, 'Houve um erro inesperado, por favor tente mais tarde!')
            return render(request, 'escala/escalar_monitores.html', {
                'clientes_dia': clientes_dia,
                'data': data_selecionada,
                'setor': setor,
                'monitores_hotelaria': monitores_disponiveis_hotelaria,
                'monitores_acampamento': monitores_disponiveis_acampamento,
                'grupos': grupos})
        else:
            ficha_cliente = FichaDeEvento.objects.get(cliente=cliente)
            ficha_cliente.escala = True
            ficha_cliente.save()

            if ficha_cliente.os:
                ordem_cliente = OrdemDeServico.objects.get(ficha_de_evento__cliente=cliente)
                ordem_cliente.escala = True
                ordem_cliente.save()

            messages.success(request, f'Escala para {cliente.nome_fantasia} salva com sucesso!')
            return redirect('escalar_monitores', setor, data)
    elif setor == 'hotelaria':
        try:
            nova_escala = EscalaHotelaria.objects.create(data=data_selecionada)
            nova_escala.monitores_hotelaria.set(request.POST.get('monitores_escalados').split(','))

            nova_escala.save()
        except Exception as e:
            email_error(request.user.get_full_name(), e, __name__)
            messages.error(request, 'Houve um erro inesperado, por favor tente mais tarde!')
            return render(request, 'escala/escalar_monitores.html', {
                'clientes_dia': clientes_dia,
                'data': data_selecionada,
                'setor': setor,
                'monitores_hotelaria': monitores_disponiveis_hotelaria,
                'monitores_acampamento': monitores_disponiveis_acampamento,
                'grupos': grupos})
        else:
            messages.success(request,
                             f'Escala para {datetime.strftime(data_selecionada, "%d/%m/%Y")} salva com sucesso!')
            return redirect('escalaPeraltas')


@login_required(login_url='login')
def editarEscalaMonitores(request, cliente, data):
    data_selecionada = datetime.strptime(data, '%d-%m-%Y').date()
    nome_fantasia_cliente = json.dumps(cliente, ensure_ascii=False).replace('"', '')
    cliente_evento = ClienteColegio.objects.get(nome_fantasia=nome_fantasia_cliente)
    ficha_evento_cliete = FichaDeEvento.objects.get(cliente=cliente_evento)
    disponiveis_hotelaria, disponiveis_acampamento = monitores_disponiveis(data_selecionada)
    id_escalados = []
    grupos = verificar_grupo(request.user.groups.all())

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
                                                                       'id_escalados': id_escalados,
                                                                       'grupos': grupos})

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
    grupos = verificar_grupo(request.user.groups.all())

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
                                                                       'restante_hotelaria': restante_hotelaria,
                                                                       'grupos': grupos})

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
    disponibilidades_hotelaria = DisponibilidadeHotelaria.objects.all()
    disponibilidades_acampamento = DisponibilidadeAcampamento.objects.all()
    eventos_ordem_de_servico = OrdemDeServico.objects.all()
    fichas_de_evento = FichaDeEvento.objects.filter(os=False)
    coordenador_hotelaria = coordenador_acampamento = False
    grupos = verificar_grupo(request.user.groups.all())
    setor = ''

    for evento in eventos_ordem_de_servico:
        evento.check_out += timedelta(days=1)

    for ficha in fichas_de_evento:
        ficha.check_out += timedelta(days=1)

    if User.objects.filter(pk=request.user.id, groups__name='Coordenador monitoria').exists():
        setor = 'acampamento'
        coordenador_acampamento = True

    if User.objects.filter(pk=request.user.id, groups__name='Coordenador hotelaria').exists():
        setor = 'hotelaria'
        coordenador_hotelaria = True

    disponiveis_hotelaria = pegar_disponiveis(disponibilidades_hotelaria, 'hotelaria')
    disponiveis_acampamento = pegar_disponiveis(disponibilidades_acampamento, 'acampamento')

    return render(request, 'escala/calendario_disponibilidade_peraltas.html',
                  {'disponiveis_hotelaria': disponiveis_hotelaria,
                   'disponiveis_acampamento': disponiveis_acampamento,
                   'eventos': eventos_ordem_de_servico,
                   'fichas_de_evento': fichas_de_evento,
                   'coordenador_hotelaria': coordenador_hotelaria,
                   'coordenador_acampamento': coordenador_acampamento,
                   'setor': setor,
                   'grupos': grupos})


@login_required(login_url='login')
def visualizarDisponibilidadeCeu(request):
    disponiveis_ceu = Disponibilidade.objects.all()
    eventos = OrdemDeServico.objects.all()
    grupos = verificar_grupo(request.user.groups.all())

    for evento in eventos:
        if evento.atividades_ceu:
            evento.check_out_ceu += timedelta(days=1)

    disponiveis = pegar_disponiveis(disponiveis_ceu, 'ceu')

    return render(request, 'escala/calendario_disponibilidade_ceu.html', {'disponiveis': disponiveis,
                                                                          'eventos': eventos,
                                                                          'grupos': grupos})
