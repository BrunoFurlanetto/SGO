from django import template

from financeiro.models import FichaFinanceira

register = template.Library()


@register.filter
def porcentagem_comissionado(valor):
    return valor * 10


@register.simple_tag
def carregar_cortesias_externas(id_ficha_financeira, id_atividade, alunos_professores):
    ficha = FichaFinanceira.objects.get(pk=id_ficha_financeira)

    for atividade in ficha.dados_evento.cortesias_externas:
        if atividade['id_atividade'] == id_atividade:
            return atividade[alunos_professores]
