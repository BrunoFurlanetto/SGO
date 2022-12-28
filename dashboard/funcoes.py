import pytz
from django.contrib.auth.models import User
from ceu.models import Professores
from datetime import datetime, timedelta, timezone
from escala.models import Disponibilidade, DiaLimite
from unidecode import unidecode

from peraltas.models import DisponibilidadeAcampamento, DisponibilidadeHotelaria


# ------------ Função necessária para verificar se é o ajax que está mandando o POST para o servidor -------------------
# ----------------------------------------------------------------------------------------------------------------------
def is_ajax(request):
    return request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest'


# ----------------------------------------------------------------------------------------------------------------------


# ------------------- Função responsável por juntar os dados à ser enviados para o ajax --------------------------------
# ----------------------------------------------------------------------------------------------------------------------
def juntar_dados(relatorios):
    i = 1
    dados = {}

    for relatorio in relatorios:
        dados[f'relatorio_{i}'] = {'id': relatorio.id,
                                   'tipo': relatorio.tipo,
                                   'coordenador': relatorio.equipe['coordenador'],
                                   'equipe': relatorio.equipe,
                                   'url': f'relatorio-de-atendimento/{unidecode(relatorio.tipo).lower()}/{relatorio.id}'}

        if relatorio.tipo != 'Público':
            dados[f'relatorio_{i}']['instituicao'] = relatorio.instituicao
        else:
            dados[f'relatorio_{i}']['instituicao'] = ''

        i += 1

    return dados


# ---------------------------------- Funções relacionadas ao resumo do mês ---------------------------------------------
# ---------------------------------- Contar atividades para o resumo do mês --------------------------------------------
def contar_atividades(professor_logado, relatorios):
    n_atividades = 0

    for relatorio in relatorios:
        if relatorio.atividades is not None:
            for i in range(len(relatorio.atividades)):
                if professor_logado.usuario.first_name in relatorio.atividades[f'atividade_{i + 1}']['professores']:
                    n_atividades += 1

    return n_atividades


# ----------------------------------------------------------------------------------------------------------------------


# ------------------------------------- Contar horas para o resumo do mês ----------------------------------------------
def contar_horas(professor_logado, relatorios):
    n_horas = timedelta(hours=0, minutes=0)

    for relatorio in relatorios:

        if relatorio.tipo != 'Público' and relatorio.locacoes is not None:
            for i in range(len(relatorio.locacoes)):
                print(relatorio.locacoes['locacao_1'].keys())
                if professor_logado.usuario.first_name in relatorio.locacoes[f'locacao_{i + 1}']['professor']:
                    for j in range(int(len(relatorio.locacoes[f'locacao_{i + 1}']['entradas_e_saidas']) / 3)):
                        n_horas += timedelta(
                            hours=int(
                                relatorio.locacoes[f'locacao_{i + 1}']['entradas_e_saidas'][
                                    f'soma_horas_{j + 1}'].split(':')[0]),
                            minutes=int(
                                relatorio.locacoes[f'locacao_{i + 1}']['entradas_e_saidas'][
                                    f'soma_horas_{j + 1}'].split(':')[1]))

    return formatar_horas(n_horas)


# ----------------------------------------------------------------------------------------------------------------------


# ------------------------------- Formatação para o reusmo do de horas do mês ------------------------------------------
def formatar_horas(horas):
    if horas != timedelta(days=0):
        h = horas.days * 24 + horas.seconds // 3600
        m = (horas.seconds % 3600) / 60
        return f'{h}h{m:.0f}min'
    else:
        h = horas.seconds // 3600
        m = (horas.seconds % 3600) / 60
        return f'{h}h{m:.0f}min'


# ----------------------------------------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------


# ------------------------------- Função para testar o aviso de disponibilidades ---------------------------------------
def teste_aviso(hora_login, usuario, id_usuario):
    dia_limite = DiaLimite.objects.get(id=1)
    diferenca = timedelta(hours=hora_login.hour, minutes=hora_login.minute, seconds=hora_login.second)
    diferenca -= timedelta(hours=datetime.now().hour, minutes=datetime.now().minute, seconds=datetime.now().second)

    if datetime.now().month != 12:
        consulta = Disponibilidade.objects.filter(professor=usuario, mes=datetime.now().month + 1)
    else:
        consulta = Disponibilidade.objects.filter(professor=usuario, mes=1, ano=datetime.now().year + 1)

    if len(consulta) == 0:
        if datetime.now().day > dia_limite.dia_limite - 5:
            if User.objects.filter(pk=id_usuario, groups__name='Professor').exists():
                if diferenca == timedelta(days=0, hours=3):
                    print('True')

                    return True

    return False


# ----------------------------------------------------------------------------------------------------------------------


# --------------------------- Função apra testar o aviso de disponibilidade da monitoria -------------------------------
def teste_aviso_monitoria(hora_login, monitor, dia_limite_acampamento, dia_limite_hotelaria):
    agora = datetime.now()
    dia_acampamento = dia_limite_acampamento.dia_limite_acampamento
    dia_hotelaria = dia_limite_hotelaria.dia_limite_hotelaria
    tempo_logado = timedelta(hours=agora.hour, minutes=agora.minute, seconds=agora.second)
    tempo_logado -= timedelta(hours=hora_login.hour, minutes=hora_login.minute, seconds=hora_login.second)
    mensagem_acampamento = mensagem_hotelaria = None

    # Consultando as disponibilidadess
    if datetime.now().month != 12:
        consulta_acampamento = DisponibilidadeAcampamento.objects.filter(monitor=monitor, mes=agora.month + 1)
        consulta_hotelaria = DisponibilidadeHotelaria.objects.filter(monitor=monitor, mes=agora.month + 1)
    else:
        consulta_acampamento = DisponibilidadeAcampamento.objects.filter(monitor=monitor, mes=1, ano=agora.year + 1)
        consulta_hotelaria = DisponibilidadeHotelaria.objects.filter(monitor=monitor, mes=1, ano=agora.year + 1)
    print()
    # Verificando mensagem para o acampamento
    if len(consulta_acampamento) == 0:
        if tempo_logado.seconds < 30:
            if dia_acampamento - 5 < agora.day < dia_acampamento:
                mensagem_acampamento = f'''
                    Atenção, você tem até o dia {dia_acampamento} para lançar a disponibilidade do <b>acampamento</b>
                    para o mês seguinte. Por favor vá em <b>Escala</b> &rarr; <b>Disponibilidade</b> e informe os dias
                    que estará disponiveis para o <b>acampamento</b>.
                '''
            elif agora.day > dia_acampamento:
                mensagem_acampamento = f'''
                    Atenção, você perdeu a data para lançar a disponibilidade do <b>acampamento</b> para o mês seguinte.
                    Por favor entre em contato com o coordenador do seu setor, para que consiga informar a 
                    disponibilidade do mês seguinte.
                '''
    # Verificando mensagem para a hotelaria
    if len(consulta_hotelaria) == 0:
        if tempo_logado.seconds < 30:
            if dia_hotelaria - 5 < agora.day < dia_hotelaria:
                mensagem_hotelaria = f'''
                    Atenção, você tem até o dia {dia_hotelaria} para
                    lançar a disponibi lidade da <b>hotelaria</b> para o mês seguinte. Por favor
                    vá em <b>Escala</b> &rarr; <b>Disponibilidade</b> e informe os dias que estará
                    disponiveis para a <b>hotelaria</b>.
                '''
            elif agora.day > dia_hotelaria:
                mensagem_hotelaria = f'''
                    Atenção, você perdeu a data para lançar a disponibilidade da <b>hotelaria</b>
                    para o mês seguinte. Por favor entre em contato com o coordenador do seu
                    setor, para que consiga informar a disponibilidade do mês seguinte.
                '''
    return mensagem_acampamento, mensagem_hotelaria
