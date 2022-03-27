from datetime import datetime

from cadastro.funcoesPublico import pegar_professores
from ceu.models import Professores, Atividades, Locaveis
from ordemDeServico.models import OrdemDeServico


def pegar_colegios_no_ceu():
    Ordens_de_servico = OrdemDeServico.objects.filter(tipo='Colégio').filter(relatorio_ceu_entregue=False)
    colegios = []

    for ordem in Ordens_de_servico:
        colegios.append({'id': ordem.id,
                         'instituicao': ordem.instituicao})

    return colegios


def pegar_empresas_no_ceu():
    ordens = OrdemDeServico.objects.filter(tipo='Empresa').filter(relatorio_ceu_entregue=False)
    empresas = []

    for ordem in ordens:
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
        'locacoes': ficha.loacao_ceu
    }}

    return info


# ----------------------------------------------------------------------------------------------------------------------

def salvar_atividades_colegio(dados, relatorio):
    dados_atividade = {}
    n_atividades = 0

    for campo in dados:
        if 'qtd' in campo:
            n_atividades += 1

        for i in range(1, n_atividades + 1):
            atividade = Atividades.objects.get(id=int(dados.get(f'ativ_{i}')))
            professores = pegar_professores_colegio(dados, i)
            data_e_hora = dados.get(f'data_hora_ativ_{i}')
            participantes = dados.get(f'qtd_ativ_{i}')

            # ------------------------------------ Salvando as atividades ----------------------------------------------
            dados_atividade[f'atividade_{i}'] = {'atividade': atividade.atividade, 'professores': professores,
                                                 'data_e_hora': data_e_hora, 'participantes': participantes}

    relatorio.atividades = dados_atividade


# ----------------------------------------------------------------------------------------------------------------------

def salvar_locacoes_empresa(dados, relatorio):
    dados_locacoes = {}
    n_locacoes = 0

    for campo in dados:
        if 'qtd' in campo:
            n_locacoes += 1

        for i in range(1, n_locacoes + 1):
            atividade = Locaveis.objects.get(id=int(dados.get(f'loc_{i}')))
            professor = Professores.objects.get(id=dados.get('fprf_loc_{i}'))
            check_in = dados.get(f'check_in{i}')
            check_out = dados.get(f'check_out{i}')
            soma_horas = somar_horas_parciais(check_in, check_out)
            participantes = dados.get(f'qtd_loc_{i}')

            # ------------------------------------ Salvando as atividades ----------------------------------------------
            dados_atividade[f'atividade_{i}'] = {'atividade': atividade.atividade, 'professores': professores,
                                                 'data_e_hora': data_e_hora, 'participantes': participantes}

    relatorio.atividades = dados_atividade


# ----------------------------------------------------------------------------------------------------------------------

def pegar_professores_colegio(dados, j):
    professores = []

    for i in range(1, 6):
        if dados.get(f'prf_{i}_ativ_{j}') is not None and dados.get(f'prf_{i}_ativ_{j}') != '':
            professor = Professores.objects.get(id=int(dados.get(f'prf_{i}_ativ_{j}')))
            professores.append(professor.usuario.first_name)

    return professores


# ----------------------------------------------------------------------------------------------------------------------

def salvar_equipe_colegio(dados, relatorio):
    professores = {'coordenador': dados.get('coordenador')}

    for i in range(2, 5):
        if dados.get(f'professor_{i}') != '':
            professor = Professores.objects.get(id=int(dados.get(f'professor_{i}')))
            professores[f'professor_{i}'] = professor.usuario.first_name

    relatorio.equipe = professores


# ----------------------------------------------------------------------------------------------------------------------
def somar_horas_parciais(entrada, saida):
    f = '%Y-%m-%dT%H:%M:%S'
    dif = (datetime.strptime(saida, f) - datetime.strptime(entrada, f)).total_seconds()
    print(dif)
