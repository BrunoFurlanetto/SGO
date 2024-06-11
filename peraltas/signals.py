from django.contrib.auth.models import User
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from datetime import date

from ordemDeServico.models import OrdemDeServico
from projetoCEU.envio_de_emails import EmailSender
from .models import FichaDeEvento, Eventos


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


@receiver(post_save, sender=FichaDeEvento)
def atualizar_evento(sender, instance, **kwargs):
    try:
        evento = Eventos.objects.get(ficha_de_evento=instance.id)
    except Eventos.DoesNotExist:
        veio_ano_anterior = FichaDeEvento.objects.filter(
            cliente=instance.cliente.id,
            os=True,
            check_in__year=instance.check_in.year - 1,
        ).exists()

        Eventos.objects.create(
            ficha_de_evento=instance,
            colaborador=instance.vendedora,
            cliente=instance.cliente,
            data_check_in=instance.check_in.date(),
            data_check_out=instance.check_out.date(),
            hora_check_in=instance.check_in.astimezone().time(),
            hora_check_out=instance.check_out.astimezone().time(),
            qtd_previa=instance.qtd_convidada,
            qtd_confirmado=0,
            data_preenchimento=instance.data_preenchimento,
            estagio_evento='pre_reserva',
            tipo_evento='Colégio' if instance.produto.colegio else 'Empresa',
            dias_evento=(instance.check_out.date() - instance.check_in.date()).days + 1,
            produto_peraltas=instance.produto,
            produto_corporativo=instance.produto_corporativo,
            adesao=0.0,
            veio_ano_anterior=veio_ano_anterior
        )
    else:
        if not evento.ordem_de_servico:
            if instance.pre_reserva and not instance.agendado:
                estagio_evento = 'pre_reserva'
            elif instance.pre_reserva and instance.agendado:
                estagio_evento = 'confirmado'
            else:
                estagio_evento = 'ficha_evento'
        else:
            estagio_evento = 'ordem_servico'

        evento.colaborador = instance.vendedora
        evento.data_check_in = instance.check_in.date()
        evento.hora_check_in = instance.check_in.astimezone().time()
        evento.data_check_out = instance.check_out.date()
        evento.hora_check_out = instance.check_out.astimezone().time()
        evento.qtd_previa = instance.qtd_convidada
        evento.qtd_confirmado = instance.qtd_confirmada if instance.qtd_confirmada else 0
        evento.data_preenchimento = instance.data_preenchimento
        evento.estagio_evento = estagio_evento
        evento.codigo_pagamento = instance.codigos_app.eficha if instance.codigos_app else ''
        evento.tipo_evento = 'Colégio' if instance.produto.colegio else 'Empresa'
        evento.dias_evento = (instance.check_out.date() - instance.check_in.date()).days + 1
        evento.produto_peraltas = instance.produto
        evento.produto_corporativo = instance.produto_corporativo
        evento.adesao = instance.adesao if instance.adesao else 0.0
        evento.save()


@receiver(post_save, sender=FichaDeEvento)
def envio_emails(sender, instance, created, **kwargs):
    if not instance.pre_reserva and not created:
        operacional = User.objects.filter(groups__name='Operacional')
        lista_emails = set()

        for grupo in [operacional]:
            for colaborador in grupo:
                lista_emails.add(colaborador.email)

        EmailSender(list(lista_emails)).mensagem_alteracao_ficha(
            instance.vendedora,
            instance.cliente,
            instance
        )


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
