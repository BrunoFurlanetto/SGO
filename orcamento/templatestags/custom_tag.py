from datetime import datetime, timedelta

from django import template

from orcamento.models import ValoresPadrao

register = template.Library()

@register.filter
def pegar_taxa(id_taxa):
    taxa = ValoresPadrao.objects.get(id_taxa=id_taxa).valor

    if id_taxa == 'comissao' or id_taxa == 'taxa_comercial':
        taxa = str(taxa).replace('.', ',')
        taxa = f'{taxa}%'

    if id_taxa == 'minimo_onibus':
        taxa = int(taxa)

    if id_taxa == 'data_pagamento':
        hoje = datetime.today().date()
        taxa = (hoje + timedelta(days=int(taxa))).strftime('%Y-%m-%d')

    return taxa
