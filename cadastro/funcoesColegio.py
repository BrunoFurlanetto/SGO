from datetime import datetime, timedelta
from random import randint
from django.contrib.auth.models import User, Group

from ceu.models import Professores, Atividades, Locaveis
from ordemDeServico.models import OrdemDeServico

import unidecode


def pegar_colegios_no_ceu():
    ordens_de_servico = OrdemDeServico.objects.filter(tipo='Colégio').filter(
        relatorio_ceu_entregue=False,
        check_out_ceu__date__lte=datetime.today().date()
    )

    return ordens_de_servico


def pegar_empresas_no_ceu():
    ordens = OrdemDeServico.objects.filter(tipo='Empresa').filter(relatorio_ceu_entregue=False)
    empresas = []

    for ordem in ordens:
        if ordem.atividades_ceu or ordem.locacao_ceu:
            empresas.append({'id': ordem.id,
                             'instituicao': ordem.instituicao})

    return empresas


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
    n_locacoes = 0

    for campo in dados:
        if 'qtd_loc' in campo:
            n_locacoes += 1

        for i in range(1, n_locacoes + 1):
            check_in = dados.get(f'check_in_{i}')
            check_out = dados.get(f'check_out_{i}')
            horas_parciais = somar_horas_parciais(check_in, check_out)
            horas_totais += horas_parciais
            print(horas_totais)
            participantes = dados.get(f'qtd_loc_{i}')

            # ------------------------------------ Salvando as atividades ----------------------------------------------
            dados_locacoes[f'locacao_{i}'] = {
                'espaco': int(dados.get(f'loc_{i}')),
                'professor': int(dados.get(f'prf_loc_{i}')),
                'check_in': check_in,
                'check_out': check_out,
                'soma_horas': str(horas_parciais),
                'participantes': participantes
            }

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
    diferenca = (datetime.strptime(str(saida), f) - datetime.strptime(str(entrada), f))

    return diferenca


# ----------------------------------------------------------------------------------------------------------------------
def criar_usuario_colegio(dados_colegio):
    identificacao = randint(11111, 99999)
    colegio_username = f'colegio_{unidecode.unidecode(dados_colegio.instituicao.split(" ")[0].lower())}_{identificacao}'
    colegio_password = f'colegio_{unidecode.unidecode(dados_colegio.instituicao.split(" ")[0].capitalize())}'
    colegio_last_name = dados_colegio.instituicao
    colegio_email = f'avaliacao_{unidecode.unidecode(dados_colegio.instituicao.split(" ")[0].lower())}_{identificacao}@fundacaoceu.com'

    user = User.objects.create_user(username=colegio_username, email=colegio_email,
                                    password=colegio_password, first_name='Colégio',
                                    last_name=colegio_last_name)

    user.save()

    usuario = User.objects.get(id=user.id)
    grupo_colegio = Group.objects.get(name='Colégio')
    usuario.groups.add(grupo_colegio)

    return colegio_email, colegio_password
