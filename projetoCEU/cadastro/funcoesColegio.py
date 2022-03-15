from ceu.models import Professores, Atividades
from ordemDeServico.models import OrdemDeServico


def pegar_colegios_no_ceu():
    fichas_de_evento = OrdemDeServico.objects.filter(tipo='Colégio').filter(relatorio_ceu_entregue=False)
    colegios = []

    for ficha in fichas_de_evento:
        colegios.append(ficha.instituicao)

    return colegios


def pegar_informacoes_colegio(colegio):
    professores = Professores.objects.all()
    atividades = Atividades.objects.all()
    ficha = OrdemDeServico.objects.get(instituicao=colegio)
    info = {}
    info_professores = {}
    info_atividades = {}

    for professor in professores:
        info_professores[professor.id] = professor.usuario.first_name

    for atividade in atividades:
        info_atividades[atividade.id] = atividade.atividade

    info['colegio'] = {
        'serie': ficha.serie,
        'responsaveis': ficha.n_professores,
        'previa': ficha.n_participantes,
        'coordenador_peraltas': ficha.monitor_responsavel.id,
        'atividades': ficha.atividades_ceu,
        'locacoes': ficha.loacao_ceu
    }

    info['professores'] = info_professores
    info['atividades'] = info_atividades

    return info
