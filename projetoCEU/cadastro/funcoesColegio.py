from ceu.models import Professores, Atividades
from ordemDeServico.models import OrdemDeServico


def pegar_colegios_no_ceu():
    fichas_de_evento = OrdemDeServico.objects.filter(tipo='Colégio').filter(relatorio_ceu_entregue=False)
    colegios = []

    for ficha in fichas_de_evento:
        colegios.append(ficha.instituicao)

    return colegios


def pegar_empresas_no_ceu():
    fichas_de_evento = OrdemDeServico.objects.filter(tipo='Empresa').filter(relatorio_ceu_entregue=False)
    empresas = []

    for ficha in fichas_de_evento:
        empresas.append(ficha.instituicao)

    return empresas

def pegar_informacoes_cliente(cliente):
    ficha = OrdemDeServico.objects.get(instituicao=cliente)

    info = {'cliente': {
        'serie': ficha.serie,
        'responsaveis': ficha.n_professores,
        'previa': ficha.n_participantes,
        'coordenador_peraltas': ficha.monitor_responsavel.id,
        'atividades': ficha.atividades_ceu,
        'locacoes': ficha.loacao_ceu
    }}

    return info
