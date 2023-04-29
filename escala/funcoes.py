import json
from datetime import datetime, timedelta
from itertools import chain

from ceu.models import Professores
from escala.models import Disponibilidade
from ordemDeServico.models import OrdemDeServico
from peraltas.models import DisponibilidadePeraltas, Monitor, DiaLimitePeraltas, FichaDeEvento, ClienteColegio, \
    Enfermeira, EscalaAcampamento, EscalaHotelaria


def is_ajax(request):
    """
    Função responsável por verificar se a requisição é do ajax

    :param request: requisição enviada
    :return: Booleano
    """

    return request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest'


def retornar_dados_grupo(ordens, id_grupo):
    for ordem in ordens:
        if ordem.ficha_de_evento.cliente.id == int(id_grupo):
            return ordem


def verificar_disponiveis(data):
    professores_disponiveis = []
    disponiveis = Disponibilidade.objects.filter(dias_disponiveis__icontains=data)

    for disponivel in disponiveis:
        professores_disponiveis.append({'id': disponivel.professor.id,
                                        'nome': disponivel.professor.usuario.get_full_name()})

    return {'disponiveis': professores_disponiveis}


def verificar_disponiveis_grupo(check_in, check_out):
    check_out = datetime.strptime(check_out, '%Y-%m-%dT%H:%M').date()
    check_in = datetime.strptime(check_in, '%Y-%m-%dT%H:%M').date()
    disponiveis = Disponibilidade.objects.filter(mes=check_in.month, ano=check_in.year)
    disponiveis_grupo = []

    for disponivel in disponiveis:
        check_in_teste = check_in

        while check_in_teste <= check_out:
            if check_in_teste.strftime('%d/%m/%Y') not in disponivel.dias_disponiveis:
                break

            if check_in_teste == check_out:
                disponiveis_grupo.append({'id': disponivel.professor.id,
                                          'nome': disponivel.professor.usuario.get_full_name()})

            check_in_teste += timedelta(days=1)

    return {'disponiveis': disponiveis_grupo}


def escalar(coodenador, prof_2, prof_3, prof_4, prof_5):
    """
    Função que verifica os professores fornecidos e  monta a escala.
    :param coodenador: Coordenador do dia
    :param prof_2: Professor 2
    :param prof_3: Professore 3
    :param prof_4: Professor 4
    :param prof_5: Professor 5
    :return: Retorna um string com a seguência dos professores.
    """

    equipe = [coodenador]  # A equipe escala sempre terá um coordenaor
    equipe = [coodenador]  # A equipe escala sempre terá um coordenaor

    # Início da verificação dos professores que foram fornecidos
    if prof_2:
        equipe.append(prof_2)

    if prof_3:
        equipe.append(prof_3)

    if prof_4:
        equipe.append(prof_4)

    if prof_5:
        equipe.append(prof_5)

    return ','.join(equipe)


def transformar_disponibilidades(disponibilidades):
    lista_disponibilidades_formatadas = []

    for i, disponibilidade in enumerate(disponibilidades, start=1):
        dias_disponiveis = disponibilidade.dias_disponiveis.split(', ')
        monitor = disponibilidade.monitor
        enfermeira = disponibilidade.enfermeira

        for j, dia_ in enumerate(dias_disponiveis, start=1):
            try:
                dia = datetime.strptime(dia_, '%d/%m/%Y').strftime('%Y-%m-%d')
            except ValueError:
                ...
            else:
                if monitor:
                    disponibilidade_formatada = {
                        'id': f'disponibilidade_{disponibilidade.monitor.id}_{dia}',
                        'title': monitor.usuario.get_full_name(),
                        'start': f'{dia}',
                        'extendedProps': {
                            'id_monitor': f'{monitor.id}',
                            'color': '#FF8C00',
                        }
                    }
                else:
                    disponibilidade_formatada = {
                        'id': f'disponibilidade_{disponibilidade.enfermeira.id}_{dia}',
                        'title': enfermeira.usuario.get_full_name(),
                        'start': f'{dia}',
                        'extendedProps': {
                            'id_enfermeira': f'{enfermeira.id}',
                            'color': '#ff7474',
                        }
                    }

                lista_disponibilidades_formatadas.append(disponibilidade_formatada)

    return json.dumps(lista_disponibilidades_formatadas)


def adicionar_dia(monitor, dia_adicionado, enfermeira):
    try:
        if monitor:
            disponibilidade_existente = DisponibilidadePeraltas.objects.get(
                monitor=monitor,
                mes=dia_adicionado.month,
                ano=dia_adicionado.year
            )
        else:
            disponibilidade_existente = DisponibilidadePeraltas.objects.get(
                enfermeira=enfermeira,
                mes=dia_adicionado.month,
                ano=dia_adicionado.year
            )
    except DisponibilidadePeraltas.DoesNotExist:
        if monitor:
            DisponibilidadePeraltas.objects.create(
                monitor=monitor,
                dias_disponiveis=dia_adicionado.strftime('%d/%m/%Y'),
                mes=dia_adicionado.month,
                ano=dia_adicionado.year,
                n_dias=1
            )
        else:
            DisponibilidadePeraltas.objects.create(
                enfermeira=enfermeira,
                dias_disponiveis=dia_adicionado.strftime('%d/%m/%Y'),
                mes=dia_adicionado.month,
                ano=dia_adicionado.year,
                n_dias=1
            )

        return True
    else:
        if disponibilidade_existente.n_dias < 22 or monitor.fixo:
            disponibilidade_existente.dias_disponiveis += f', {dia_adicionado.strftime("%d/%m/%Y")}'
            disponibilidade_existente.n_dias += 1
            disponibilidade_existente.save()

            return True
        else:
            return False


def remover_dia(monitor, dia_removido, enfermeira):
    if monitor:
        disponibilidade_cadastrada = DisponibilidadePeraltas.objects.get(
            monitor=monitor,
            mes=dia_removido.month,
            ano=dia_removido.year
        )
    else:
        disponibilidade_cadastrada = DisponibilidadePeraltas.objects.get(
            enfermeira=enfermeira,
            mes=dia_removido.month,
            ano=dia_removido.year
        )

    try:
        lista_dias = disponibilidade_cadastrada.dias_disponiveis.split(', ')
        lista_dias.remove(dia_removido.strftime('%d/%m/%Y'))
        disponibilidade_cadastrada.dias_disponiveis = ', '.join(lista_dias)
        disponibilidade_cadastrada.n_dias -= 1
        disponibilidade_cadastrada.save()
    except Exception as e:
        print(e)
        return

    return


def verificar_dias(dias_enviados, professor):
    """
    Está função é responsável pela verificação dos dias enviados pelo usuário para serem salvos na base de dados,
    verifica dentre todas as datas as que já estão salvas, para que não haja duplicatas e retorna duas listas, uma
    com os dias a serem salvos e a outra com as datas já salvas anteriormente.

    :param dias_enviados: Dias enviados pelo usuário para ser cadastrado na base de dados
    :param professor: Professor que enviou os dias
    :return: No final é retornado duas listas, a primeira com os os dias que serão salvos na base de dados
    e a segunda com os dias que o usuário enviou e que já estão salvos. Importante para que os dias já salvos
    sejam mostrado na tela para o usuário.
    """
    lista_dias = dias_enviados.split(', ')  # Transforma a string que vem com os dias em uma lista
    # ----------------------------- Verifica o mês e o ano das datas enviadas -----------------------------
    mes = datetime.strptime(dias_enviados.split(', ')[0], '%d/%m/%Y').month
    ano = datetime.strptime(dias_enviados.split(', ')[0], '%d/%m/%Y').year
    dias_ja_cadastrados = []  # Lista para os dias já presentes na base de dados
    dias_a_cadastrar = []  # Lista para os dias que serão salvos na base de dados
    dias_limite = False

    try:
        dias_cadastrados = Disponibilidade.objects.get(professor=professor, mes=mes, ano=ano)
    except Disponibilidade.DoesNotExist:
        dias_cadastrados = False

    if dias_cadastrados:  # Primeiro verifica se o usuário já cadastrou algum dia
        lista_dias_cadastrados = dias_cadastrados.dias_disponiveis.split(', ')  # Lista de dias já cadastrado

        if len(lista_dias_cadastrados) > 22:
            dias_limite = True
        else:
            dias_faltando = 22 - len(lista_dias_cadastrados)
            # ----- Looping de verificação dos dias -----
            for dia in lista_dias:
                if dias_faltando > 0:
                    if dia in lista_dias_cadastrados:
                        dias_ja_cadastrados.append(dia)
                    else:
                        dias_a_cadastrar.append(dia)
                        dias_faltando -= 1
                else:
                    dias_limite = True
                    dias_ja_cadastrados.append(dia)
            # -------------------------------------------
    else:
        dias_a_cadastrar.append(dias_enviados)  # Caso o usuário não tenha cadastrado nenhum dia ainda

    return ', '.join(dias_a_cadastrar), ', '.join(dias_ja_cadastrados), dias_limite


def contar_dias(dias):
    """
    Função responsável por simplesmente contar o número de dias disponíveis que o usuário informou

    :param dias: Lista dos dias que serão salvos
    :return: Retorna o comprimento da lista
    """

    lista_dias = dias.split(', ')
    return len(lista_dias)


def verificar_mes_e_ano(dias):
    """
    Função para conseguir o mês e o ano das datas disponiveis enviadas.

    :param dias: Lista de dias enviados
    :return: Retorna o mês e o ano das datas
    """

    mes = datetime.strptime(dias.split(', ')[0], '%d/%m/%Y').month
    ano = datetime.strptime(dias.split(', ')[0], '%d/%m/%Y').year

    return mes, ano


def pegar_clientes_data_selecionada(data):
    """
    Função responsável por pegar os colégio e as empresas que virão em uma determinada data, selecionada
    peloe coordenador do acampamento e retornar os dados todos padronizados. Necessário pelos models da
    ficha de evento e ordem de serviço ter nomes diferentes em relação ao cliente.

    :param data: Data selecionada
    :return: Retorna a lista de todos os clientes padronizado, id e nome fantasia
    """
    # ----- Primeiramente é pego os cliente que não tornaram OS e depois as fichas de evento que já tem sua OS -----
    clientes_dia_ficha = FichaDeEvento.objects.filter(os=False, escala=False, pre_reserva=False).filter(
        check_in__date__lte=data,
        check_out__date__gte=data
    )
    clientes_dia_ordem = OrdemDeServico.objects.filter(escala=False).filter(
        check_in__date__lte=data,
        check_out__date__gte=data
    )
    # Junta em uma lista pra facilitar no looping que vai pegar os dados de forma correta
    todos_clientes = list(chain(clientes_dia_ficha, clientes_dia_ordem))
    clientes = []  # Lista que vai receber os dados

    # ----------------- Looping respoensável por pegar os dados do cliente em cada instância ---------------------
    for cliente in todos_clientes:
        if isinstance(cliente, FichaDeEvento):
            clientes.append({'id': cliente.cliente.id, 'nome_fantasia': cliente.cliente.nome_fantasia})
        else:
            clientes.append({'id': cliente.ficha_de_evento.cliente.id,
                             'nome_fantasia': cliente.ficha_de_evento.cliente.nome_fantasia})
    # ------------------------------------------------------------------------------------------------------------
    return clientes


def gerar_disponibilidade(id_cliente, data, editando=False):
    cliente = ClienteColegio.objects.get(id=int(id_cliente))

    if editando:
        ficha_de_evento_cliente = FichaDeEvento.objects.get(
            cliente=cliente,
            check_in__date__lte=data,
            check_out__date__gte=data
        )
    else:
        ficha_de_evento_cliente = FichaDeEvento.objects.get(
            escala=False,
            check_in__date__lte=data,
            check_out__date__gte=data,
            cliente=cliente
        )

    check_in = ficha_de_evento_cliente.check_in
    check_out = ficha_de_evento_cliente.check_out

    if ficha_de_evento_cliente.os:
        ordem_cliente = OrdemDeServico.objects.get(
            ficha_de_evento__cliente=cliente,
            check_in__date__lte=data,
            check_out__date__gte=data
        )
        check_in = ordem_cliente.check_in
        check_out = ordem_cliente.check_out

    disponibilidades_peraltas = DisponibilidadePeraltas.objects.filter(
        dias_disponiveis__icontains=check_in.strftime('%d/%m/%Y')
    )

    disponiveis_intervalo = pegar_disponiveis_intervalo(check_in, check_out, disponibilidades_peraltas)

    return disponiveis_intervalo


def pegar_disponiveis_intervalo(check_in, check_out, lista_disponiveis):
    disponiveis_intervalo = []
    dias = check_out - check_in
    monitores_disponiveis_intervalo = []

    for disponivel in lista_disponiveis:
        intervalo = True

        for i in range(0, dias.days + 1):
            if (check_in + timedelta(days=i)).strftime('%d/%m/%Y') in disponivel.dias_disponiveis:
                continue
            else:
                intervalo = False
                break

        if intervalo and disponivel not in disponiveis_intervalo:
            disponiveis_intervalo.append(disponivel)

    for disponibilidade in disponiveis_intervalo:
        areas = []

        if disponibilidade.monitor:
            areas.append('som') if disponibilidade.monitor.som else ...
            areas.append('video') if disponibilidade.monitor.video else ...
            areas.append('fotos_e_filmagens') if disponibilidade.monitor.fotos_e_filmagens else ...
            biologo = 'biologo' if disponibilidade.monitor.biologo else ''

            dados_monitor = {
                'id': disponibilidade.monitor.id,
                'nome': disponibilidade.monitor.usuario.get_full_name(),
                'setor': 'peraltas',
                'tecnica': disponibilidade.monitor.tecnica,
                'areas': '-'.join(areas),
                'biologo': biologo
            }
        else:
            dados_monitor = {
                'id': disponibilidade.enfermeira.id,
                'nome': disponibilidade.enfermeira.usuario.get_full_name(),
                'setor': 'enfermeira',
                'tecnica': False,
                'areas': '',
                'biologo': False
            }

        monitores_disponiveis_intervalo.append(dados_monitor)

    return monitores_disponiveis_intervalo


def verificar_escalas(id_monitor, data_selecionada, id_cliente):
    monitor_escalado = Monitor.objects.get(id=int(id_monitor))
    escalas_monitor_hotelaria = None

    if id_cliente:
        try:
            escala_monitor_escalado = EscalaAcampamento.objects.get(
                cliente__id=int(id_cliente),
                check_in_cliente__date__lte=data_selecionada,
                check_out_cliente__date__gte=data_selecionada,
            )
        except EscalaAcampamento.DoesNotExist:
            check_in = check_out = None
        else:
            check_in = escala_monitor_escalado.check_in_cliente
            check_out = escala_monitor_escalado.check_out_cliente

        escalas_monitor_acampamento = EscalaAcampamento.objects.filter(
            monitores_acampamento=monitor_escalado,
            monitores_embarque=monitor_escalado,
            check_in_cliente__date__lte=data_selecionada,
            check_out_cliente__date__gte=data_selecionada).exclude(cliente__id=int(id_cliente))
        if check_in:
            for soma_dia in range(0, (check_out.day - check_in.day) + 1):
                dia = check_in + timedelta(days=soma_dia)

                escalas_monitor_hotelaria = EscalaHotelaria.objects.filter(
                    monitores_escalados=monitor_escalado,
                    data=dia
                )

                if len(escalas_monitor_hotelaria) > 0:
                    break
    else:
        escalas_monitor_acampamento = EscalaAcampamento.objects.filter(
            monitores_acampamento=monitor_escalado,
            check_in_cliente__date__lte=data_selecionada,
            check_out_cliente__date__gte=data_selecionada
        )

    if escalas_monitor_acampamento and not escalas_monitor_hotelaria:
        return {'acampamento': True, 'hotelaria': False}
    elif escalas_monitor_hotelaria and not escalas_monitor_acampamento:
        return {'acampamento': False, 'hotelaria': True}
    else:
        return {'acampamento': False, 'hotelaria': False}


def escalados_para_o_evento(dados_evento):
    escala = EscalaAcampamento.objects.get(pk=dados_evento.get('id_escala'))
    cliente = escala.cliente
    check_in_evento = escala.check_in_cliente
    check_out_evento = escala.check_out_cliente
    monitores_escalados = []
    monitores_embarque = []
    enfermeiras = []

    try:
        ordem_evento_cliente = OrdemDeServico.objects.get(ficha_de_evento__cliente=cliente,
                                                          check_in=check_in_evento,
                                                          check_out=check_out_evento)
    except OrdemDeServico.DoesNotExist:
        ordem_evento_cliente = False

    for monitor in escala.monitores_acampamento.all():
        if ordem_evento_cliente and ordem_evento_cliente.monitor_responsavel == monitor:
            monitores_escalados.append({'nome': monitor.usuario.get_full_name(), 'coordenador': True})
        else:
            monitores_escalados.append({'nome': monitor.usuario.get_full_name(), 'coordenador': False})

    for monitor in escala.biologos.all():
        if ordem_evento_cliente and ordem_evento_cliente.monitor_responsavel == monitor:
            monitores_escalados.append({'nome': monitor.usuario.get_full_name(), 'coordenador': True})
        else:
            monitores_escalados.append({'nome': monitor.usuario.get_full_name(), 'coordenador': False})

    for monitor in escala.monitores_embarque.all():
        if ordem_evento_cliente and ordem_evento_cliente.monitor_responsavel == monitor:
            monitores_embarque.append({'nome': monitor.usuario.get_full_name(), 'coordenador': True})
        else:
            monitores_embarque.append({'nome': monitor.usuario.get_full_name(), 'coordenador': False})

    for enfermeira in escala.enfermeiras.all():
        enfermeiras.append({'nome': enfermeira.usuario.get_full_name(), 'coordenador': False})

    return {
        'escalados': {
            'acampamento': monitores_escalados,
            'embarque': monitores_embarque,
            'enfermeiras': enfermeiras
        },
        'id_cliente': cliente.id,
        'pre_escala': escala.pre_escala
    }


def pegar_disponiveis(disponibilidades, setor):
    disponiveis_peraltas = []
    disponiveis_ceu = []

    if setor == 'peraltas':
        for disponivel in disponibilidades:
            datas = []
            temp = disponivel.dias_disponiveis.split(', ')

            for dia in temp:
                try:
                    datas.append(datetime.strptime(dia, '%d/%m/%Y').strftime('%Y-%m-%d'))
                except ValueError:
                    ...

            if disponivel.monitor:
                disponiveis_peraltas.append({
                    'monitor': disponivel.monitor.usuario.get_full_name(),
                    'dias_disponiveis': datas
                })
            else:
                disponiveis_peraltas.append({
                    'monitor': disponivel.enfermeira.usuario.get_full_name(),
                    'dias_disponiveis': datas
                })

        return disponiveis_peraltas
    else:
        for disponivel in disponibilidades:
            datas = []
            temp = disponivel.dias_disponiveis.split(', ')

            for dia in temp:
                datas.append(datetime.strptime(dia, '%d/%m/%Y').strftime('%Y-%m-%d'))

            disponiveis_ceu.append({
                'professor': disponivel.professor.usuario.get_full_name(),
                'dias_disponiveis': datas
            })

        return disponiveis_ceu


def especialidade_monitor(monitor_escalado):
    especialidades = []
    monitor = Monitor.objects.get(id=monitor_escalado['id'])

    if monitor.som:
        especialidades.append('som')

    if monitor.video:
        especialidades.append('video')

    if monitor.fotos_e_filmagens:
        especialidades.append('fotos_e_filmagens')

    return ' '.join(especialidades)


def pegar_escalacoes(escala, acampamento=True):
    escalados = []

    for monitor in escala.monitores_acampamento.all():
        escalados.append(monitor.id)

    for monitor in escala.monitores_embarque.all():
        escalados.append(monitor.id)

    for monitor in escala.biologos.all():
        escalados.append(monitor.id)

    for enfermeira in escala.enfermeiras.all():
        escalados.append(enfermeira.id)

    return escalados


def procurar_ficha_de_evento(cliente, data_selecionada):
    try:
        ficha_de_evento = FichaDeEvento.objects.get(
            cliente=cliente,
            check_in__date__lte=data_selecionada,
            check_out__date__gte=data_selecionada
        )
    except FichaDeEvento.DoesNotExist:
        ordem_de_servico = OrdemDeServico.objects.get(
            ficha_de_evento__cliente=cliente,
            check_in__date__lte=data_selecionada,
            check_out__date__gte=data_selecionada
        )

        return ordem_de_servico.ficha_de_evento, ordem_de_servico
    else:
        if ficha_de_evento.os:
            return ficha_de_evento, OrdemDeServico.objects.get(ficha_de_evento=ficha_de_evento)
        else:
            return ficha_de_evento, None


def pegar_dados_monitor_embarque(os):
    dados_monitores = []
    print(len(os.dados_transporte.all()))
    if not os.dados_transporte:
        return None

    for transporte in os.dados_transporte.all():
        areas = []
        monitor = transporte.monitor_embarque

        areas.append('som') if monitor.som else ...
        areas.append('video') if monitor.video else ...
        areas.append('fotos_e_filmagens') if monitor.fotos_e_filmagens else ...
        biologo = 'biologo' if monitor.biologo else ''

        dados_monitor = {
            'id': monitor.id,
            'nome': monitor.usuario.get_full_name(),
            'setor': 'peraltas',
            'tecnica': monitor.tecnica,
            'areas': '-'.join(areas),
            'biologo': biologo
        }

        dados_monitores.append(dados_monitor)

    return dados_monitores


def pegar_dados_monitor_biologo(os):
    dados_monitores = []

    if not os.atividades_eco:
        return None

    for atividade in os.atividades_eco.values():
        areas = []
        id_monitor = atividade['biologo']
        monitor = Monitor.objects.get(pk=id_monitor)

        areas.append('som') if monitor.som else ...
        areas.append('video') if monitor.video else ...
        areas.append('fotos_e_filmagens') if monitor.fotos_e_filmagens else ...
        biologo = 'biologo' if monitor.biologo else ''

        dados_monitor = {
            'id': monitor.id,
            'nome': monitor.usuario.get_full_name(),
            'setor': 'peraltas',
            'tecnica': monitor.tecnica,
            'areas': '-'.join(areas),
            'biologo': biologo
        }

        if dados_monitor not in dados_monitores:
            dados_monitores.append(dados_monitor)

    return dados_monitores


def salvar_ultima_pre_escala(dados_escala):
    return {
        'acampamento': list(map(int, dados_escala.getlist('id_monitores[]'))),
        'embarque': list(map(int, dados_escala.getlist('id_monitores_embarque[]'))),
        'biologos': list(map(int, dados_escala.getlist('id_biologos[]'))),
    }
