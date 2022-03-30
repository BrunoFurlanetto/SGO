from datetime import datetime, timedelta

from cadastro.funcoesPublico import pegar_professores
from ceu.models import Professores, Atividades, Locaveis
from ordemDeServico.models import OrdemDeServico


def pegar_colegios_no_ceu():
    Ordens_de_servico = OrdemDeServico.objects.filter(tipo='Colégio').filter(relatorio_ceu_entregue=False)
    colegios = []

    for ordem in Ordens_de_servico:
        if ordem.atividades_ceu or ordem.loacao_ceu:
            colegios.append({'id': ordem.id,
                             'instituicao': ordem.instituicao})

    return colegios


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
    horas_totais = timedelta()
    n_locacoes = 0

    for campo in dados:
        if 'qtd' in campo:
            n_locacoes += 1

        for i in range(1, n_locacoes + 1):
            local = Locaveis.objects.get(id=int(dados.get(f'loc_{i}')))
            professor = Professores.objects.get(id=dados.get(f'prf_loc_{i}'))
            check_in = dados.get(f'check_in_{i}')
            check_out = dados.get(f'check_out_{i}')
            horas_parciais = somar_horas_parciais(check_in, check_out)
            horas_totais += horas_parciais
            print(horas_totais)
            participantes = dados.get(f'qtd_loc_{i}')

            # ------------------------------------ Salvando as atividades ----------------------------------------------
            dados_locacoes[f'locacao_{i}'] = {'espaco': local.local.estrutura,
                                              'professor': professor.usuario.first_name,
                                              'check_in': check_in,
                                              'check_out': check_out,
                                              'soma_horas': str(horas_parciais),
                                              'participantes': participantes}

    relatorio.horas_totais_locacoes = horas_totais
    relatorio.locacoes = dados_locacoes


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
    professor = Professores.objects.get(id=int(dados.get('coordenador')))
    professores = {'coordenador': professor.usuario.first_name}

    for i in range(2, 5):
        if dados.get(f'professor_{i}') != '':
            professor = Professores.objects.get(id=int(dados.get(f'professor_{i}')))
            professores[f'professor_{i}'] = professor.usuario.first_name

    relatorio.equipe = professores


# ----------------------------------------------------------------------------------------------------------------------
def somar_horas_parciais(entrada, saida):
    f = '%Y-%m-%dT%H:%M'
    diferenca = (datetime.strptime(str(saida), f) - datetime.strptime(str(entrada), f))

    return diferenca
