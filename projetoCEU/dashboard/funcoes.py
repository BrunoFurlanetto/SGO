from django.contrib.auth.models import User
from ceu.models import Professores
from datetime import datetime, timedelta
from escala.models import Disponibilidade
from unidecode import unidecode


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
                if professor_logado.usuario.first_name in relatorio.atividades[f'atividade_{i+1}']['professores']:
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
                if professor_logado.usuario.first_name in relatorio.locacoes[f'locacao_{i+1}']['professor']:
                    for j in range(int(len(relatorio.locacoes[f'locacao_{i+1}']['entradas_e_saidas'])/3)):
                        n_horas += timedelta(
                            hours=int(
                                relatorio.locacoes[f'locacao_{i+1}']['entradas_e_saidas'][f'soma_horas_{j+1}'].split(':')[0]),
                            minutes=int(
                                relatorio.locacoes[f'locacao_{i+1}']['entradas_e_saidas'][f'soma_horas_{j+1}'].split(':')[1]))

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
    diferenca = timedelta(hours=hora_login.hour, minutes=hora_login.minute, seconds=hora_login.second)
    diferenca -= timedelta(hours=datetime.now().hour, minutes=datetime.now().minute, seconds=datetime.now().second)

    if datetime.now().month != 12:
        consulta = Disponibilidade.objects.filter(professor=usuario, mes=datetime.now().month + 1)
    else:
        consulta = Disponibilidade.objects.filter(professor=usuario, mes=1, ano=datetime.now().year + 1)

    if len(consulta) == 0:

        if datetime.now().day > 20:

            if User.objects.filter(pk=id_usuario, groups__name='Professor').exists():
                if diferenca == timedelta(days=0, hours=3):
                    print('True')
                    return True

    return False
# ----------------------------------------------------------------------------------------------------------------------
