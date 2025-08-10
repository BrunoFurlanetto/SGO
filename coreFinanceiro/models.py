from django.db import models


class TiposPagamentos(models.Model):
    tipo_pagamento = models.CharField(max_length=255)
    offline = models.BooleanField(default=False)
    eficha = models.BooleanField(default=False, verbose_name='e-Ficha')

    def __str__(self):
        return self.tipo_pagamento

    class Meta:
        app_label = 'financeiro'


class ClassificacoesItens(models.Model):
    lista_sintetico_analitico = (
        (0, 'Sintético'),
        (1, 'Analítico'),
    )

    codigo_padrao = models.CharField(max_length=255, verbose_name='Codigo Padrão', unique=True)
    codigo_simplificado = models.CharField(max_length=255, verbose_name='Codigo Simplificado', unique=True)
    descritivo = models.TextField(verbose_name='Descritivo')
    sintetico_analitico = models.IntegerField(verbose_name='Sintético/Analítico', choices=lista_sintetico_analitico)
    ativado = models.BooleanField(default=False, verbose_name='Ativado')
    arredondamento = models.BooleanField(
        default=False,
        verbose_name='Arredondamento',
        help_text='Categoria na Ficha Financeira que será utilizada para o arredondamento.'
    )

    def __str__(self):
        return f'{self.codigo_simplificado} ({self.codigo_padrao})'

    class Meta:
        app_label = 'financeiro'
        verbose_name = 'Classificação de item'
        verbose_name_plural = 'Classificações de itens'
