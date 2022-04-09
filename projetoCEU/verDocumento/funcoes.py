from cadastro.models import RelatorioDeAtendimentoPublicoCeu, RelatorioDeAtendimentoColegioCeu, \
    RelatorioDeAtendimentoEmpresaCeu
from ceu.models import Atividades, Professores, Locaveis
from ordemDeServico.models import OrdemDeServico


def is_ajax(request):
    return request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest'


def requests_ajax(requisicao):
    if requisicao.get('id_relatorio_publico'):
        relatorio = RelatorioDeAtendimentoPublicoCeu.objects.get(id=int(requisicao.get('id_relatorio_publico')))
        equipe = {}
        atividades = {}
        horas = {}
        professores = {}

        for professor in relatorio.equipe:
            prf = Professores.objects.get(usuario__first_name=relatorio.equipe[f'{professor}'])
            equipe[professor] = prf.id

        for i in range(1, len(relatorio.atividades) + 1):
            atividade = Atividades.objects.get(atividade=relatorio.atividades[f'atividade_{i}']['atividade'])
            atividades[f'ativ{i}'] = atividade.id
            horas[f'horaAtividade_{i}'] = relatorio.atividades[f'atividade_{i}']['data_e_hora'].split(' ')[1]

            for j in range(len(relatorio.atividades[f'atividade_{i}']['professores'])):
                professor = Professores.objects.get(
                    usuario__first_name=relatorio.atividades[f'atividade_{i}']['professores'][j])
                professores[f'prf{j + 1}atv{i}'] = professor.id

        dados = {
            'equipe': equipe,
            'id_data_atendimento': relatorio.data_atendimento,
            'atividades': atividades,
            'horas': horas,
            'professores': professores,
            'observacoes': relatorio.relatorio
        }

        return dados

    if requisicao.get('id_relatorio'):
        if requisicao.get('tipo') == 'Colégio':
            relatorio = RelatorioDeAtendimentoColegioCeu.objects.get(id=int(requisicao.get('id_relatorio')))
        else:
            relatorio = RelatorioDeAtendimentoEmpresaCeu.objects.get(id=int(requisicao.get('id_relatorio')))

        equipe = {}
        professores_atividade = {}
        professores_locacao = {}

        for professor in relatorio.equipe:
            prf = Professores.objects.get(usuario__first_name=relatorio.equipe[f'{professor}'])
            equipe[professor] = prf.id

        if relatorio.atividades:
            for i in range(1, len(relatorio.atividades) + 1):
                for j in range(len(relatorio.atividades[f'atividade_{i}']['professores'])):
                    professor = Professores.objects.get(
                        usuario__first_name=relatorio.atividades[f'atividade_{i}']['professores'][j])
                    professores_atividade[f'prof_{j + 1}_ativ_{i}'] = professor.id

        if relatorio.locacoes:
            for i in range(1, len(relatorio.locacoes) + 1):
                professor = Professores.objects.get(usuario__first_name=relatorio.locacoes[f'locacao_{i}']['professor'])
                professores_locacao[f'prof_loc_{i}'] = professor.id

        dados = {
            'equipe': equipe,
            'atividades': relatorio.atividades,
            'locacoes': relatorio.locacoes,
            'professores_atividade': professores_atividade,
            'professores_locacoes': professores_locacao,
            'relatorio': relatorio.relatorio,
        }

        return dados

    if requisicao.get('id_ordem_de_servico'):
        ordem_de_servico = OrdemDeServico.objects.get(id=int(requisicao.get('id_ordem_de_servico')))

        if ordem_de_servico.atividades_ceu:
            for i in range(1, len(ordem_de_servico.atividades_ceu) + 1):
                atividade = Atividades.objects.get(atividade=ordem_de_servico.atividades_ceu[f'atividade_{i}']['atividade'])
                ordem_de_servico.atividades_ceu[f'atividade_{i}'][f'id_atividade'] = atividade.id

        if ordem_de_servico.locacao_ceu:
            for i in range(1, len(ordem_de_servico.locacao_ceu) + 1):
                local = Locaveis.objects.get(local__estrutura=ordem_de_servico.locacao_ceu[f'locacao_{i}']['espaco'])
                ordem_de_servico.locacao_ceu[f'locacao_{i}']['id_espaco'] = local.id

        dados_ordem_de_servico = {
            'check_in': ordem_de_servico.check_in,
            'check_out': ordem_de_servico.check_out,
            'atividades_ceu': ordem_de_servico.atividades_ceu,
            'locacoes_ceu': ordem_de_servico.locacao_ceu
        }

        return dados_ordem_de_servico
