from django.db.models.signals import pre_save
from django.dispatch import receiver
from datetime import date

from .models import FichaDeEvento


@receiver(pre_save, sender=FichaDeEvento)
def atualizar_data_preenchimento(sender, instance, **kwargs):
    if not instance.pk:
        print('Que')
        instance.data_preenchimento = date.today()
    else:
        ficha_existente = FichaDeEvento.objects.get(pk=instance.pk)

        if not ficha_existente.agendado and instance.agendado:
            print('Eba')
            instance.data_preenchimento = date.today()

        if ficha_existente.pre_reserva and not instance.pre_reserva:
            print('Oba')
            instance.data_preenchimento = date.today()
