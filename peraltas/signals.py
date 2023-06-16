from django.db.models.signals import pre_save
from django.dispatch import receiver
from datetime import date

from .models import FichaDeEvento


@receiver(pre_save, sender=FichaDeEvento)
def atualizar_data_preenchimento(sender, instance, **kwargs):
    print(instance.agendado, instance.pre_reserva)
    if not instance.pk or instance.agendado or not instance.pre_reserva:
        instance.data_preenchimento = date.today()
