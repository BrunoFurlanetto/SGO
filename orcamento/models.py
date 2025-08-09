import os
from collections import defaultdict
from datetime import datetime, timedelta
import json
import re
from itertools import chain
from random import randint

from django import forms
from django.contrib.auth.models import User
from django.core import serializers
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
from django.db import models, transaction
from django.db.models.signals import pre_delete, pre_save, post_save
from django.dispatch import receiver
from django.urls import reverse_lazy, reverse
from django.utils import timezone
from unidecode import unidecode

from ceu.models import Atividades
from coreFinanceiro.models import ClassificacoesItens
from peraltas.models import ClienteColegio, Responsavel, EmpresaOnibus, Vendedor, ProdutosPeraltas, AtividadesEco


def default_validade():
    return timezone.now() + timezone.timedelta(days=180)


def rename_template_orcamento(instance, filename):
    ext = os.path.splitext(filename)[1]
    ano = instance.ano_vigencia or timezone.now().year  # Garante um valor mesmo antes do save
    filename = f"template_orcamento_{ano}{ext}"
    return os.path.join('orcamentos/templates/', filename)


class TemplateOrcamento(models.Model):
    ano_vigencia = models.PositiveIntegerField(
        unique=True,
        default=timezone.now().year,
        help_text='Apenas um arquivo de template será permitido por ano. Caso um novo arquivo seja enviado para um ano '
                  'que já possua um template cadastrado, o arquivo anterior será automaticamente substituído pelo mais recente'
    )
    arquivo = models.FileField(
        upload_to=rename_template_orcamento,
        validators=[FileExtensionValidator(['pdf'])],
        help_text='Arquivo em <strong>PDF</strong> contendo o modelo de orçamento a ser utilizado para o ano correspondente. '
                  '<strong>A proposta comercial será sempre inserida antes da última página do template</strong>. '
                  'O arquivo deve conter <strong>somente as informações fixas</strong>, pois todas as páginas referentes '
                  'à proposta comercial serão geradas automaticamente pelo sistema.',
    )

    def __str__(self):
        return self.arquivo.name


class ValoresPadrao(models.Model):
    lista_comportamentos = (
        ('porcentagem', 'Porcentagem'),
        ('intervalo_dias', 'Intervalo de dias'),
        ('numerico', 'Numérico'),
        ('monetario', 'Monetario'),
    )

    nome_taxa = models.CharField(
        max_length=255,
        verbose_name='Nome da taxa',
        help_text='Esse nome irá aparecer apaenas para o finenceiro na área administrativa'
    )
    nome_taxa_comercial = models.CharField(
        max_length=30,
        verbose_name='Nome da taxa para o comercial',
        help_text='Nome que irá aparecer para o comercial e/ou para a gerência',
    )
    aparecer_comercial = models.BooleanField(help_text='Se essa taxa deve ou não ser vista pelo comercial',
                                             default=True)
    aparecer_gerência = models.BooleanField(help_text='Se essa taxa deve ou não ser vista pela gerência', default=True)
    valor_padrao = models.DecimalField(verbose_name='Valor', decimal_places=2, max_digits=4)
    valor_minimo = models.DecimalField(
        verbose_name='Valor minimo',
        decimal_places=2,
        max_digits=5,
        blank=True,
        null=True,
        help_text='Caso não haja, deixe em branco!'
    )
    valor_maximo = models.DecimalField(
        verbose_name='Valor maximo',
        decimal_places=2,
        max_digits=5,
        blank=True,
        null=True,
        help_text='Caso não haja, deixe em branco!'
    )
    descricao = models.TextField(verbose_name='Descrição da taxa')
    comportamento = models.CharField(
        verbose_name='Comportamento',
        max_length=255,
        choices=lista_comportamentos,
        default='porcentagem',
        help_text='Comportamento que a variável vai adotar dentro do sistema de orçamento'
    )
    id_taxa = models.CharField(max_length=255, editable=False)

    # classificacao = models.ForeignKey(ClassificacoesItens, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        verbose_name = 'Configuração geral'
        verbose_name_plural = '01 - Configurações gerias'

    @property
    def tipo_variavel(self):
        if self.comportamento == 'porcentagem' or self.comportamento == 'monetario':
            return 'text'

        if self.comportamento == 'intervalo_dias':
            return 'date'

        if self.comportamento == 'numerico':
            return 'number'

    @property
    def valor_padrao_formatado(self):
        if self.comportamento == 'porcentagem':
            return f'{self.valor_padrao}%'.replace('.', ',')

        if self.comportamento == 'intervalo_dias':
            return (datetime.today() + timedelta(days=int(self.valor_padrao))).strftime('%Y-%m-%d')

        if self.comportamento == 'monetario':
            return f'R$ {self.valor_padrao:.2f}'

        if self.comportamento == 'numerico':
            return int(self.valor_padrao)

    @property
    def valor_minimo_formatado(self):
        if self.comportamento == 'porcentagem':
            return f'{self.valor_minimo}%'.replace('.', ',')

        if self.comportamento == 'intervalo_dias':
            return (datetime.today() + timedelta(days=int(self.valor_minimo))).strftime('%Y-%m-%d')

        if self.comportamento == 'monetario':
            return f'R$ {self.valor_minimo:.2f}'

        if self.comportamento == 'numerico':
            return int(self.valor_minimo)

    @property
    def valor_maximo_formatado(self):
        if self.comportamento == 'porcentagem':
            return f'{self.valor_maximo}%'.replace('.', ',')

        if self.comportamento == 'intervalo_dias':
            return (datetime.today() + timedelta(days=int(self.valor_maximo))).strftime('%Y-%m-%d')

        if self.valor_maximo and self.comportamento == 'monetario':
            return f'R$ {self.valor_maximo:.2f}'

        if self.comportamento == 'numerico':
            return int(self.valor_maximo)

    @classmethod
    def retornar_dados_gerencia(cls):
        taxas_base = cls.objects.filter(id_taxa__in=['taxa_comercial', 'comissao', 'desconto_geral'])

        return {
            'teto_desconto_geral': float(taxas_base.get(id_taxa='desconto_geral').valor_padrao),
            'taxa_negocial': {
                'piso_taxa_negocial': float(taxas_base.get(id_taxa='taxa_comercial').valor_minimo),
                'padrao_taxa_negocial': float(taxas_base.get(id_taxa='taxa_comercial').valor_padrao),
                'teto_taxa_negocial': float(taxas_base.get(id_taxa='taxa_comercial').valor_maximo),
            },
            'comissao': {
                'piso_comissao': float(taxas_base.get(id_taxa='comissao').valor_minimo),
                'padrao_comissao': float(taxas_base.get(id_taxa='comissao').valor_padrao),
                'teto_comissao': float(taxas_base.get(id_taxa='comissao').valor_maximo),
            }
        }

    def __str__(self):
        return self.nome_taxa

    def save(self, *args, **kwargs):
        if not self.pk:
            self.id_taxa = unidecode(self.nome_taxa).lower().replace(' ', '_')

        super().save(*args, **kwargs)

        if 'comercial' in self.id_taxa or 'comissao' in self.id_taxa:
            OrcamentoOpicional.update_valor_final()
            OrcamentoPeriodo.update_valor_final()
            OrcamentoMonitor.update_valor_final()
            ValoresTransporte.update_valor_final()

    @classmethod
    def listar_valores(cls):
        valores = cls.objects.all()
        lista_valores = {}

        for valor in valores:
            lista_valores[valor.id_taxa] = valor.valor_padrao

        return lista_valores

    @classmethod
    def mostrar_taxas(cls, objeto_gerencia=None, tipo_de_pacote=None):
        def html_base(nome_taxa, tipo_input, id_taxa, valor_padrao, valor_maximo, valor_minimo):
            return f"""
                <div>
                    <label>{nome_taxa}</label>
                    <input type="{tipo_input}" id="{id_taxa}" name="{id_taxa}" value="{valor_padrao}"
                           data-nome_taxa="{nome_taxa}" data-valor_default="{valor_padrao}"
                           data-valor_inicial="{valor_padrao}" data-valor_alterado="{valor_padrao}"                            
                           data-teto="{valor_maximo}" data-piso="{valor_minimo}">
                </div>                        
            """

        html = ''
        novas_taxas = None
        taxas_cadastradas = cls.objects.filter(aparecer_comercial=True)
        valor_padrao = valor_maximo = valor_minimo = ''
        relacao_tipo_comportamento = {
            'numerico': 'number',
            'intervalo_dias': 'date',
            'porcentagem': 'text',
            'monetario': 'text',
        }

        if tipo_de_pacote:
            novas_taxas = tipo_de_pacote.retornar_dados_gerencia()

        for taxa in taxas_cadastradas:
            valor_maximo = valor_minimo = ''

            if taxa.id_taxa == 'minimo_onibus':
                valor_padrao = int(taxa.valor_padrao) if objeto_gerencia is None else int(
                    objeto_gerencia['minimo_onibus'])
                valor_maximo = int(taxa.valor_maximo)
                valor_minimo = int(taxa.valor_minimo)

            if taxa.id_taxa == 'data_pagamento':
                if objeto_gerencia is None:
                    valor = datetime.today().date() + timedelta(days=int(taxa.valor_padrao))
                    valor_padrao = valor.strftime('%Y-%m-%d')
                else:
                    valor_padrao = objeto_gerencia['data_pagamento']

            if taxa.id_taxa == 'comissao':
                if objeto_gerencia is None:
                    valor_padrao = str(taxa.valor_padrao).replace('.', ',') + '%'
                else:
                    valor_padrao = f"{objeto_gerencia['comissao']:.2f}%".replace('.', ',')

                valor_maximo = str(taxa.valor_maximo).replace('.', ',') + '%'
                valor_minimo = str(taxa.valor_minimo).replace('.', ',') + '%'

                if tipo_de_pacote:
                    if novas_taxas['comissao']['padrao_comissao'] is not None:
                        valor_padrao = str(novas_taxas['comissao']['padrao_comissao']).replace('.', ',') + '%'

                    if novas_taxas['comissao']['piso_comissao'] is not None:
                        valor_minimo = str(novas_taxas['comissao']['piso_comissao']).replace('.', ',') + '%'

                    if novas_taxas['comissao']['teto_comissao'] is not None:
                        valor_maximo = str(novas_taxas['comissao']['teto_comissao']).replace('.', ',') + '%'

            if taxa.id_taxa == 'taxa_comercial':
                if objeto_gerencia is None:
                    valor_padrao = str(taxa.valor_padrao).replace('.', ',') + '%'
                else:
                    valor_padrao = f"{objeto_gerencia['taxa_comercial']:.2f}%".replace('.', ',')

                valor_maximo = str(taxa.valor_maximo).replace('.', ',') + '%'
                valor_minimo = str(taxa.valor_minimo).replace('.', ',') + '%'

                if tipo_de_pacote:
                    if novas_taxas['taxa_negocial']['padrao_taxa_negocial'] is not None:
                        valor_padrao = str(novas_taxas['taxa_negocial']['padrao_taxa_negocial']).replace('.', ',') + '%'

                    if novas_taxas['taxa_negocial']['piso_taxa_negocial'] is not None:
                        valor_minimo = str(novas_taxas['taxa_negocial']['piso_taxa_negocial']).replace('.', ',') + '%'

                    if novas_taxas['taxa_negocial']['teto_taxa_negocial'] is not None:
                        valor_maximo = str(novas_taxas['taxa_negocial']['teto_taxa_negocial']).replace('.', ',') + '%'

            html += html_base(
                taxa.nome_taxa_comercial,
                relacao_tipo_comportamento[taxa.comportamento],
                taxa.id_taxa,
                valor_padrao,
                valor_maximo,
                valor_minimo
            )

        html += html_base(
            'Desconto',
            'text',
            'desconto_geral',
            '0,00',
            str(novas_taxas['teto_desconto_geral']).replace('.', ',') if tipo_de_pacote else '0,00',
            '0,00'
        )

        return html


class OrcamentoMonitor(models.Model):
    nome_monitoria = models.CharField(max_length=100)
    descricao_monitoria = models.TextField(blank=True)
    valor = models.DecimalField(decimal_places=2, max_digits=5, default=0.00)
    valor_final = models.DecimalField(
        decimal_places=2,
        max_digits=5,
        default=0.00,
        editable=False,
        verbose_name='Preço de venda'
    )
    inicio_vigencia = models.DateField()
    final_vigencia = models.DateField(default=default_validade)
    regra_cortesia = models.TextField(blank=True,
                                      help_text='Texto da regra de cortesia que será mostrado dentro das condições finais do orçamento')
    racional_monitoria = models.PositiveIntegerField(default=8, verbose_name="Racional Monitoria")
    sem_monitoria = models.BooleanField(default=False)
    liberado = models.BooleanField(default=False)
    classificacao = models.ForeignKey(
        ClassificacoesItens,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        limit_choices_to={'sintetico_analitico': True},
    )

    class Meta:
        verbose_name = 'Valor monitoria'
        verbose_name_plural = '05 - Valores de monitoria'

    def __str__(self):
        return self.nome_monitoria

    @classmethod
    def update_valor_final(cls):
        taxa_comercial = float(ValoresPadrao.objects.get(id_taxa__icontains='comercial').valor_padrao)
        comissao = float(ValoresPadrao.objects.get(id_taxa__icontains='comissao').valor_padrao)

        for monitoria in cls.objects.all():
            monitoria.valor_final = float(monitoria.valor) / (1 - ((taxa_comercial + comissao) / 100))
            monitoria.save()

    def save(self, *args, **kwargs):
        taxa_comercial = float(ValoresPadrao.objects.get(id_taxa__icontains='comercial').valor_padrao)
        comissao = float(ValoresPadrao.objects.get(id_taxa__icontains='comissao').valor_padrao)
        self.valor_final = float(self.valor) / (1 - ((taxa_comercial + comissao) / 100))

        super().save(*args, **kwargs)

    @classmethod
    def verificar_validade(cls, check_in, check_out, financeiro):
        data = check_in

        while data <= check_out:
            if financeiro:
                monitoria = cls.objects.filter(
                    inicio_vigencia__lte=data,
                    final_vigencia__gte=data,
                ).exists()
            else:
                monitoria = cls.objects.filter(
                    inicio_vigencia__lte=data,
                    final_vigencia__gte=data,
                    liberado=True,
                ).exists()

            if not monitoria:
                return False

            data += timedelta(days=1)

        return True


class CategoriaOpcionais(models.Model):
    nome_categoria = models.CharField(max_length=100)
    staff = models.BooleanField(default=False)
    ceu_sem_hospedagem = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Categoria'
        verbose_name_plural = '07a - Categorias de opcionais'

    def __str__(self):
        return self.nome_categoria


class SubcategoriaOpcionais(models.Model):
    nome_sub_categoria = models.CharField(max_length=100)

    class Meta:
        verbose_name = 'Subcategoria'
        verbose_name_plural = '07b - Subcategorias de opcionais'

    def __str__(self):
        return self.nome_sub_categoria


class OrcamentoOpicional(models.Model):
    nome = models.CharField(max_length=100)
    categoria = models.ForeignKey(CategoriaOpcionais, on_delete=models.DO_NOTHING, null=True, blank=True)
    sub_categoria = models.ForeignKey(SubcategoriaOpcionais, on_delete=models.DO_NOTHING, null=True, blank=True)
    descricao = models.TextField()
    valor = models.DecimalField(decimal_places=2, max_digits=5, default=0.00)
    valor_final = models.DecimalField(decimal_places=2, max_digits=5, default=0.00, editable=False)
    inicio_vigencia = models.DateField()
    final_vigencia = models.DateField(default=default_validade)
    liberado = models.BooleanField(default=False)
    classificacao = models.ForeignKey(
        ClassificacoesItens,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        limit_choices_to={'sintetico_analitico': True}
    )

    class Meta:
        verbose_name = 'Valor opcionais'
        verbose_name_plural = '07c - Valores de opcionais'

    def __str__(self):
        return self.nome

    @classmethod
    def update_valor_final(cls):
        taxa_comercial = float(ValoresPadrao.objects.get(id_taxa__icontains='comercial').valor_padrao)
        comissao = float(ValoresPadrao.objects.get(id_taxa__icontains='comissao').valor_padrao)

        for opcional in cls.objects.all():
            opcional.valor_final = float(opcional.valor) / (1 - ((taxa_comercial + comissao) / 100))
            opcional.save()

    def save(self, *args, **kwargs):
        taxa_comercial = float(ValoresPadrao.objects.get(id_taxa__icontains='comercial').valor_padrao)
        comissao = float(ValoresPadrao.objects.get(id_taxa__icontains='comissao').valor_padrao)
        self.valor_final = float(self.valor) / (1 - ((taxa_comercial + comissao) / 100))

        super().save(*args, **kwargs)


class DiasSemana(models.Model):
    id_dia = models.IntegerField(primary_key=True)
    nome_dia = models.CharField(max_length=255)

    def __str__(self):
        return self.nome_dia


class OrcamentoPeriodo(models.Model):
    nome_periodo = models.CharField(max_length=255)
    inicio_vigencia = models.DateField(verbose_name='Início da vigência', default=timezone.now)
    final_vigencia = models.DateField(verbose_name='Final da vigência',
                                      default=default_validade)
    dias_semana_validos = models.ManyToManyField(DiasSemana)
    valor = models.DecimalField(decimal_places=2, max_digits=5, default=0.00)
    valor_final = models.DecimalField(decimal_places=2, max_digits=5, default=0.00, editable=False,
                                      verbose_name='Preço de venda')
    descricao = models.TextField(blank=True)
    liberado = models.BooleanField(default=False, help_text='Liberado para o comercial')
    exclusivo_montagem_pacote = models.BooleanField(default=False)
    classificacao = models.ForeignKey(
        ClassificacoesItens,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        limit_choices_to={'sintetico_analitico': True}
    )

    class Meta:
        verbose_name = 'Valor do periodo'
        verbose_name_plural = '03 - Valores de diárias'

    def __str__(self):
        return self.nome_periodo

    @classmethod
    def update_valor_final(cls):
        taxa_comercial = float(ValoresPadrao.objects.get(id_taxa__icontains='comercial').valor_padrao)
        comissao = float(ValoresPadrao.objects.get(id_taxa__icontains='comissao').valor_padrao)

        for periodo in cls.objects.all():
            periodo.valor_final = float(periodo.valor) / (1 - ((taxa_comercial + comissao) / 100))
            periodo.save()

    def save(self, *args, **kwargs):
        taxa_comercial = float(ValoresPadrao.objects.get(id_taxa__icontains='comercial').valor_padrao)
        comissao = float(ValoresPadrao.objects.get(id_taxa__icontains='comissao').valor_padrao)
        self.valor_final = float(self.valor) / (1 - ((taxa_comercial + comissao) / 100))

        super().save(*args, **kwargs)

    @classmethod
    def verificar_validade(cls, check_in, check_out, financeiro):
        data = check_in

        while data <= check_out:
            if financeiro:
                periodo = cls.objects.filter(
                    inicio_vigencia__lte=data,
                    final_vigencia__gte=data,
                    dias_semana_validos__in=[data.weekday()],
                ).exists()
            else:
                periodo = cls.objects.filter(
                    inicio_vigencia__lte=data,
                    final_vigencia__gte=data,
                    dias_semana_validos__in=[data.weekday()],
                    liberado=True,
                ).exists()

            if not periodo:
                return False

            data += timedelta(days=1)

        return True


class TaxaPeriodo(models.Model):
    inicio_vigencia = models.DateField(default=timezone.now)
    final_vigencia = models.DateField(default=default_validade)
    descricao = models.TextField(blank=True)
    valor = models.DecimalField(decimal_places=2, max_digits=7, default=0.00)
    classificacao = models.ForeignKey(
        ClassificacoesItens,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        limit_choices_to={'sintetico_analitico': True},
    )

    class Meta:
        verbose_name = 'Valor da taxa do periodo'
        verbose_name_plural = '04 - Valores da taxa dos periodos'


class HorariosPadroes(models.Model):
    refeicao = models.CharField(max_length=50, verbose_name='Título')
    horario = models.TimeField(verbose_name='Horário início')
    final_horario = models.TimeField(verbose_name='Horário final')
    entrada_saida = models.BooleanField()
    so_ceu = models.BooleanField(default=False)
    racional = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        default=1.00,
        help_text='Número de diárias de hotelaria'
    )
    racional_monitor = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        default=1.00,
        help_text='Número de diárias de monitoria'
    )
    descritivo = models.TextField(verbose_name='Descritivo', blank=True)
    descricao_alimentacao = models.TextField(verbose_name='Descrição das alimentações')

    class Meta:
        verbose_name = 'Horário de entrada e saída'
        verbose_name_plural = '02 - Horários de entrada e saída'

    def __str__(self):
        return f'Horário {self.refeicao}'

    @property
    def hora(self):
        return self.horario.strftime('%H:%M')

    @property
    def horario_final(self):
        return self.final_horario.strftime('%H:%M')

    @property
    def tipo(self):
        if self.entrada_saida:
            return 'Entrada'
        else:
            return 'Saída'


class ValoresTransporte(models.Model):
    titulo_transporte = models.CharField(max_length=255)
    valor_1_dia = models.DecimalField(
        max_digits=7, decimal_places=2, verbose_name='Valor de 1 dia')
    valor_final_1_dia = models.DecimalField(
        max_digits=7, decimal_places=2, verbose_name='Preço de venda de 1 dia', editable=False, default=0.00)
    valor_2_dia = models.DecimalField(
        max_digits=7, decimal_places=2, verbose_name='Valor de 2 dias')
    valor_final_2_dia = models.DecimalField(
        max_digits=7, decimal_places=2, verbose_name='Preço de venda de 2 dias', editable=False, default=0.00)
    valor_3_dia = models.DecimalField(
        max_digits=7, decimal_places=2, verbose_name='Valor de 3 dias')
    valor_final_3_dia = models.DecimalField(
        max_digits=7, decimal_places=2, verbose_name='Preço de venda de 3 dias', editable=False, default=0.00)
    valor_4_dia = models.DecimalField(
        max_digits=7, decimal_places=2, verbose_name='Valor de 4 dias')
    valor_5_dia = models.DecimalField(
        max_digits=7, decimal_places=2, verbose_name='Valor de 5 dias')
    valor_acrescimo = models.DecimalField(
        max_digits=7, decimal_places=2, verbose_name='Acréscimo dia extra'
    )
    acrescimo_barra = models.DecimalField(
        max_digits=7, decimal_places=2, verbose_name='Acréscimo Barra Bonita'
    )
    leva_e_busca = models.DecimalField(
        max_digits=7, decimal_places=2, verbose_name='Leva e Busca', default=0.00)
    percentual = models.DecimalField(
        max_digits=3, decimal_places=2, verbose_name='Percentual', default=0.10)
    inicio_vigencia = models.DateField(verbose_name='Inicio vigência dos valores', default=timezone.now)
    final_vigencia = models.DateField(verbose_name='Final vigência dos valores', default=default_validade)
    descricao = models.TextField(verbose_name="Descrição", default="")
    liberado = models.BooleanField(default=False)
    classificacao = models.ForeignKey(
        ClassificacoesItens,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        limit_choices_to={'sintetico_analitico': True},
    )

    class Meta:
        verbose_name = 'Valor do transporte'
        verbose_name_plural = '06 - Valores de transporte'

    def __str__(self):
        return f'Valores do transporte de {self.inicio_vigencia.strftime("%d/%m/%Y")} até {self.final_vigencia.strftime("%d/%m/%Y")}'

    @classmethod
    def update_valor_final(cls):
        taxa_comercial = float(ValoresPadrao.objects.get(id_taxa__icontains='comercial').valor_padrao)
        comissao = float(ValoresPadrao.objects.get(id_taxa__icontains='comissao').valor_padrao)

        for trnasporte in cls.objects.all():
            trnasporte.valor_final_1_dia = float(trnasporte.valor_1_dia) / (1 - ((taxa_comercial + comissao) / 100))
            trnasporte.valor_final_2_dia = float(trnasporte.valor_2_dia) / (1 - ((taxa_comercial + comissao) / 100))
            trnasporte.valor_final_3_dia = float(trnasporte.valor_3_Dia) / (1 - ((taxa_comercial + comissao) / 100))
            trnasporte.save()

    def save(self, *args, **kwargs):
        taxa_comercial = float(ValoresPadrao.objects.get(id_taxa__icontains='comercial').valor_padrao)
        comissao = float(ValoresPadrao.objects.get(id_taxa__icontains='comissao').valor_padrao)
        self.valor_final_1_dia = float(self.valor_1_dia) / (1 - ((taxa_comercial + comissao) / 100))
        self.valor_final_2_dia = float(self.valor_2_dia) / (1 - ((taxa_comercial + comissao) / 100))
        self.valor_final_3_dia = float(self.valor_3_dia) / (1 - ((taxa_comercial + comissao) / 100))

        super().save(*args, **kwargs)

    @classmethod
    def verificar_validade(cls, check_in, check_out, financeiro):
        data = check_in

        while data <= check_out:
            if financeiro:
                transporte = cls.objects.filter(
                    inicio_vigencia__lte=data,
                    final_vigencia__gte=data,
                ).exists()
            else:
                transporte = cls.objects.filter(
                    inicio_vigencia__lte=data,
                    final_vigencia__gte=data,
                    liberado=True,
                ).exists()

            if not transporte:
                return False

            data += timedelta(days=1)

        return True


class StatusOrcamento(models.Model):
    status = models.CharField(max_length=100)
    analise_gerencia = models.BooleanField(
        default=False,
        help_text='Status utilizado para análise e respostas da gerência.'
    )
    negativa_gerencia = models.BooleanField(
        default=False,
        help_text='Status de orçamento utilizado pela gerência para negar um pedido do comercial.'
    )
    aprovacao_gerencia = models.BooleanField(
        default=False,
        help_text='Status de orçamento utilizado pela gerência para aprovar um pedido do comercial.'
    )
    aprovacao_cliente = models.BooleanField(
        default=False,
        help_text='Status utilizado para orçamentos aceitos pelo cliente.'
    )
    negado_cliente = models.BooleanField(
        default=False,
        help_text='Status utilizado para orçamentos no qual o cliente não aceitou.'
    )
    orcamento_vencido = models.BooleanField(
        default=False,
        help_text='Status utilizado para orçamentos que estão vencdos.'
    )

    def __str__(self):
        return self.status

    def clean(self):
        """
        Verifica se já existe um registro com a mesma combinação de campos booleanos.
        """
        # Cria um dicionário com os valores booleanos do objeto atual
        filtros = {
            'analise_gerencia': self.analise_gerencia,
            'negativa_gerencia': self.negativa_gerencia,
            'aprovacao_gerencia': self.aprovacao_gerencia,
            'aprovacao_cliente': self.aprovacao_cliente,
            'negado_cliente': self.negado_cliente,
            'orcamento_vencido': self.orcamento_vencido,
        }

        # Procura no banco um registro com os mesmos valores booleanos
        query = StatusOrcamento.objects.filter(**filtros)

        # Se for um update, excluímos o próprio objeto da verificação
        if self.pk:
            query = query.exclude(pk=self.pk)

        if query.exists():
            raise ValidationError("Já existe um status de orçamento com essa mesma combinação de valores.")

    def save(self, *args, **kwargs):
        self.clean()  # Garante que a validação será feita antes de salvar
        super().save(*args, **kwargs)


class TiposDePacote(models.Model):
    titulo = models.CharField(max_length=100, verbose_name="Título")
    teto_desconto_geral = models.DecimalField(
        decimal_places=2,
        max_digits=5,
        blank=True,
        null=True,
        help_text='Deixar em branco para pegar os valores padrão'
    )
    minimo_taxa_negocial = models.DecimalField(
        decimal_places=2,
        max_digits=5,
        blank=True,
        null=True,
        help_text='Deixar em branco para pegar os valores padrão'
    )
    valor_padrao_taxa_negocial = models.DecimalField(
        decimal_places=2,
        max_digits=5,
        blank=True,
        null=True,
        help_text='Deixar em branco para pegar os valores padrão'
    )
    maximo_taxa_negocial = models.DecimalField(
        decimal_places=2,
        max_digits=5,
        blank=True,
        null=True,
        help_text='Deixar em branco para pegar os valores padrão'
    )
    minimo_comissao = models.DecimalField(
        decimal_places=2,
        max_digits=5,
        blank=True,
        null=True,
        help_text='Deixar em branco para pegar os valores padrão'
    )
    valor_padrao_comissao = models.DecimalField(
        decimal_places=2,
        max_digits=5,
        blank=True,
        null=True,
        help_text='Deixar em branco para pegar os valores padrão'
    )
    maximo_comissao = models.DecimalField(
        decimal_places=2,
        max_digits=5,
        blank=True,
        null=True,
        help_text='Deixar em branco para pegar os valores padrão'
    )
    n_diarias = models.PositiveIntegerField(default=1, verbose_name='Número de diarias')
    so_ceu = models.BooleanField(default=False)
    descricao = models.TextField()

    class Meta:
        verbose_name = '10 - Tipos de pacote'

    def __str__(self):
        return self.titulo

    @classmethod
    def dados_do_tipo_de_pacote(cls):
        dados = {}

        return

    def retornar_dados_gerencia(self):
        return {
            'so_ceu': self.so_ceu,
            'teto_desconto_geral': self.teto_desconto_geral,
            'taxa_negocial': {
                'piso_taxa_negocial': self.minimo_taxa_negocial,
                'padrao_taxa_negocial': self.valor_padrao_taxa_negocial,
                'teto_taxa_negocial': self.maximo_taxa_negocial,
            },
            'comissao': {
                'piso_comissao': self.minimo_comissao,
                'padrao_comissao': self.valor_padrao_comissao,
                'teto_comissao': self.maximo_comissao,
            }
        }


class DadosDePacotes(models.Model):
    nome_do_pacote = models.CharField(max_length=255, verbose_name="Nome do Pacote")
    minimo_de_pagantes = models.PositiveIntegerField(verbose_name="Minimo de pagantes")
    tipos_de_pacote_elegivel = models.ForeignKey(TiposDePacote, verbose_name="Pacotes elegíveis",
                                                 on_delete=models.PROTECT)
    monitoria_fechado = models.BooleanField(default=True)
    transporte_fechado = models.BooleanField(default=True)
    opcionais_fechado = models.BooleanField(default=True)
    cortesia = models.BooleanField(default=True, verbose_name="Cortesia")
    regra_cortesia = models.PositiveIntegerField(verbose_name="Regra de cortesias", blank=True, null=True)
    periodos_aplicaveis = models.JSONField(verbose_name="Periodos aplicaveis")
    descricao = models.TextField(verbose_name="Descrição do pacote")

    def __str__(self):
        return f'Dados do pacote promocional {self.nome_do_pacote}'

    @staticmethod
    def tratar_dados(dados):
        dados_tratados = {}

        for campo, value in dados.items():
            try:
                dado_int = int(value)
            except ValueError:
                try:
                    dado_float = float(value.replace(',', '.').replace('%', ''))
                except ValueError:
                    dados_tratados[campo] = value
                else:
                    dados_tratados[campo] = dado_float
            else:
                dados_tratados[campo] = dado_int

        # if dados.getlist('produtos_elegiveis[]'):
        #     lista = [int(i) for i in dados.getlist('produtos_elegiveis[]')]
        # else:
        #     lista = [int(dados.get('produtos_elegiveis'))]
        #
        # dados_tratados['produtos_elegiveis'] = lista
        dados_tratados['periodos_aplicaveis'] = DadosDePacotes.juntar_periodos(dados)

        return dados_tratados

    @staticmethod
    def juntar_periodos(dados_pacote):
        periodo_n = 1
        periodos = []

        while True:
            if dados_pacote.get(f'periodo_{periodo_n}', None):
                try:
                    dados_pacote[f'dias_periodo_{periodo_n}[]']
                except KeyError:
                    periodos.append({
                        f'periodo_{periodo_n}': dados_pacote.get(f'periodo_{periodo_n}'),
                        f'dias_periodos_{periodo_n}': list(map(int, dados_pacote.get(f'dias_periodo_{periodo_n}'))),
                        f'check_in_permitido_{periodo_n}': ' - '.join(
                            dados_pacote.getlist(f'check_in_permitido_{periodo_n}[]')),
                        f'check_out_permitido_{periodo_n}': ' - '.join(
                            dados_pacote.getlist(f'check_out_permitido_{periodo_n}[]')),
                    })
                else:
                    periodos.append({
                        f'periodo_{periodo_n}': dados_pacote.get(f'periodo_{periodo_n}'),
                        f'check_in_permitido_{periodo_n}': ' - '.join(
                            dados_pacote.getlist(f'check_in_permitido_{periodo_n}[]')),
                        f'check_out_permitido_{periodo_n}': ' - '.join(
                            dados_pacote.getlist(f'check_out_permitido_{periodo_n}[]')),
                        f'dias_periodos_{periodo_n}': list(
                            map(int, dados_pacote.getlist(f'dias_periodo_{periodo_n}[]')))
                    })
            else:
                break

            periodo_n += 1

        return periodos

    def ajustar_periodos(self):
        """
        Avança os períodos elegíveis em um ano à frente.
        """
        novos_periodos = []
        periodos = self.periodos_aplicaveis  # Acesso direto ao JSONField, sem json.loads

        for periodo in periodos:
            novo_periodo = {}

            for key, value in periodo.items():
                if 'dias' not in key and 'check' not in key:
                    datas = value.split(" - ")
                    novas_datas = [
                        (datetime.strptime(data, "%d/%m/%Y") + timedelta(days=365)).strftime("%d/%m/%Y")
                        for data in datas
                    ]
                    novo_periodo[key] = " - ".join(novas_datas)
                else:
                    novo_periodo[key] = value
            novos_periodos.append(novo_periodo)

        return novos_periodos

    def montar_dados_periodos(self):
        def unidade_base(i, periodo, intervalo, lista_dias, check_ins, check_outs):
            return f"""
                <div class="mt-3 div_periodos_aplicaveis" style="display: flex; column-gap: 10px">
                    <div class="periodos">
                        <input type="text" id="{periodo}"
                               name="{periodo}" value="{intervalo}"
                               class="periodos_aplicaveis">
                        <button type="button" class="btn_remover_periodo"
                                onclick="remover_periodo(this)">
                            <span>&times;</span></button>
                    </div>
                    <div class="dias mt-2">
                        <div>
                            <input id="input_seg" type="checkbox" name="dias_{periodo}"
                                   value="0" {'checked' if 0 in lista_dias else ''}>
                            <label for="input_seg">Seg</label>
                        </div>
                        <div>
                            <input id="input_ter" type="checkbox" name="dias_{periodo}"
                                   value="1" {'checked' if 1 in lista_dias else ''}>
                            <label for="input_ter">Ter</label>
                        </div>
                        <div>
                            <input id="input_qua" type="checkbox" name="dias_{periodo}"
                                   value="2" {'checked' if 2 in lista_dias else ''}>
                            <label for="input_qua">Qua</label>
                        </div>
                        <div>
                            <input id="input_qui" type="checkbox" name="dias_{periodo}"
                                   value="3" {'checked' if 3 in lista_dias else ''}>
                            <label for="input_qui">Qui</label>
                        </div>
                        <div>
                            <input id="input_sex" type="checkbox" name="dias_{periodo}"
                                   value="4" {'checked' if 4 in lista_dias else ''}>
                            <label for="input_sex">Sex</label>
                        </div>
                        <div>
                            <input id="input_sab" type="checkbox" name="dias_{periodo}"
                                   value="5" {'checked' if 5 in lista_dias else ''}>
                            <label for="input_sab">Sab</label>
                        </div>
                        <div>
                            <input id="input_dom" type="checkbox" name="dias_{periodo}"
                                   value="6" {'checked' if 6 in lista_dias else ''}>
                            <label for="input_dom">Dom</label>
                        </div>
                    </div>
                    <div id="horas_permitidas" class="mt-2">
                        <div id="check_in" >
                            <label>Periodo de check in</label>
                            <div>
                                <input type="time" name="check_in_permitido_{i}" value="{check_ins[0]}">
                                a
                                <input type="time" name="check_in_permitido_{i}" value="{check_ins[1]}">
                            </div>
                        </div>
                        <div id="check_out" class="mt-2">
                            <label>Periodo de check out</label>
                            <div>
                                <input type="time" name="check_out_permitido_{i}" value="{check_outs[0]}">
                                a
                                <input type="time" name="check_out_permitido_{i}" value="{check_outs[1]}">
                            </div>
                        </div>
                    </div>
                    <hr style="width: 100%">
                </div>
            """

        html_dados = ''

        for i, periodo in enumerate(self.periodos_aplicaveis, start=1):
            html_dados += unidade_base(
                i,
                f'periodo_{i}',
                periodo[f'periodo_{i}'],
                periodo[f'dias_periodos_{i}'],
                periodo[f'check_in_permitido_{i}'].split(' - ') if periodo.get(f'check_in_permitido_{i}') else ['', ''],
                periodo[f'check_out_permitido_{i}'].split(' - ') if periodo.get(f'check_out_permitido_{i}') else ['',
                                                                                                                  ''],
            )

        return html_dados

    def serializar_objetos(self):
        obj = self
        dados = serializers.serialize('json', [obj, ])

        return json.loads(dados)[0]


class MotivosRecusa(models.Model):
    motivo = models.CharField(max_length=255, verbose_name='Motivo de recusa')

    def __str__(self):
        return self.motivo


class Orcamento(models.Model):
    sim_e_nao = (
        ('sim', 'Sim'),
        ('nao', 'Não')
    )

    apelido = models.CharField(max_length=255, verbose_name="Apelido", blank=True, null=True)
    cliente = models.ForeignKey(
        ClienteColegio,
        on_delete=models.CASCADE,
        verbose_name='Cliente',
        blank=True,
        null=True
    )
    responsavel = models.ForeignKey(
        Responsavel,
        on_delete=models.CASCADE,
        verbose_name='Responsável',
        blank=True,
        null=True
    )
    tipo_de_pacote = models.ForeignKey(
        TiposDePacote,
        on_delete=models.CASCADE,
        verbose_name='Tipo de pacote',
        blank=True,
        null=True
    )
    produto = models.ForeignKey(
        ProdutosPeraltas,
        on_delete=models.CASCADE,
        verbose_name='Produto',
        blank=True,
        null=True
    )
    check_in = models.DateTimeField(verbose_name='Check in', blank=True, null=True)
    check_out = models.DateTimeField(verbose_name='Check out', blank=True, null=True)
    tipo_monitoria = models.ForeignKey(OrcamentoMonitor, on_delete=models.CASCADE, verbose_name='Tipo de monitoria')
    transporte = models.CharField(max_length=3, default='', choices=sim_e_nao, verbose_name='Transporte')
    opcionais = models.ManyToManyField(
        OrcamentoOpicional,
        blank=True,
        verbose_name='Opcionais',
    )
    opcionais_extra = models.JSONField(blank=True, null=True, verbose_name='Opcionais extra')
    desconto = models.DecimalField(blank=True, null=True, max_digits=6, decimal_places=2, verbose_name='Desconto')
    valor = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Valor orçamento')
    colaborador = models.ForeignKey(User, on_delete=models.DO_NOTHING, blank=True)
    observacoes = models.TextField(blank=True, verbose_name='Observações')
    motivo_recusa = models.ForeignKey(MotivosRecusa, on_delete=models.SET_NULL, blank=True, null=True, verbose_name='Motivo da recusa')
    obs_recusa = models.CharField(blank=True, null=True, max_length=255, verbose_name='Oservações da recusa')
    objeto_gerencia = models.JSONField(blank=True, null=True, editable=False)
    objeto_orcamento = models.JSONField(blank=True, null=True, editable=False)
    orcamento_promocional = models.ForeignKey(
        'orcamento.OrcamentosPromocionais',
        on_delete=models.CASCADE,
        verbose_name='Orçamento Promocional',
        related_name='id_orcamento_promocional',
        blank=True,
        null=True,
    )
    comentario_desconto = models.TextField(blank=True)
    gerente_responsavel = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='gerente_responsavel'
    )
    aprovacao_diretoria = models.BooleanField(default=False)
    promocional = models.BooleanField(default=False)
    status_orcamento = models.ForeignKey(
        StatusOrcamento,
        on_delete=models.DO_NOTHING,
        blank=True,
        null=True,
        verbose_name='Status'
    )
    previa = models.BooleanField(default=True)
    data_preenchimento = models.DateTimeField(auto_now_add=True, verbose_name='Data de preenchimento')
    data_vencimento = models.DateField(verbose_name='Data de vencimento')
    data_ultima_edicao = models.DateTimeField(
        blank=True,
        null=True,
        auto_now=True,
        verbose_name='Data da ultima edição'
    )
    condicoes_finais = models.TextField(blank=True)
    regras_de_pagamento = models.TextField(blank=True,
        default='Os pagamentos podem ser realizados de duas maneiras <ol><li><b>Via Sistema Peraltas</b>: Até 6 '
                'parcelas mensais consecutivas. </li><li><b>Via Escola</b>: Em até 5 parcelas.</li><li>Em caso de dúvida,'
                ' entre em contato com a sua consultora de vendas.</li></ol>'
    )

    class Meta:
        verbose_name = 'Orçamento'
        verbose_name_plural = '09 - Orçamentos criados'
        permissions = (('aprovar_orcamentos', 'Aprovar orcamentos'), ('ver_outras_previas', 'Ver outras prévias'))

    def __str__(self):
        if not self.promocional:
            return f'Orçamento de {self.cliente}'
        else:
            return f'Orçamento promocional {self.id}'

    @property
    def alimentacao_entrada(self):
        return HorariosPadroes.objects.get(
            entrada_saida=True,
            horario__lte=self.check_in.astimezone().time(),
            final_horario__gte=self.check_in.astimezone().time(),
            so_ceu=self.tipo_de_pacote.so_ceu if self.promocional else False
        ).descricao_alimentacao

    @property
    def alimentacao_saida(self):
        return HorariosPadroes.objects.get(
            entrada_saida=False,
            horario__lte=self.check_out.astimezone().time(),
            final_horario__gte=self.check_out.astimezone().time(),
            so_ceu=self.tipo_de_pacote.so_ceu if self.promocional else False
        ).descricao_alimentacao

    @property
    def dias_evento(self):
        return (self.check_out.astimezone().date() - self.check_in.astimezone().date()).days + 1

    @property
    def infos_transporte(self):
        return ValoresTransporte.objects.get(
            inicio_vigencia__lte=self.check_in.astimezone().date(),
            final_vigencia__gte=self.check_in.astimezone().date(),
        ).descricao

    @property
    def opcionais_contratados(self):
        opcionais_orcamento = self.opcionais.all()
        opcionais_pacote = self.orcamento_promocional.orcamento.opcionais.all() if self.orcamento_promocional else []
        todos_opcionais = list(chain(opcionais_orcamento, opcionais_pacote))

        return todos_opcionais

    @property
    def opcionais_contratados_unicos(self):
        # Coleta todos os opcionais únicos dos orçamentos ativos
        opcionais_unicos = set()

        for opcional in self.opcionais_contratados:  # Supondo que "opcionais_contratados" seja o campo no Orcamento
            if not opcional.categoria.staff:
                opcionais_unicos.add(opcional.id)

        return OrcamentoOpicional.objects.filter(id__in=opcionais_unicos)

    def descritivo_opcionais(self):

        return set([op for op in self.opcionais_contratados if not op.categoria.staff])

    @property
    def oficina_de_foguetes(self):
        foguetes = [op for op in self.opcionais_contratados if 'PHOBOS' in op.nome]

        return len(foguetes) > 0

    @property
    def desconto_aplicado(self):
        if self.desconto and self.desconto < 0:
            return True

        return False

    @property
    def get_valor_comissao(self):
        return self.objeto_gerencia['comissao']

    @property
    def get_valor_taxa(self):
        return self.objeto_gerencia['taxa_comercial']

    @property
    def desconto_percentual_diaria(self):
        return f'{self.objeto_gerencia["desconto_produto_percent"]:.2f}'.replace('.', ',')

    @property
    def desconto_percentual_monitoria(self):
        return f'{self.objeto_gerencia["desconto_monitoria_percent"]:.2f}'.replace('.', ',')

    @property
    def desconto_percentual_transporte(self):
        return f'{self.objeto_gerencia["desconto_transporte_percent"]:.2f}'.replace('.', ',')

    @property
    def desconto_real_diaria(self):
        return f'{self.objeto_gerencia.get("desconto_produto_real", 0.00):.2f}'.replace('.', ',')

    @property
    def desconto_real_monitoria(self):
        return f'{self.objeto_gerencia.get("desconto_monitoria_real", 0.00):.2f}'.replace('.', ',')

    @property
    def desconto_real_transporte(self):
        return f'{self.objeto_gerencia.get("desconto_transporte_real", 0.00):.2f}'.replace('.', ',')

    @property
    def refeicoes_check_in(self):
        return HorariosPadroes.objects.get(
            entrada_saida=True,
            so_ceu=False,
            horario__lte=self.check_in.astimezone().time(),
            final_horario__gte=self.check_in.astimezone().time()
        ).descricao_alimentacao

    @property
    def refeicoes_check_out(self):
        return HorariosPadroes.objects.get(
            entrada_saida=False,
            so_ceu=False,
            horario__lte=self.check_out.astimezone().time(),
            final_horario__gte=self.check_out.astimezone().time(),
        ).descricao_alimentacao

    @property
    def opcionais_ceu(self):
        ceu = [op for op in self.opcionais_contratados if 'ceu' in op.categoria.nome_categoria]

        return ceu

    @property
    def minimo_pagantes(self):
        return self.orcamento_promocional.dados_pacote.minimo_de_pagantes if self.orcamento_promocional else 35

    @property
    def racional_cortesia(self):
        return self.orcamento_promocional.dados_pacote.regra_cortesia if self.orcamento_promocional else 15

    def colaborador_vendedora(self):
        try:
            return Vendedor.objects.get(usuario=self.colaborador)
        except Vendedor.DoesNotExist:
            return ''

    def delete(self, *args, **kwargs):
        id_orcamento = self.pk
        super(Orcamento, self).delete(*args, **kwargs)

        try:
            tratativa = Tratativas.objects.get(orcamentos__in=[id_orcamento])
        except Tratativas.DoesNotExist:
            ...
        else:
            if len(tratativa.orcamentos.all()) > 0:
                tratativa.delete()

    def get_periodo(self):
        check_in = self.check_in.strftime('%d/%m/%Y %H:%M')
        check_out = self.check_out.strftime('%d/%m/%Y %H:%M')

        return f'{check_in} - {check_out}'

    def serializar_objetos(self):
        obj = self
        dados = serializers.serialize('json', [obj, ])

        return json.loads(dados)[0]

    def valor_sem_desconto(self):
        return self.valor - self.desconto

    def dados_iniciais(self):
        return {
            'colaborador': self.colaborador.id,
            'monitoria': 0 if 'sem monitoria' in self.tipo_monitoria.nome_monitoria else 1,
            'onibus': 0 if self.transporte == 'não' else 1,
            'check_in': self.check_in,
            'check_out': self.check_out,
            'comissao': '0,00%',
            'valor_a_vista': str(self.valor).replace('.', ','),
            'inicio_vencimento': datetime.strptime(self.objeto_gerencia['data_pagamento'], '%Y-%m-%d'),
            'final_vencimento': datetime.strptime(self.objeto_gerencia['data_pagamento'], '%Y-%m-%d'),
            'razao_social': self.cliente.razao_social,
            'endereco': self.cliente.endereco,
            'cnpj': self.cliente.cnpj,
            'observacoes_orcamento': self.observacoes,
        }

    def listar_opcionais(self):
        ops_validos = []
        descritivo_opcionais = (self.objeto_orcamento['descricao_opcionais']).copy()

        if not self.promocional and self.orcamento_promocional:
            for op in descritivo_opcionais:
                if op['id'] in [o['id'] for o in self.orcamento_promocional.orcamento.objeto_orcamento['descricao_opcionais']]:
                    self.objeto_orcamento['descricao_opcionais'].remove(op)

                    continue
            ops_validos = self.objeto_orcamento['descricao_opcionais']
        else:
            ops_validos = self.objeto_orcamento['descricao_opcionais']

        return ops_validos

    def op_extra_formatado(self):
        op_extras = []

        if self.opcionais_extra:
            for op in self.opcionais_extra:
                op_extras.append({
                    'id': op['id'],
                    'nome': op['nome'],
                    'descricao': op['descricao'],
                    'valor': str(op['valor']).replace('.', ','),
                })

        return op_extras

    # -------------------------- Métodos pra tabelar os valores da tabela da ficha financeira --------------------------
    def datas_evento(self):
        data = self.check_in
        datas = []

        while data <= self.check_out:
            datas.append(data.strftime('%d/%m'))
            data += timedelta(days=1)

        return datas

    def valores_diaria(self):
        periodo = self.objeto_orcamento['periodo_viagem']
        diaria = self.objeto_orcamento['valores']['diaria']
        dia_dia = [str(a + b).replace('.', ',') for a, b in zip(periodo['valores'], diaria['valores'])]

        return {
            'valor_neto': f"{(diaria['valor'] + periodo['valor']):.2f}".replace('.', ','),
            'taxas': f"{(diaria['taxa_comercial'] + periodo['taxa_comercial']):.2f}".replace('.', ','),
            'cov': f"{(diaria['comissao_de_vendas'] + periodo['comissao_de_vendas']):.2f}".replace('.', ','),
            'desconto': f"{(diaria['desconto'] + periodo['desconto']):.2f}".replace('.', ','),
            'acrescimo': f"{(diaria['acrescimo'] + periodo['acrescimo']):.2f}".replace('.', ','),
            'valor_final': f"{(diaria['valor_final'] + periodo['valor_final']):.2f}".replace('.', ','),
            'dia_dia': dia_dia,
        }

    def valores_monitoria(self):
        monitoria = self.objeto_orcamento['valores']['tipo_monitoria']
        dia_dia = list(map(lambda a: str(round(a, 2)).replace('.', ','), monitoria['valores']))

        return {
            'valor_neto': f"{monitoria['valor']:.2f}".replace('.', ','),
            'taxas': f"{monitoria['taxa_comercial']:.2f}".replace('.', ','),
            'cov': f"{monitoria['comissao_de_vendas']:.2f}".replace('.', ','),
            'desconto': f"{monitoria['desconto']:.2f}".replace('.', ','),
            'acrescimo': f"{monitoria['acrescimo']:.2f}".replace('.', ','),
            'valor_final': f"{monitoria['valor_final']:.2f}".replace('.', ','),
            'dia_dia': dia_dia
        }

    def valores_transporte(self):
        transporte = self.objeto_orcamento['valores']['transporte']
        dia_dia = list(map(lambda a: str(round(a, 2)).replace('.', ','), transporte['valores']))

        return {
            'valor_neto': f"{transporte['valor']:.2f}".replace('.', ','),
            'taxas': f"{transporte['taxa_comercial']:.2f}".replace('.', ','),
            'cov': f"{transporte['comissao_de_vendas']:.2f}".replace('.', ','),
            'desconto': f"{transporte['desconto']:.2f}".replace('.', ','),
            'acrescimo': f"{transporte['acrescimo']:.2f}".replace('.', ','),
            'valor_final': f"{transporte['valor_final']:.2f}".replace('.', ','),
            'dia_dia': dia_dia,
        }

    def valores_opcionais(self):
        valores_atividades = self.objeto_orcamento['valores']['opcionais']
        descritivo_atividades = self.objeto_orcamento['descricao_opcionais']

        total_geral = total_sem_taxas = total_taxa = total_comissao = total_desconto = total_acrescimo = 0
        total_dia_dia = []
        atividades_ceu = []

        for atividade in descritivo_atividades:
            if atividade['categoria'] == 'extra':
                continue

            op = OrcamentoOpicional.objects.get(pk=atividade['id'])

            if not op.categoria.staff:
                dia_dia_ativ = list(map(lambda a: str(round(a, 2)).replace('.', ','), atividade['valores']))

                atividades_ceu.append({
                    'id': atividade['id'],
                    'atividade': atividade['nome'],
                    'valor_neto': f"{atividade['valor']:.2f}".replace('.', ','),
                    'valor_desconto': f"{atividade['valor_com_desconto']:.2f}".replace('.', ','),
                    'taxas': f"{atividade['taxa_comercial']:.2f}".replace('.', ','),
                    'cov': f"{atividade['comissao_de_vendas']:.2f}".replace('.', ','),
                    'desconto': f"{atividade['desconto']:.2f}".replace('.', ','),
                    'acrescimo': f"{atividade['acrescimo']:.2f}".replace('.', ','),
                    'valor_final': f"{atividade['valor_final']:.2f}".replace('.', ','),
                    'dia_dia': dia_dia_ativ
                })

                total_taxa += atividade["taxa_comercial"]
                total_comissao += atividade["comissao_de_vendas"]
                total_desconto += atividade["desconto"]
                total_acrescimo += atividade["acrescimo"]
                total_sem_taxas += atividade["valor"]
                total_geral += atividade["valor_final"]

                while len(total_dia_dia) < len(atividade["valores"]):
                    total_dia_dia.append(0)

                for i, valor in enumerate(atividade["valores"]):
                    total_dia_dia[i] += valor

        return {
            'valor_neto': f"{total_sem_taxas:.2f}".replace('.', ','),
            'taxas': f"{total_taxa:.2f}".replace('.', ','),
            'cov': f"{total_comissao:.2f}".replace('.', ','),
            'desconto': f"{total_desconto:.2f}".replace('.', ','),
            'acrescimo': f"{total_acrescimo:.2f}".replace('.', ','),
            'valor_final': f"{total_geral:.2f}".replace('.', ','),
            'dia_dia': total_dia_dia,
            'descritivo_atividades': atividades_ceu,
        }

    def valores_op_internos(self):
        descritivo_op_interno = self.objeto_orcamento['descricao_opcionais']
        total_geral = total_sem_taxas = total_taxa = total_comissao = total_desconto = total_acrescimo = 0
        total_dia_dia = []
        ops_interno = []

        for op in descritivo_op_interno:
            dia_dia_ativ = [0] * self.dias_evento
            i = 0
            op_id = op["id"]

            if op['categoria'] == 'extra':
                continue

            try:
                opcional = OrcamentoOpicional.objects.get(id=op_id)
            except OrcamentoOpicional.DoesNotExist:
                continue

            if opcional.categoria.staff:
                dia_dia_ativ[0] = op['valor']

                ops_interno.append({
                    'id': op['id'],
                    'atividade': op['nome'],
                    'valor_neto': f"{op['valor']:.2f}".replace('.', ','),
                    'valor_desconto': f"{op['valor_com_desconto']:.2f}".replace('.', ','),
                    'taxas': f"{op['taxa_comercial']:.2f}".replace('.', ','),
                    'cov': f"{op['comissao_de_vendas']:.2f}".replace('.', ','),
                    'desconto': f"{op['desconto']:.2f}".replace('.', ','),
                    'acrescimo': f"{op['acrescimo']:.2f}".replace('.', ','),
                    'valor_final': f"{op['valor_final']:.2f}".replace('.', ','),
                    'dia_dia': dia_dia_ativ
                })

                total_taxa += op["taxa_comercial"]
                total_comissao += op["comissao_de_vendas"]
                total_desconto += op["desconto"]
                total_acrescimo += op["acrescimo"]
                total_sem_taxas += op["valor"]
                total_geral += op["valor_final"]

                while len(total_dia_dia) < self.dias_evento:
                    total_dia_dia.append(0)

                while i < self.dias_evento:
                    if i == 0:
                        total_dia_dia[i] += op['valor']

                    i += 1

        return {
            'valor_neto': f"{total_sem_taxas:.2f}".replace('.', ','),
            'taxas': f"{total_taxa:.2f}".replace('.', ','),
            'cov': f"{total_comissao:.2f}".replace('.', ','),
            'desconto': f"{total_desconto:.2f}".replace('.', ','),
            'acrescimo': f"{total_acrescimo:.2f}".replace('.', ','),
            'valor_final': f"{total_geral:.2f}".replace('.', ','),
            'dia_dia': total_dia_dia,
            'descritivo_atividades': ops_interno,
        }

    def valores_outros(self):
        valores_outros = self.objeto_orcamento['valores']['opcionais_extras']
        descritivo_outros = self.objeto_orcamento['descricao_opcionais']
        outros = []
        total_dia_dia = []

        for outro in descritivo_outros:
            dia_dia_ativ = [0] * self.dias_evento
            i = 0

            try:
                outro['id'].isnumeric()
                # for atividade_extra in outro.get('outros'):
            except AttributeError:
                continue
            else:
                dia_dia_ativ[0] = outro['valor']

                outros.append({
                    'id': outro['id'],
                    'atividade': outro['nome'],
                    'valor_neto': f"{outro['valor']:.2f}".replace('.', ','),
                    'taxas': f"{outro['taxa_comercial']:.2f}".replace('.', ','),
                    'cov': f"{outro['comissao_de_vendas']:.2f}".replace('.', ','),
                    'desconto': f"{outro['desconto']:.2f}".replace('.', ','),
                    'acrescimo': f"{outro['acrescimo']:.2f}".replace('.', ','),
                    'valor_final': f"{outro['valor_final']:.2f}".replace('.', ','),
                    'dia_dia': dia_dia_ativ,
                    })

                while len(total_dia_dia) < self.dias_evento:
                    total_dia_dia.append(0)

                while i < self.dias_evento:
                    if i == 0:
                        total_dia_dia[i] += outro['valor']

                    i += 1

        return {
            'valor_neto': f"{valores_outros['valor']:.2f}".replace('.', ','),
            'taxas': f"{valores_outros['taxa_comercial']:.2f}".replace('.', ','),
            'cov': f"{valores_outros['comissao_de_vendas']:.2f}".replace('.', ','),
            'desconto': f"{valores_outros['desconto']:.2f}".replace('.', ','),
            'acrescimo': f"{valores_outros['acrescimo']:.2f}".replace('.', ','),
            'valor_final': f"{valores_outros['valor_final']:.2f}".replace('.', ','),
            'descritivo_atividades': outros,
            'dia_dia': total_dia_dia,
        }

    def valores_totais(self):
        totais = self.objeto_orcamento['total']
        dia_dia = list(map(lambda a: str(round(a, 2)).replace('.', ','), totais['valores']))

        return {
            'valor_neto': f"{totais['valor']:.2f}".replace('.', ','),
            'taxas': f"{totais['taxa_comercial']:.2f}".replace('.', ','),
            'cov': f"{totais['comissao_de_vendas']:.2f}".replace('.', ','),
            'desconto': f"{totais['desconto']:.2f}".replace('.', ','),
            'acrescimo': f"{totais['acrescimo']:.2f}".replace('.', ','),
            'valor_final': f"{totais['valor_final']:.2f}".replace('.', ','),
            'dia_dia': dia_dia,
        }


class OrcamentosPromocionais(models.Model):
    dados_pacote = models.ForeignKey(DadosDePacotes, on_delete=models.CASCADE)
    orcamento = models.ForeignKey(Orcamento, on_delete=models.CASCADE)
    liberado_para_venda = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Pacotes promocionais'
        verbose_name_plural = '08 - Pacotes construidos'

    def __str__(self):
        return self.dados_pacote.nome_do_pacote

    def valor_base(self):
        return self.orcamento.valor

    def validade(self):
        return self.orcamento.data_vencimento.strftime('%d/%m/%Y')

    def listar_ops_promocionais(self):
        return self.orcamento.objeto_orcamento['descricao_opcionais']

    def listar_opcionais(self):
        opcionais = self.orcamento.opcionais.all()
        lista_opcionais = {}

        for opcional in opcionais:
            if f'opcionais_{opcional.categoria.id}' not in lista_opcionais.keys():
                lista_opcionais[f'opcionais_{opcional.categoria.id}'] = [opcional.nome]
            else:
                lista_opcionais[f'opcionais_{opcional.categoria.id}'].append(opcional.nome)

        return lista_opcionais

    @classmethod
    def pegar_pacotes_promocionais(cls, n_dias, id_tipo_pacote, check_in, check_out):
        def comparar_intervalo():
            intervalos = []
            dias_semana_validos = []

            for p in pacote.dados_pacote.periodos_aplicaveis:
                intervalos.append(list(p.values())[0])
                dias_semana_validos.append(list(p.values())[1])

            for i, intervalo in enumerate(intervalos):
                cin, cout = intervalo.split(' - ')
                i_check_in = datetime.strptime(cin, '%d/%m/%Y').date()
                i_check_out = datetime.strptime(cout, '%d/%m/%Y').date()
                check_in_formatado = datetime.strptime(check_in, '%Y-%m-%d %H:%M').date()
                check_out_formatado = datetime.strptime(check_out, '%Y-%m-%d %H:%M').date()
                dias = [(check_in_formatado + timedelta(days=i)) for i in
                        range((check_out_formatado - check_in_formatado).days + 1)]
                dias_da_semana = list(map(lambda day: day.weekday(), dias))

                if check_in_formatado >= i_check_in and check_out_formatado <= i_check_out:
                    if all(dia in dias_semana_validos[i] for dia in dias_da_semana):
                        return True

            return False

        pacotes = cls.objects.filter(
            orcamento__data_vencimento__gte=datetime.today().date(),
            orcamento__previa=False,
            liberado_para_venda=True,
            dados_pacote__tipos_de_pacote_elegivel_id=int(id_tipo_pacote) if id_tipo_pacote != '' else 0
        )
        pacotes_validos = []

        for pacote in pacotes:
            if comparar_intervalo():
                # if int(id_tipo_pacote) if id_tipo_pacote != '' else 0 == pacote.dados_pacote.tipos_de_pacote_elegivel.id:
                # dados = serializers.serialize('json', [pacote.dados_pacote, ])
                # campos = json.loads(dados)[0]['fields']
                pacotes_validos.append({
                    'id': pacote.id,
                    'nome': pacote.dados_pacote.nome_do_pacote,
                })

        return pacotes_validos


class Tratativas(models.Model):
    cliente = models.ForeignKey(ClienteColegio, on_delete=models.CASCADE, verbose_name='Cliente')
    colaborador = models.ForeignKey(User, on_delete=models.DO_NOTHING, verbose_name='Colaborador')
    id_tratativa = models.CharField(primary_key=True, max_length=255, editable=False)
    orcamentos_em_previa = models.ManyToManyField(Orcamento, related_name='orcamentos_em_previa')
    orcamentos = models.ManyToManyField(Orcamento, verbose_name="Orcamentos", related_name='orcamentos')
    status = models.ForeignKey(StatusOrcamento, on_delete=models.DO_NOTHING, verbose_name='Status da Tratativa', default=1)
    motivo_recusa = models.TextField(verbose_name="Motivo da recusa", blank=True)
    orcamento_aceito = models.ForeignKey(
        Orcamento,
        verbose_name="Orcamento aceito",
        on_delete=models.DO_NOTHING,
        null=True,
        blank=True,
        related_name='orcamento_aceito'
    )
    ficha_financeira = models.BooleanField(default=False, verbose_name='Ficha financeira')

    @property
    def responsavel_tratativa(self):
        return self.orcamentos.all()[0].responsavel

    @property
    def colaborador_vendedora(self):
        try:
            return Vendedor.objects.get(usuario=self.colaborador)
        except Vendedor.DoesNotExist:
            return ''

    def orcamentos_ganhos(self):
        return list(self.orcamentos.filter(status_orcamento__aprovacao_cliente=True))

    @staticmethod
    @receiver(pre_delete, sender=User)
    def redefinir_colaborador(sender, instance, **kwargs):
        with transaction.atomic():
            try:
                diretoria = Vendedor.objects.filter(usuario__groups__name__icontains='diretoria')[0]
                Tratativas.objects.filter(colaborador=instance).update(colaborador=diretoria.usuario)
                Orcamento.objects.filter(colaborador=instance).update(colaborador=diretoria.usuario)
            except Exception as e:
                raise e

    def save(self, *args, **kwargs):
        if not self.id_tratativa:
            cnpj = self.cliente.cnpj
            data = datetime.now().date().strftime('%d%m%Y')
            fim = randint(11111111, 99999999)
            self.id_tratativa = f'{data}_{re.sub(r"[^a-zA-Z0-9]", "", cnpj)}_{fim}'

        super().save(*args, **kwargs)

    def pegar_orcamentos(self):
        orcamentos = []

        for orcamento in self.orcamentos.all():
            if not orcamento.previa:
                orcamentos.append({
                    'cliente': orcamento.cliente.__str__(),
                    'id_orcamento': orcamento.id,
                    'status': orcamento.status_orcamento.status,
                    'apelido': orcamento.apelido,
                    'vencimento': orcamento.data_vencimento.strftime('%d/%m/%Y'),
                    'data_edicao': orcamento.data_ultima_edicao.strftime('%d/%m/%Y %H:%M'),
                    'check_in': orcamento.check_in.astimezone().strftime('%d/%m/%Y %H:%M'),
                    'check_out': orcamento.check_out.astimezone().strftime('%d/%m/%Y %H:%M'),
                    'valor': str(orcamento.valor).replace('.', ','),
                })

        return orcamentos

    def status_tratativa(self):
        if self.orcamento_aceito:
            return 'Ganho'
        else:
            if self.status.status == 'Perdido':
                return self.status.status

            status_orcamentos = [orcamento.status_orcamento.status for orcamento in self.orcamentos.all()]

            if 'Em aberto' in status_orcamentos or 'Em análise' in status_orcamentos:
                return 'Em aberto'
            else:
                return 'Orcamentos vencidos e/ou perdido'

    def vencimento_tratativa(self):
        vencimentos = sorted([orcamento.data_vencimento for orcamento in self.orcamentos.all()])

        return vencimentos[0].strftime('%d/%m/%Y')

    def perder_orcamentos(self, id_orcamento):
        satus_perdido = StatusOrcamento.objects.get(negado_cliente=True)
        orcamento = self.orcamentos.all().get(pk=id_orcamento)
        orcamento.status_orcamento = satus_perdido
        orcamento.save()

    def ganhar_orcamento(self, id_orcamento_ganho):
        status_ganho = StatusOrcamento.objects.get(aprovacao_cliente=True)
        orcamento = self.orcamentos.all().get(pk=id_orcamento_ganho)
        orcamento.status_orcamento = status_ganho
        orcamento.save()

    def orcamentos_abertos(self):
        if self.orcamento_aceito:
            return [self.orcamento_aceito]

        status_perdido = StatusOrcamento.objects.get(negado_cliente=True)

        return self.orcamento_aceito if self.orcamento_aceito else self.orcamentos.all().exclude(
            status_orcamento=status_perdido)


class CadastroPacotePromocional(forms.ModelForm):
    class Meta:
        model = DadosDePacotes
        exclude = ()

        widgets = {
            'regra_cortesia': forms.NumberInput(attrs={'style': 'width: 15%'}),
            'limite_desconto_geral': forms.TextInput(),
        }

    def __init__(self, *args, **kwargs):
        super(CadastroPacotePromocional, self).__init__(*args, **kwargs)
        tipos_de_pacote = TiposDePacote.objects.all().order_by('titulo')

        self.fields['tipos_de_pacote_elegivel'].choices = [("", "---------")] + [
            (tipo.id, tipo.titulo) for tipo in tipos_de_pacote
        ]


class SeuModeloAdminForm(forms.ModelForm):
    class Meta:
        model = OrcamentoPeriodo
        fields = '__all__'

    def clean_dias_semana_validos(self):
        dias_semana_validos = self.cleaned_data.get('dias_semana_validos')
        inicio_vigencia = self.cleaned_data.get('inicio_vigencia')
        dias_selecionados = [dia.id_dia for dia in dias_semana_validos]

        periodos_conflitantes = OrcamentoPeriodo.objects.filter(
            inicio_vigencia__lte=inicio_vigencia,
            final_vigencia__gte=inicio_vigencia,
            dias_semana_validos__in=dias_selecionados
        ).exclude(pk=self.instance.pk)

        if periodos_conflitantes.exists():
            raise ValidationError('O grupo de períodos escolhidos já está cadastrado neste mesmo período de vigência.')

        return dias_semana_validos


class CadastroOrcamento(forms.ModelForm):
    class Meta:
        model = Orcamento
        exclude = ()

        widgets = {
            'promocional': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
            }),
            'produto': forms.Select(attrs={'disabled': True, 'onchange': 'verificar_preenchimento()'}),
            'tipo_de_pacote': forms.Select(attrs={'disabled': True, 'onchange': 'verificar_pacotes_promocionais()'}),
            'tipo_monitoria': forms.Select(attrs={'onchange': 'pegar_regra_cortesia()'}),
            'transporte': forms.RadioSelect(),
            'cliente': forms.Select(attrs={'onchange': 'gerar_responsaveis(this)'}),
            'responsavel': forms.Select(attrs={'disabled': True, 'onchange': 'liberar_periodo(this)'}),
            'orcamento_promocional': forms.Select(attrs={'disabled': True, 'onchange': 'mostrar_dados_pacote(this)'}),
        }

    def __init__(self, *args, **kwargs):
        super(CadastroOrcamento, self).__init__(*args, **kwargs)
        url = reverse('pacote_promocional')
        self.fields['promocional'].widget.attrs['onclick'] = f'window.location.href="{url}"'
        clientes = ClienteColegio.objects.all()
        responsaveis = Responsavel.objects.all()
        gerentes = [('', '')]
        responsaveis_cargo = [('', '')]
        clientes_cnpj = [('', '')]
        opcoes_validas_monitoria = [('', '')]

        if self.instance and self.instance.pk:
            valores_monitorias = OrcamentoMonitor.objects.filter(
                inicio_vigencia__year=self.instance.check_in.date().year,
                liberado=True,
            ).order_by('nome_monitoria')
        else:
            valores_monitorias = OrcamentoMonitor.objects.filter(
                inicio_vigencia__year=datetime.now().year,
                liberado=True,
            ).order_by('nome_monitoria')

        for cliente in clientes:
            clientes_cnpj.append((cliente.id, f'{cliente} ({cliente.cnpj})'))

        for responsavel in responsaveis:
            cargos = []

            for cargo in responsavel.cargo.all():
                if cargo != '':
                    cargos.append(cargo.cargo)

            if len(cargos) > 0:
                responsaveis_cargo.append((responsavel.id, f'{responsavel.nome} ({", ".join(cargos)})'))
            else:
                responsaveis_cargo.append((responsavel.id, responsavel.nome))

        for valor in valores_monitorias:
            opcoes_validas_monitoria.append((valor.id, valor.nome_monitoria))

        for gerente in User.objects.filter(groups__name__icontains='gerência'):
            gerentes.append((gerente.id, gerente.get_full_name()))

        self.fields['cliente'].choices = clientes_cnpj
        self.fields['responsavel'].choices = responsaveis_cargo
        self.fields['tipo_monitoria'].choices = opcoes_validas_monitoria
        self.fields['gerente_responsavel'].choices = gerentes

        # Inicializa um dicionário para armazenar os campos opcionais por categoria
        self.opcionais_por_categoria = {}

        # Itera sobre todas as categorias de opcionais
        for categoria in CategoriaOpcionais.objects.all():
            # Obtém os opcionais pertencentes a essa categoria

            if self.instance.pk is None or self.instance.previa:
                opcionais = OrcamentoOpicional.objects.filter(
                    categoria=categoria,
                    inicio_vigencia__lte=timezone.now().date(),
                    final_vigencia__gte=timezone.now().date(),
                    liberado=True
                ).order_by('nome')
            else:
                opcionais = OrcamentoOpicional.objects.filter(
                    categoria=categoria,
                    liberado=True
                ).order_by('nome')
            # Define um nome e id customizado para o campo
            field_name = f'opcionais_{categoria.id}'

            # Cria um campo ModelMultipleChoiceField para esses opcionais usando Select com multiple
            self.fields[field_name] = forms.ModelMultipleChoiceField(
                queryset=opcionais,
                required=False,
                widget=forms.SelectMultiple(attrs={
                    'id': f'opcionais_{categoria.id}',
                    'name': 'opcionais',
                }),
                label=categoria.nome_categoria,
            )
            # Inicializa o campo se o objeto do formulário já tiver sido criado
            if self.instance.pk:
                initial_values = self.instance.opcionais.filter(categoria=categoria).values_list('id', flat=True)
                self.fields[field_name].initial = list(initial_values)

            # Armazena o campo no dicionário
            self.opcionais_por_categoria[categoria.nome_categoria] = self[field_name]


class CadastroHorariosPadroesAdmin(forms.ModelForm):
    class Meta:
        model = HorariosPadroes
        fields = '__all__'
        widgets = {
            'entrada_saida': forms.RadioSelect(choices=((True, 'Entrada'), (False, 'Saída'))),
        }
