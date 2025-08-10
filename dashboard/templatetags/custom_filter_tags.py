from datetime import datetime

from django import template

register = template.Library()


@register.filter(name='substituir_ponto')
def substituir_ponto(valor):
    print(valor)
    return str(valor).replace('.', ',')

@register.filter(name='alerta_preenchimento')
def alerta_preenchimento(valor):
    data_aprovacao_cliente = valor
    print((datetime.today().date() - data_aprovacao_cliente).days, '<<<<-----')
    if (datetime.today().date() - data_aprovacao_cliente).days < 1:
        return 'bg-success'
    elif (datetime.today().date() - data_aprovacao_cliente).days < 2:
        return 'bg-warning'
    else:
        return 'bg-danger'
