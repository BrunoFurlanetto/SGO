from django.contrib.auth.models import User
from django.db.models.signals import pre_save, pre_delete
from django.dispatch import receiver
from datetime import date

from .models import FichaDeEvento


@receiver(pre_save, sender=FichaDeEvento)
def atualizar_data_preenchimento(sender, instance, **kwargs):
    if not instance.pk:
        instance.data_preenchimento = date.today()
    else:
        ficha_existente = FichaDeEvento.objects.get(pk=instance.pk)

        if not ficha_existente.agendado and instance.agendado:
            instance.data_preenchimento = date.today()

        if ficha_existente.pre_reserva and not instance.pre_reserva:
            instance.data_preenchimento = date.today()
