from django import forms
from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import pre_delete
from django.dispatch import receiver

from orcamento.models import Orcamento
from peraltas.models import ClienteColegio, Responsavel, Vendedor


class DadosEvento(models.Model):
    sim_e_nao = (
        (0, 'Não'),
        (1, 'Sim'),
    )

    responsavel_operecional = models.ForeignKey(
        Responsavel,
        on_delete=models.DO_NOTHING,
        verbose_name='Responsável operacional',
        blank=True,
        null=True
    )
    responsavel_financeiro = models.CharField(max_length=255, verbose_name='Responsável financeiro')
    colaborador = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Colaborador')
    comissao = models.DecimalField(max_digits=4, decimal_places=2, verbose_name='Comissão')
    check_in = models.DateTimeField(verbose_name='Check in')
    check_out = models.DateTimeField(verbose_name='Check out')
    coordenacao = models.IntegerField(choices=sim_e_nao, verbose_name='Coordenação')  # TODO: Verificar o que é esse campo
    monitoria = models.IntegerField(choices=sim_e_nao, verbose_name='Monitoria')
    onibus = models.IntegerField(choices=sim_e_nao, verbose_name='Ônibus')
    seguro = models.IntegerField(choices=sim_e_nao, verbose_name='Seguro')
    qtd_reservada = models.PositiveIntegerField(verbose_name='Qtd reserva')
    alunos_confirmados = models.PositiveIntegerField(verbose_name='Alunos confirmados', default=0)
    responsaveis_confirmados = models.PositiveIntegerField(verbose_name='Responsáveis confirmados', default=0)
    cortesia_alunos = models.PositiveIntegerField(verbose_name='Cortesia de alunos', default=0)
    cortesia_responsaveis = models.PositiveIntegerField(verbose_name='Cortesia de responsáveis', default=0)
    responsaveis_outros_locais = models.PositiveIntegerField(verbose_name='Responsáveis em outros locais', default=0)
    alunos_outros_locais = models.PositiveIntegerField(verbose_name='Alunos em outros locais', default=0)  # TODO: Verifiacar o que é esse campo

    @staticmethod
    @receiver(pre_delete, sender=User)
    def redefinir_colaborador(sender, instance, **kwargs):
        diretoria = Vendedor.objects.filter(usuario__groups__icontains='diretoria')[0]
        DadosEvento.objects.filter(colaborador=instance).update(colaborador=diretoria.usuario)


class DadosPagamento(models.Model):
    # produto = models.DecimalField(decimal_places=2, max_digits=8, verbose_name='Produto') TODO: Veficiar esse campo
    periodo = models.DecimalField(max_digits=8, decimal_places=2, verbose_name='Período')
    descritivo_periodo = models.JSONField(editable=False)
    monitoria = models.DecimalField(max_digits=8, decimal_places=2, verbose_name='Monitoria')
    descritivo_monitoria = models.JSONField(editable=False)
    atividades_ceu = models.DecimalField(max_digits=8, decimal_places=2, verbose_name='Atividades CEU')
    descritivo_atividades_ceu = models.JSONField(editable=False)
    atividades_peraltas = models.DecimalField(max_digits=8, decimal_places=2, verbose_name='Atividades Peraltas')
    descritivo_atividades_peraltas = models.JSONField(editable=False)
    opcionais = models.DecimalField(max_digits=8, decimal_places=2, verbose_name='Opcionais')
    descritivo_opcionais = models.JSONField(editable=False)
    op_extra = models.DecimalField(max_digits=8, decimal_places=2, verbose_name='Opcionais extra')
    descritivo_extra = models.JSONField(editable=False)


class PlanosPagamento(models.Model):
    valor_a_vista = models.DecimalField(max_digits=8, decimal_places=2, verbose_name='Valor à vista')
    forma_pagamento = models.DecimalField(max_digits=8, decimal_places=2, verbose_name='Forma de pagamento')
    parcelas = models.PositiveIntegerField(verbose_name='Parcelas', default=1)
    inicio_vencimento = models.DateField(verbose_name='Início vencimento')
    final_vencimento = models.DateField(verbose_name='Final vencimento')


class NotaFiscal(models.Model):
    razao_social = models.CharField(max_length=255, verbose_name='Razao social')
    endereco = models.CharField(max_length=255, verbose_name='Endereço')
    cnpj = models.CharField(max_length=255, verbose_name='CNPJ')

    def __str__(self):
        return f'Dados nota fiscal de {self.razao_social}'


class FichaFinanceira(models.Model):
    orcamento = models.ForeignKey(Orcamento, on_delete=models.CASCADE, verbose_name='Orçamento')
    cliente = models.ForeignKey(ClienteColegio, on_delete=models.CASCADE, verbose_name='Cliente')
    enviado_ac = models.CharField(max_length=255, verbose_name='Enviado a/c', blank=True, null=True)
    dados_evento = models.ForeignKey(DadosEvento, on_delete=models.CASCADE, verbose_name='Dados do evento')
    dados_pagamento = models.ForeignKey(DadosPagamento, on_delete=models.CASCADE, verbose_name='Dados do pagamento')
    planos_pagamento = models.ForeignKey(PlanosPagamento, on_delete=models.CASCADE, verbose_name='Planos de pagamento')
    nf = models.BooleanField(default=False, verbose_name='NF')
    dados_nota_fiscal = models.ForeignKey(
        NotaFiscal,
        on_delete=models.DO_NOTHING,
        verbose_name='Dados da nota fiscal',
        blank=True,
        null=True
    )
    valor_final = models.DecimalField(max_digits=8, decimal_places=2, verbose_name='Valor final')
    observacoes = models.TextField(verbose_name='Observações', blank=True)
    descritivo_ficha_financeira = models.JSONField(editable=False)
    autorizado_diretoria = models.BooleanField(default=False, verbose_name='Autorizado pela diretoria')

    def __str__(self):
        return f'Ficha financeira de {self.cliente}'


# ------------------------------------------------ Forms ---------------------------------------------------------------
class CadastroDadosEvento(forms.ModelForm):
    class Meta:
        model = DadosEvento
        fields = '__all__'


class CadastroDadosPagamento(forms.ModelForm):
    class Meta:
        model = DadosPagamento
        fields = '__all__'


class CadastroPlanosPagamento(forms.ModelForm):
    class Meta:
        model = PlanosPagamento
        fields = '__all__'


class CadastroNotaFiscal(forms.ModelForm):
    class Meta:
        model = NotaFiscal
        fields = '__all__'


class CadastroFichaFinanceira(forms.ModelForm):
    class Meta:
        model = FichaFinanceira
        fields = '__all__'
