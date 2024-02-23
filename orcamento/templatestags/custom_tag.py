from datetime import datetime, timedelta

from django import template

from orcamento.models import ValoresPadrao

register = template.Library()


@register.filter
def pegar_taxa(id_taxa):
    taxa = ValoresPadrao.objects.get(id_taxa=id_taxa).valor

    if 'comissao' in id_taxa or 'taxa_comercial' in id_taxa:
        taxa = str(taxa).replace('.', ',')
        taxa = f'{taxa}%'

    if 'onibus' in id_taxa:
        taxa = int(taxa)

    if id_taxa == 'data_pagamento':
        hoje = datetime.today().date()
        taxa = (hoje + timedelta(days=int(taxa))).strftime('%Y-%m-%d')

    return taxa


@register.filter
def fone(fone):
    return f'({fone[0:2]}) {fone[2:3]} {fone[3:7]} - {fone[7:]}'


@register.filter
def substituir_ponto(valor):
    return str(valor).replace('.', ',')