import datetime
from itertools import chain

from ceu.models import Professores
from escala.models import Disponibilidade
from ordemDeServico.models import OrdemDeServico
from peraltas.models import DisponibilidadeAcampamento, DisponibilidadeHotelaria, Monitor, DiaLimiteHotelaria, \
    DiaLimiteAcampamento, FichaDeEvento, ClienteColegio, EscalaAcampamento


def is_ajax(request):
    """
    Função responsável por verificar se a requisição é do ajax

    :param request: requisição enviada
    :return: Booleano
    """

    return request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest'


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


def verificar_dias(dias_enviados, professor, peraltas=None):
    """
    Está função é responsável pela verificação dos dias enviados pelo usuário para serem salvos na base de dados,
    verifica dentre todas as datas as que já estão salvas, para que não haja duplicatas e retorna duas listas, uma
    com os dias a serem salvos e a outra com as datas já salvas anteriormente.

    :param dias_enviados: Dias enviados pelo usuário para ser cadastrado na base de dados
    :param professor: Professor ou monitor que enviou os dias
    :param peraltas: Se o usuário que enviou os dias é do acampamento Peraltas ou da hotelaria
    :return: No final é retornado duas listas, a primeira com os os dias que serão salvos na base de dados
    e a segunda com os dias que o usuário enviou e que já estão salvos. Importante para que os dias já salvos
    sejam mostrado na tela para o usuário.
    """
    lista_dias = dias_enviados.split(', ')  # Transforma a string que vem com os dias em uma lista
    # ----------------------------- Verifica o mês e o ano das datas enviadas -----------------------------
    mes = datetime.datetime.strptime(dias_enviados.split(', ')[0], '%d/%m/%Y').month
    ano = datetime.datetime.strptime(dias_enviados.split(', ')[0], '%d/%m/%Y').year
    dias_ja_cadastrados = []  # Lista para os dias já presentes na base de dados
    dias_a_cadastrar = []  # Lista para os dias que serão salvos na base de dados

    # Verifica a intancia do usuário que enviou a disponibilidade, se é professor do CEU ou do Peraltas
    # para poder pegar os dias já cadastrados pelo usuário no model correto
    if isinstance(professor, Professores):
        try:
            dias_cadastrados = Disponibilidade.objects.get(professor=professor, mes=mes, ano=ano)
        except Disponibilidade.DoesNotExist:
            dias_cadastrados = None
    else:
        if peraltas == 'acampamento':  # Em caso de ser do Peraltas, verifica se a disponibildade vai pro acampamento
            try:
                dias_cadastrados = DisponibilidadeAcampamento.objects.get(monitor=professor, mes=mes, ano=ano)
            except DisponibilidadeAcampamento.DoesNotExist:
                dias_cadastrados = None
        else:  # Ou se vai para a hotelaria
            try:
                dias_cadastrados = DisponibilidadeHotelaria.objects.get(monitor=professor, mes=mes, ano=ano)
            except DisponibilidadeHotelaria.DoesNotExist:
                dias_cadastrados = None

    if dias_cadastrados:  # Primeiro verifica se o usuário já cadastrou algum dia
        lista_dias_cadastrados = dias_cadastrados.dias_disponiveis.split(', ')  # Lista de dias já cadastrado

        # ----- Looping de verificação dos dias -----
        for dia in lista_dias:
            if dia in lista_dias_cadastrados:
                dias_ja_cadastrados.append(dia)
            else:
                dias_a_cadastrar.append(dia)
        # -------------------------------------------
    else:
        dias_a_cadastrar.append(dias_enviados)  # Caso o usuário não tenha cadastrado nenhum dia ainda

    return ', '.join(dias_a_cadastrar), ', '.join(dias_ja_cadastrados)


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

    mes = datetime.datetime.strptime(dias.split(', ')[0], '%d/%m/%Y').month
    ano = datetime.datetime.strptime(dias.split(', ')[0], '%d/%m/%Y').year

    return mes, ano


def alterar_dia_limite_peraltas(dados):
    """
    Função responsável por salvar a alteração do dia limite para envio das disponibilidade. Importante
    ressaltar que o dia já deve vir correto, para isso foi implementado um verificação do dia, no frontend
    com javascript antes de ele ser enviado.

    :param dados: Setor que enviou a alteração e o novo dia limite
    :return: Retorna se o novo dia foi salvo com sucesso ou não e uma mensagem padrão para
    cada uma das respostas.
    """
    # ----------------------- No caso do setor que alterou a data tenha sido a hotelaria ----------------------------
    if dados.get('setor') == 'hotelaria':
        dia_limite_hotelaria = DiaLimiteHotelaria.objects.get(id=1)  # Dia limite atual

        try:  # Tentativa de alteração da data
            dia_limite_hotelaria.dia_limite_hotelaria = int(dados.get('novo_dia'))
            dia_limite_hotelaria.save()
        except:  # Caso tenha acontecido algum erro ainda não reportado
            return {'tipo': 'error', 'mensagem': 'Houve um erro inesperado, por favor tente novamente mais tarde!'}
        else:  # Novo dia salvo com sucesso
            return {'tipo': 'sucesso', 'mensagem': 'Dia limite atualizado com sucesso!'}

    # -------------------- No caso do setor que alterou o dia tenha sido o acampamento ----------------------------
    if dados.get('setor') == 'acampamento':
        dia_limite_acampamento = DiaLimiteAcampamento.objects.get(id=1)  # Dia limite atual

        try:  # Tentativa de atualização do dia
            dia_limite_acampamento.dia_limite_acampamento = int(dados.get('novo_dia'))
            dia_limite_acampamento.save()
        except:  # Caso tenha acontecido algum erro ainda não relatado
            return {'tipo': 'error', 'mensagem': 'Houve um erro inesperado, por favor tente novamente mais tarde!'}
        else:  # Novo dia salvo com sucesso
            return {'tipo': 'sucesso', 'mensagem': 'Dia limite atualizado com sucesso!'}


def pegar_clientes_data_selecionada(data):
    """
    Função responsável por pegar os colégio e as empresas que virão em uma determinada data, selecionada
    peloe coordenador do acampamento e retornar os dados todos padronizados. Necessário pelos models da
    ficha de evento e ordem de serviço ter nomes diferentes em relação ao cliente.

    :param data: Data selecionada
    :return: Retorna a lista de todos os clientes padronizado, id e nome fantasia
    """
    # ----- Primeiramente é pego os cliente que não tornaram OS e depois as fichas de evento que já tem sua OS -----
    clientes_dia_ficha = FichaDeEvento.objects.filter(os=False, escala=False).filter(check_in__date__lte=data,
                                                                                     check_out__date__gte=data)
    clientes_dia_ordem = OrdemDeServico.objects.filter(escala=False).filter(check_in__date__lte=data,
                                                                            check_out__date__gte=data)
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


def monitores_disponiveis(data):
    mes = data.month
    ano = data.year
    monitores_diponiveis_hotelaria = []
    monitores_disponiveis_acampamento = []

    monitores_hotelaria = DisponibilidadeHotelaria.objects.filter(ano=ano).filter(mes=mes).filter(
        dias_disponiveis__icontains=data.strftime('%d/%m/%Y'))
    monitores_acampamento = DisponibilidadeAcampamento.objects.filter(ano=ano).filter(mes=mes).filter(
        dias_disponiveis__icontains=data.strftime('%d/%m/%Y'))

    monitores = list(chain(monitores_hotelaria, monitores_acampamento))

    for monitor in monitores:
        if isinstance(monitor, DisponibilidadeHotelaria):
            monitores_diponiveis_hotelaria.append({'id': monitor.monitor.id,
                                                   'nome': monitor.monitor.usuario.get_full_name()})
        else:
            monitores_disponiveis_acampamento.append({'id': monitor.monitor.id,
                                                      'nome': monitor.monitor.usuario.get_full_name()})

    return monitores_diponiveis_hotelaria, monitores_disponiveis_acampamento


def escalados_para_o_evento(dados_evento):
    cliente = ClienteColegio.objects.get(nome_fantasia=dados_evento.get('cliente'))
    check_in_evento = datetime.datetime.strptime(dados_evento.get('check_in_evento'), '%Y-%m-%dT%H:%M')
    check_out_evento = datetime.datetime.strptime(dados_evento.get('check_out_evento'), '%Y-%m-%dT%H:%M')
    monitores_escalados = []

    escala_evento_cliente = EscalaAcampamento.objects.get(cliente=cliente, check_in_cliente=check_in_evento,
                                                          check_out_cliente=check_out_evento)

    for monitor in escala_evento_cliente.monitores_acampamento.all():
        monitores_escalados.append(monitor.usuario.get_full_name())

    return {'escalados': monitores_escalados}
