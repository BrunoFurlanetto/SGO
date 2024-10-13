from django import template

from peraltas.models import EscalaAcampamento

register = template.Library()


@register.simple_tag
def soma_valor_nivel(id_escala, nivel):

    return EscalaAcampamento.soma_valor_diaria_nivel(id_escala, nivel)


@register.filter
def get_attr(obj, attr):
    # Permite o acesso dinâmico de atributos com "dot notation"
    attrs = attr.split('.')
    for at in attrs:
        obj = getattr(obj, at)
    return obj
