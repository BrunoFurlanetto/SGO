from cadastro.models import RelatorioDeAtendimentoColegioCeu
from peraltas.models import ClienteColegio


def pegar_atividades_relatorio(colegio):
    colegio_avaliando = ClienteColegio.objects.get(nome_fantasia=colegio)
    relatorio_colegio = RelatorioDeAtendimentoColegioCeu.objects.get(instituicao=colegio_avaliando)
    atividades = {}

    for i in range(1, len(relatorio_colegio.atividades) + 1):
        ativ = relatorio_colegio.atividades[f'atividade_{i}']['atividade']
        data_ativ = relatorio_colegio.atividades[f'atividade_{i}']['data_e_hora'].split('T')[0]

        atividades[f'atividade_{i}'] = {'atividade': ativ, 'data': data_ativ}

    print(atividades['atividade_1'].values())
