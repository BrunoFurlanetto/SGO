from django import template

register = template.Library()


@register.filter
def get_obs_field(form, field_name):
    obs_field_name = f"{field_name}_obs"

    try:
        return form[obs_field_name]  # Acessa o campo do formulário corretamente
    except KeyError:
        return None


@register.filter
def get_field(form, index):
    field_name = f'palavra_{index + 1}'
    return form[field_name] if field_name in form.fields else None
