from django import template

register = template.Library()


@register.filter
def get_obs_field(form, field_name):
    obs_field_name = f"{field_name}_obs"

    try:
        return form[obs_field_name]  # Acessa o campo do formulário corretamente
    except KeyError:
        return None
