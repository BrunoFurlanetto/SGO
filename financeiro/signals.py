from django.contrib.auth.models import User
from django.db.models.signals import pre_delete
from django.dispatch import receiver

from financeiro.models import PlanosPagamento, FichaFinanceira, DadosEvento
from peraltas.models import Vendedor
from financeiro.models import TiposPagamentos


@receiver(pre_delete, sender=User)
def redefinir_colaborador(sender, instance, **kwargs):
    diretoria = Vendedor.objects.filter(usuario__groups__name__icontains='diretoria')[0]
    eventos_alteradors = DadosEvento.objects.filter(colaborador=instance).update(colaborador=diretoria.usuario)
    FichaFinanceira.objects.filter(dados_evento__id__in=[evento.id for evento in eventos_alteradors]).update()


@receiver(pre_delete, sender=TiposPagamentos)
def redefenir_tipo_pagamento(sender, instance, **kwargs):
    planos_afetados = PlanosPagamento.objects.filter(tipo_pagamento=instance)

    FichaFinanceira.objects.filter(tipo_pagamento__id__in=[plano.id for plano in planos_afetados]).update(
        observacoes_ficha_financeira='SGO: Necessário redefinir o tipo de pagamento na seção "Planos de pagamento"',
        autorizado_diretoria=False
    )
