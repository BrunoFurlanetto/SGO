from datetime import datetime, timedelta

from django import template

from orcamento.models import ValoresPadrao

register = template.Library()


@register.filter
def pegar_taxa(id_taxa):
    taxa = ValoresPadrao.objects.get(id_taxa__icontains=id_taxa)
    padrao = minimo = maximo = ''

    if 'comissao' in id_taxa or 'taxa_comercial' in id_taxa or 'onibus' in id_taxa:
        if 'comissao' in id_taxa or 'taxa_comercial' in id_taxa:
            padrao = f'{taxa.valor_padrao}%'.replace('.', ',')
            minimo = f'{taxa.valor_minimo}%'.replace('.', ',')
            maximo = f'{taxa.valor_maximo}%'.replace('.', ',')

        if 'onibus' in id_taxa:
            padrao = int(taxa.valor_padrao)
            minimo = int(taxa.valor_minimo)
            maximo = int(taxa.valor_maximo)

        return f'''
            value={padrao} data-valor_default={padrao} data-valor_inicial={padrao}
            data-valor_alterado={padrao} data-teto={maximo} data-piso={minimo}
        '''

    hoje = datetime.today().date()
    padrao = (hoje + timedelta(days=int(taxa.valor_padrao))).strftime('%Y-%m-%d')

    return f'''
        value={padrao} data-valor_default={padrao} data-valor_inicial={padrao}
        data-valor_alterado={padrao}
    '''


@register.filter
def fone(fone):
    return f'({fone[0:2]}) {fone[2:3]} {fone[3:7]} - {fone[7:]}'


@register.filter
def substituir_ponto(valor):
    return str(valor).replace('.', ',')


@register.filter
def formatar_porcentagem(valor):
    return f'{valor:.2f}%'.replace('.', ',')

@register.filter
def somar_float(valor1, valor2):
    return valor1 + valor2
