from django import template

register = template.Library()


@register.filter(name='substituir_ponto')
def substituir_ponto(valor):
    print(valor)
    return str(valor).replace('.', ',')
