from django import forms
from django.db import models

from peraltas.models import ClienteColegio, Responsavel


class OrcamentoMonitor(models.Model):
    nome_monitoria = models.CharField(max_length=100)
    descricao_monitoria = models.TextField(blank=True)
    valor = models.DecimalField(decimal_places=2, max_digits=5, default=0.00)


class OrcamentoOpicional(models.Model):
    nome = models.CharField(max_length=100)
    descricao = models.TextField(default='Opcional combinado com o cliente')
    valor = models.DecimalField(decimal_places=2, max_digits=5, default=0.00)


class OrcamentoPeriodo(models.Model):
    nome_periodo = models.CharField(max_length=255)
    valor = models.DecimalField(decimal_places=2, max_digits=5, default=0.00)
    descricao = models.TextField(blank=True)
    id = models.CharField(max_length=11, unique=True, primary_key=True)


class OrcamentoAlimentacao(models.Model):
    tipo_alimentacao = models.CharField(max_length=100)
    descricao = models.TextField(blank=True)
    valor = models.DecimalField(decimal_places=2, max_digits=5, default=0.00)


class Orcamento(models.Model):
    cliente = models.ForeignKey(ClienteColegio, on_delete=models.CASCADE, verbose_name='Cliente')
    responsavel = models.ForeignKey(Responsavel, on_delete=models.CASCADE, verbose_name='Responsável')
    periodo_viagem = models.ForeignKey(OrcamentoPeriodo, on_delete=models.CASCADE, verbose_name='Período da viagem')
    tipo_monitoria = models.ForeignKey(OrcamentoMonitor, on_delete=models.CASCADE, verbose_name='Tipo de monitoria')
    transporte = models.BooleanField(default=False, verbose_name='Transporte')
    opcionais = models.ManyToManyField(OrcamentoOpicional, blank=True, verbose_name='Opcionais')
    desconto = models.DecimalField(blank=True, null=True, max_digits=4, decimal_places=2, verbose_name='Desconto')
    observacoes = models.TextField(blank=True, verbose_name='Observações')
    motivo_recusa = models.CharField(max_length=255, verbose_name='Motivo da recusa')
    promocional = models.BooleanField(default=False)
    aprovado = models.BooleanField(default=False)
    necessita_aprovacao_gerencia = models.BooleanField(default=False, verbose_name='Necessita de aprovação da gerência')

    def __str__(self):
        return f'Orçamento de {self.cliente}'


class CadastroOrcamento(forms.ModelForm):
    class Meta:
        model = Orcamento
        exclude = ()
