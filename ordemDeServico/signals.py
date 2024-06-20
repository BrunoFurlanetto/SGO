from django.db.models.signals import post_save
from django.dispatch import receiver

from ordemDeServico.models import OrdemDeServico
from peraltas.models import Eventos


@receiver(post_save, sender=OrdemDeServico)
def atualizar_evento(sender, instance, created, **kwargs):
    if created:
        instance.ficha_de_evento.os = True
        instance.ficha_de_evento.save()

    evento = Eventos.objects.get(ficha_de_evento=instance.ficha_de_evento.id)

    evento.ordem_de_servico = instance
    evento.colaborador = instance.vendedor
    evento.data_check_in = instance.check_in.date()
    evento.hora_check_in = instance.check_in.time()
    evento.data_check_out = instance.check_out.date()
    evento.hora_check_out = instance.check_out.time()
    evento.qtd_confirmado = instance.n_participantes
    evento.data_preenchimento = instance.data_preenchimento
    evento.estagio_evento = 'ordem_servico'
    evento.tipo_evento = instance.tipo
    evento.dias_evento = (instance.check_out.date() - instance.check_in.date()).days + 1
    evento.adesao = (instance.n_participantes / evento.qtd_previa) * 100

    evento.save()
