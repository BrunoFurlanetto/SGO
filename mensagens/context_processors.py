from django.contrib.auth.models import User, Permission, Group
from django.db.models import Q


def gerentes_context(request):
    try:
        permissao = Permission.objects.get(codename="aprovar_orcamentos", content_type__app_label="orcamento")

        gerentes = User.objects.filter(
            Q(user_permissions=permissao) |  # Usuários com a permissão diretamente
            Q(groups__permissions=permissao)  # Usuários que têm a permissão via grupo
        ).distinct()

        return {"gerentes": gerentes}

    except Permission.DoesNotExist:
        return {"gerentes": []}
