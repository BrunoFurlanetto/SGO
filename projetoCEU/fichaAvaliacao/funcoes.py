import datetime

from cadastro.models import RelatorioDeAtendimentoColegioCeu
from ceu.models import Professores, Atividades
from ordemDeServico.models import OrdemDeServico
from peraltas.models import ClienteColegio, Responsavel, RelacaoClienteResponsavel, Vendedor


def pegar_dados_colegio(colegio):
    colegio_avaliando = ClienteColegio.objects.get(nome_fantasia=colegio)
    ordem_colegio = OrdemDeServico.objects.get(instituicao=colegio_avaliando, ficha_avaliacao=False)
    dados_colegio = {}

    dados_colegio = {'instituicao': colegio_avaliando.id,
                     'cidade': ordem_colegio.cidade,
                     'n_alunos': ordem_colegio.n_participantes,
                     'n_professores': ordem_colegio.n_professores,
                     'serie': ordem_colegio.serie,
                     'id_vendedor': ordem_colegio.vendedor.id,
                     'nome_vendedor': ordem_colegio.vendedor.usuario.get_full_name()}

    return dados_colegio


def pegar_dados_avaliador(colegio):
    colegio_avaliando = ClienteColegio.objects.get(nome_fantasia=colegio)
    ordem_colegio = OrdemDeServico.objects.get(instituicao=colegio_avaliando, ficha_avaliacao=False)
    responsavel = Responsavel.objects.get(nome=ordem_colegio.responsavel_grupo)
    dados_responsavel = {}

    dados_responsavel = {'id': responsavel.id,
                         'nome': responsavel.nome,
                         'cargo': responsavel.cargo,
                         'email': responsavel.email_responsavel_evento, }

    return dados_responsavel


def pegar_atividades_relatorio(colegio):
    colegio_avaliando = ClienteColegio.objects.get(nome_fantasia=colegio)
    relatorio_colegio = RelatorioDeAtendimentoColegioCeu.objects.get(instituicao=colegio_avaliando,
                                                                     ficha_avaliacao=False)
    atividades = []

    for i in range(1, len(relatorio_colegio.atividades) + 1):
        if relatorio_colegio.atividades[f'atividade_{i}']['atividade'] not in atividades:
            atividades.append(relatorio_colegio.atividades[f'atividade_{i}']['atividade'])

    return atividades


def pegar_professores_relatorio(colegio):
    colegio_avaliando = ClienteColegio.objects.get(nome_fantasia=colegio)
    relatorio_colegio = RelatorioDeAtendimentoColegioCeu.objects.get(instituicao=colegio_avaliando,
                                                                     ficha_avaliacao=False)
    professores = []

    for i in relatorio_colegio.equipe:
        professores.append(relatorio_colegio.equipe[i])

    return professores


# --------------------------------------------- Salvando avalia????o ----------------------------------------------------
def salvar_avaliacoes_vendedor(dados, ficha):
    vendedora = Vendedor.objects.get(id=int(ficha.nome_vendedor.id))
    media = (int(dados.get('cordialidade_vendedor')) +
             int(dados.get('agilidade_vendedor')) +
             int(dados.get('clareza_vendedor'))) / 3

    vendedora.n_avaliacoes += 1
    vendedora.nota = (vendedora.nota + media) / vendedora.n_avaliacoes
    vendedora.save()

    dados_avaliacao = {'vendedora': vendedora.usuario.get_full_name(),
                       'cordialidade': dados.get('cordialidade_vendedor'),
                       'agilidade': dados.get('agilidade_vendedor'),
                       'clareza_ideias': dados.get('clareza_vendedor'),
                       'media': media}

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

        avaliacoes[f'atividade_{i}'] = {'atividade': atividade.atividade,
                                        'avaliacao': dados.get(f'avaliacao_atividade_{i}')}

    ficha.avaliacoes_atividades = avaliacoes


def salvar_avaliacoes_professores(dados, ficha):
    teste_professores = 0
    avaliacoes = {}

    for chave in dados:
        if 'professor' in chave:
            teste_professores += 1

    n_professores = int((teste_professores - 1) / 4)

    for i in range(1, n_professores + 1):
        professor = Professores.objects.get(usuario__first_name=dados.get(f'professor_{i}'))
        media = (int(dados.get(f'dominio_professor_{i}')) +
                 int(dados.get(f'cordialidade_professor_{i}')) +
                 int(dados.get(f'desenvoltura_professor_{i}'))) / 3

        professor.n_avaliacoes += 1
        professor.nota = (professor.nota + media) / professor.n_avaliacoes
        professor.save()

        avaliacoes[f'professor_{i}'] = {'professor': professor.usuario.get_full_name(),
                                        'dominio': dados.get(f'dominio_professor_{i}'),
                                        'cordialidade': dados.get(f'cordialidade_professor_{i}'),
                                        'desenvoltura': dados.get(f'desenvoltura_professor_{i}'),
                                        'media': media}

    ficha.avaliacoes_professores = avaliacoes
