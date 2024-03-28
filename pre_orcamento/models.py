from django.utils import timezone
from django.contrib.auth.models import User
from django.db import models

from ceu.models import Atividades
from orcamento.models import StatusOrcamento
from peraltas.models import PerfilsParticipantes, ProdutosPeraltas, AtividadesEco


def status_default():
    return StatusOrcamento.objects.get(status__icontains='aberto')


def default_validade():
    return timezone.now() + timezone.timedelta(days=20)


class PreCadastro(models.Model):
    cnpj = models.CharField(max_length=18, unique=True, verbose_name='CNPJ')
    nome_colegio = models.CharField(max_length=255, verbose_name='Nome do colégio')
    nome_responsavel = models.CharField(max_length=255, verbose_name='Nome do responsável')
    telefone_responsavel = models.CharField(max_length=255, verbose_name='Telefone do responsável')

    def __str__(self):
        return self.nome_colegio


class ColaboradorExterno(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Usuário')
    telefone = models.CharField(max_length=11, verbose_name='Telefone')

    def __str__(self):
        return self.usuario.get_full_name()


class PreOrcamento(models.Model):
    tipo_viagem_choices = (
        ('', ''),
        ('lazer', 'Lazer'),
        ('estudo', 'Estudo'),
    )

    cliente = models.ForeignKey(PreCadastro, on_delete=models.CASCADE, verbose_name='Cliente')
    colaborador = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Colaborador')
    serie_grupo = models.ForeignKey(
        PerfilsParticipantes,
        on_delete=models.DO_NOTHING,
        verbose_name='Série do grupo',
        null=True, blank=True
    )
    tipo_pacote = models.ForeignKey(
        ProdutosPeraltas,
        on_delete=models.DO_NOTHING,
        verbose_name='Tipo de pacote',
        null=True, blank=True
    )
    tipo_viagem = models.CharField(max_length=6, verbose_name='Tipo de viagem', default='', choices=tipo_viagem_choices)
    atividades_ceu_sugeridas = models.ManyToManyField(
        Atividades,
        verbose_name='Atividades CEU sugeridas',
        related_name='atividades_ceu_sugeridas',
        blank=True,
    )
    atividades_peraltas_sugeridas = models.ManyToManyField(
        AtividadesEco,
        verbose_name='Atividades Peraltas sugeridas',
        related_name='atividades_peraltas_sugeridas',
        blank=True,
    )
    atividades_ceu_aceitas = models.ManyToManyField(
        Atividades,
        verbose_name='Atividades CEU aceitas',
        related_name='atividades_ceu_aceitas',
        blank=True,
    )
    atividades_peraltas_aceitas = models.ManyToManyField(
        AtividadesEco,
        verbose_name='Atividades Peraltas aceitas',
        related_name='atividades_peraltas_aceitas',
        blank=True,
    )
    data_preenchimento = models.DateField(default=timezone.now, verbose_name='Data de preenchimento', editable=False)
    validade = models.DateField(default=default_validade)
    status = models.ForeignKey(
        StatusOrcamento,
        verbose_name='Status',
        on_delete=models.DO_NOTHING,
        blank=True, null=True
    )
