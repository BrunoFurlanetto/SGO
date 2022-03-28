from cadastro.models import RelatorioDeAtendimentoPublicoCeu
from ceu.models import Atividades, Professores


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
                professor = Professores.objects.get(usuario__first_name=relatorio.atividades[f'atividade_{i}']['professores'][j])
                professores[f'prf{j+1}atv{i}'] = professor.id

        dados = {
            'equipe': equipe,
            'id_data_atendimento': relatorio.data_atendimento,
            'atividades': atividades,
            'horas': horas,
            'professores': professores,
            'observacoes': relatorio.relatorio
        }

        return dados
