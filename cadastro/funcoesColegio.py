from datetime import datetime, timedelta
from random import randint
from django.contrib.auth.models import User, Group

from ceu.models import Professores, Atividades, Locaveis
from ordemDeServico.models import OrdemDeServico

import unidecode


def pegar_colegios_no_ceu():
    return OrdemDeServico.objects.filter(tipo='Colégio').filter(
        relatorio_ceu_entregue=False,
        check_out_ceu__date__lte=datetime.today().date()
    ).order_by('check_out')


def pegar_empresas_no_ceu():
    return OrdemDeServico.objects.filter(tipo='Empresa').filter(
        relatorio_ceu_entregue=False,
        check_out_ceu__date__lte=datetime.today().date()
    ).order_by('check_out')


def pegar_informacoes_cliente(cliente):
    ficha = OrdemDeServico.objects.get(id=int(cliente))

    info = {'cliente': {
        'check_in': ficha.check_in_ceu,
        'check_out': ficha.check_out_ceu,
        'instituicao': ficha.instituicao,
        'serie': ficha.serie,
        'responsaveis': ficha.n_professores,
        'previa': ficha.n_participantes,
        'coordenador_peraltas': ficha.monitor_responsavel.id,
        'atividades': ficha.atividades_ceu,
        'locacoes': ficha.locacao_ceu
    }}

    return info


# ----------------------------------------------------------------------------------------------------------------------

def salvar_atividades_colegio(dados, relatorio):
    dados_atividade = {}
    n_atividades = 1

    while True:
        if dados.getlist(f'ativ_{n_atividades}', None):
            lista_professores = [
                int(id_professor) for id_professor in dados.getlist(f'professores_ativ_{n_atividades}') if
                id_professor != ''
            ]

            dados_atividade[f'atividade_{n_atividades}'] = {
                'atividade': int(dados.getlist(f'ativ_{n_atividades}')[0]),
                'professores': lista_professores,
                'data_e_hora': dados.getlist(f'ativ_{n_atividades}')[1],
                'participantes': int(dados.getlist(f'ativ_{n_atividades}')[2])
            }
        else:
            break

        n_atividades += 1

    relatorio.atividades = dados_atividade


# ----------------------------------------------------------------------------------------------------------------------

def salvar_locacoes_empresa(dados, relatorio):
    dados_locacoes = {}
    horas_totais = timedelta()
    locacao = 1

    while True:
        if dados.getlist(f'loc_{locacao}', None):
            check_in = dados.getlist(f'loc_{locacao}')[1]
            check_out = dados.getlist(f'loc_{locacao}')[2]
            horas_parciais = somar_horas_parciais(check_in, check_out)
            horas_totais += horas_parciais
            participantes = dados.getlist(f'loc_{locacao}')[3]

            # ------------------------------------ Salvando as atividades ----------------------------------------------
            dados_locacoes[f'locacao_{locacao}'] = {
                'espaco': int(dados.getlist(f'loc_{locacao}')[0]),
                'professor': [
                    int(id_professor) for id_professor in dados.getlist(f'professores_locacao_{locacao}')
                    if id_professor != ''
                ],
                'check_in': check_in,
                'check_out': check_out,
                'soma_horas': str(horas_parciais),
                'participantes': participantes
            }
        else:
            break

        locacao += 1

    relatorio.horas_totais_locacoes = horas_totais
    relatorio.locacoes = dados_locacoes


# ----------------------------------------------------------------------------------------------------------------------

def pegar_professores_colegio(dados, j):
    professores = []

    for i in range(1, 6):
        if dados.get(f'prf_{i}_ativ_{j}') is not None and dados.get(f'prf_{i}_ativ_{j}') != '':
            professores.append(int(dados.get(f'prf_{i}_ativ_{j}')))

    return professores


# ----------------------------------------------------------------------------------------------------------------------

def salvar_equipe_colegio(dados, relatorio):
    lista_professores = [int(id_professor) for id_professor in dados.getlist('professores') if id_professor != '']
    professores = {'coordenador': lista_professores.pop(0)}

    for i, id_professor in enumerate(lista_professores, start=2):
        professores[f'professor_{i}'] = id_professor

    relatorio.equipe = professores


# ----------------------------------------------------------------------------------------------------------------------
def somar_horas_parciais(entrada, saida):
    f = '%Y-%m-%dT%H:%M'
    diferenca = (datetime.strptime(str(saida), '%Y-%m-%dT%H:%M') - datetime.strptime(str(entrada), '%Y-%m-%dT%H:%M'))

    return diferenca


# ----------------------------------------------------------------------------------------------------------------------
def criar_usuario_colegio(dados_colegio, id_ordem):
    identificacao = randint(11111, 99999)
    colegio_username = id_ordem
    colegio_password = f'colegio_{unidecode.unidecode(dados_colegio.instituicao.split(" ")[0].capitalize())}'
    colegio_last_name = dados_colegio.instituicao
    colegio_email = f'avaliacao_{unidecode.unidecode(dados_colegio.instituicao.split(" ")[0].lower())}_{identificacao}@fundacaoceu.com'

    user = User.objects.create_user(
        username=colegio_username,
        email=colegio_email,
        password=colegio_password,
        first_name='Colégio - Avaliação',
        last_name=colegio_last_name
    )

    user.save()

    usuario = User.objects.get(id=user.id)
    grupo_colegio = Group.objects.get(name__icontains='colégio')
    usuario.groups.add(grupo_colegio)

    return colegio_email, colegio_password
