import datetime

from cadastro.models import RelatorioDeAtendimentoColegioCeu
from ceu.models import Professores, Atividades
from ordemDeServico.models import OrdemDeServico
from peraltas.models import ClienteColegio, Responsavel, RelacaoClienteResponsavel, Vendedor


def pegar_dados_colegio(id_ordem):
    ordem_colegio = OrdemDeServico.objects.get(pk=id_ordem)
    dados_colegio = {}

    dados_colegio = {
        'instituicao': ordem_colegio.ficha_de_evento.cliente.id,
        'cidade': ordem_colegio.cidade,
        'n_alunos': ordem_colegio.n_participantes,
        'n_professores': ordem_colegio.n_professores,
        'serie': ordem_colegio.serie,
        'id_vendedor': ordem_colegio.vendedor.id,
        'nome_vendedor': ordem_colegio.vendedor.usuario.get_full_name()
    }

    return dados_colegio


def pegar_dados_avaliador(id_ordem):
    ordem_colegio = OrdemDeServico.objects.get(pk=id_ordem)
    responsavel = Responsavel.objects.get(pk=ordem_colegio.ficha_de_evento.responsavel_evento.id)
    dados_responsavel = {}

    dados_responsavel = {
        'id': responsavel.id,
        'nome': responsavel.nome,
        'cargo': responsavel.cargo,
        'email': responsavel.email_responsavel_evento,
    }

    return dados_responsavel


def pegar_atividades_relatorio(id_ordem):
    relatorio_colegio = RelatorioDeAtendimentoColegioCeu.objects.get(ordem__id=id_ordem)
    atividades = []

    for i in range(1, len(relatorio_colegio.atividades) + 1):
        if relatorio_colegio.atividades[f'atividade_{i}']['atividade'] not in atividades:
            atividade = Atividades.objects.get(id=relatorio_colegio.atividades[f'atividade_{i}']['atividade'])
            atividades.append(atividade)

    return atividades


def pegar_professores_relatorio(id_ordem):
    relatorio_colegio = RelatorioDeAtendimentoColegioCeu.objects.get(ordem__id=id_ordem)
    professores = []

    for i in relatorio_colegio.equipe:
        professor = Professores.objects.get(id=relatorio_colegio.equipe[i])
        professores.append({'nome': professor, 'id': professor.id})

    return professores


# --------------------------------------------- Salvando avaliação ----------------------------------------------------
def salvar_avaliacoes_vendedor(dados, ficha):
    vendedora = Vendedor.objects.get(id=int(ficha.nome_vendedor.id))
    media = (int(dados.get('cordialidade_vendedor')) +
             int(dados.get('agilidade_vendedor')) +
             int(dados.get('clareza_vendedor'))) / 3

    vendedora.n_avaliacoes += 1
    vendedora.nota = (vendedora.nota + media) / vendedora.n_avaliacoes
    vendedora.save()

    dados_avaliacao = {
        'vendedora': vendedora.id,
        'cordialidade': dados.get('cordialidade_vendedor'),
        'agilidade': dados.get('agilidade_vendedor'),
        'clareza_ideias': dados.get('clareza_vendedor'),
        'media': media
    }

    ficha.avaliacao_vendedor = dados_avaliacao


def salvar_avaliacoes_atividades(dados, ficha):
    n_atividades = 0
    avaliacoes = {}

    for chave in dados:
        if 'atividade' in chave:
            n_atividades += 1

    n_atividades = int(n_atividades / 2)

    for i in range(1, n_atividades + 1):
        atividade = Atividades.objects.get(atividade=dados.get(f'atividade_{i}'))
        atividade.n_avaliacoes += 1
        atividade.nota = (atividade.nota + int(dados.get(f'avaliacao_atividade_{i}'))) / atividade.n_avaliacoes
        atividade.save()

        avaliacoes[f'atividade_{i}'] = {
            'atividade': atividade.id,
            'avaliacao': dados.get(f'avaliacao_atividade_{i}')
        }

    ficha.avaliacoes_atividades = avaliacoes


def salvar_avaliacoes_professores(dados, ficha, dados_professores):
    avaliacoes = {}

    for i, dado_professor in enumerate(dados_professores, start=1):
        print(i)
        professor = Professores.objects.get(id=dado_professor['id'])
        media = (int(dados.get(f'dominio_professor_{i}')) +
                 int(dados.get(f'cordialidade_professor_{i}')) +
                 int(dados.get(f'desenvoltura_professor_{i}'))) / 3

        professor.n_avaliacoes += 1
        professor.nota = (professor.nota + media) / professor.n_avaliacoes
        professor.save()

        avaliacoes[f'professor_{i}'] = {
            'professor': professor.id,
            'dominio': dados.get(f'dominio_professor_{i}'),
            'cordialidade': dados.get(f'cordialidade_professor_{i}'),
            'desenvoltura': dados.get(f'desenvoltura_professor_{i}'),
            'media': media
        }

    ficha.avaliacoes_professores = avaliacoes
