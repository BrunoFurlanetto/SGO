from django import template

register = template.Library()


@register.filter()
def cnpj(valor):
    return f'{valor[0:2]}.{valor[2:5]}.{valor[5:8]}/{valor[8:12]}-{valor[12:14]}'


@register.filter()
def phone(valor):
    return f'({valor[0:2]}) {valor[2]} {valor[3:7]}-{valor[7:12]}'