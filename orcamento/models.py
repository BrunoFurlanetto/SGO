import datetime
import json
import re
from random import randint

from django import forms
from django.contrib.auth.models import User
from django.core import serializers
from django.core.exceptions import ValidationError
from django.db import models, transaction
from django.db.models import PositiveIntegerField
from django.db.models.signals import pre_delete, pre_save, post_save
from django.dispatch import receiver
from django.utils import timezone
from unidecode import unidecode
from django.contrib.postgres.fields import ArrayField

from ceu.models import Atividades
from peraltas.models import ClienteColegio, Responsavel, EmpresaOnibus, Vendedor, ProdutosPeraltas, AtividadesEco


def default_validade():
    return timezone.now() + timezone.timedelta(days=180)


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
    aparecer_comercial = models.BooleanField(help_text='Se essa taxa deve ou não ser vista pelo comercial', default=True)
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
            return (datetime.datetime.today() + datetime.timedelta(days=int(self.valor_padrao))).strftime('%Y-%m-%d')

        if self.comportamento == 'monetario':
            return f'R$ {self.valor_padrao:.2f}'

        if self.comportamento == 'numerico':
            return int(self.valor_padrao)

    @property
    def valor_minimo_formatado(self):
        if self.comportamento == 'porcentagem':
            return f'{self.valor_minimo}%'.replace('.', ',')

        if self.comportamento == 'intervalo_dias':
            return (datetime.datetime.today() + datetime.timedelta(days=int(self.valor_minimo))).strftime('%Y-%m-%d')

        if self.comportamento == 'monetario':
            return f'R$ {self.valor_minimo:.2f}'

        if self.comportamento == 'numerico':
            return int(self.valor_minimo)

    @property
    def valor_maximo_formatado(self):
        if self.comportamento == 'porcentagem':
            return f'{self.valor_maximo}%'.replace('.', ',')

        if self.comportamento == 'intervalo_dias':
            return (datetime.datetime.today() + datetime.timedelta(days=int(self.valor_maximo))).strftime('%Y-%m-%d')

        if self.valor_maximo and self.comportamento == 'monetario':
            return f'R$ {self.valor_maximo:.2f}'

        if self.comportamento == 'numerico':
            return int(self.valor_maximo)

    def __str__(self):
        return self.nome_taxa

    def save(self, *args, **kwargs):
        if not self.pk:
            self.id_taxa = unidecode(self.nome_taxa).lower().replace(' ', '_')

        super().save(*args, **kwargs)

    @classmethod
    def listar_valores(cls):
        valores = cls.objects.all()
        lista_valores = {}

        for valor in valores:
            lista_valores[valor.id_taxa] = valor.valor_padrao

        return lista_valores


class OrcamentoMonitor(models.Model):
    nome_monitoria = models.CharField(max_length=100)
    descricao_monitoria = models.TextField(blank=True)
    valor = models.DecimalField(decimal_places=2, max_digits=5, default=0.00)
    inicio_vigencia = models.DateField()
    final_vigencia = models.DateField(default=default_validade)
    racional_monitoria = models.PositiveIntegerField(
        default=8, verbose_name="Racional Monitoria")

    class Meta:
        verbose_name = 'Valor monitoria'
        verbose_name_plural = '05 - Valores de monitoria'

    def __str__(self):
        return self.nome_monitoria


class CategoriaOpcionais(models.Model):
    nome_categoria = models.CharField(max_length=100)

    class Meta:
        verbose_name = 'Categoria'
        verbose_name_plural = '07a - Categorias de opcionais'

    def __str__(self):
        return self.nome_categoria


class OrcamentoOpicional(models.Model):
    nome = models.CharField(max_length=100)
    categoria = models.ForeignKey(CategoriaOpcionais, on_delete=models.DO_NOTHING, null=True, blank=True)
    descricao = models.TextField()
    valor = models.DecimalField(decimal_places=2, max_digits=5, default=0.00)
    inicio_vigencia = models.DateField()
    final_vigencia = models.DateField(default=default_validade)

    class Meta:
        verbose_name = 'Valor opcionais'
        verbose_name_plural = '07b - Valores de opcionais'

    def __str__(self):
        return self.nome


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
    descricao = models.TextField(blank=True)
    liberado = models.BooleanField(default=False, help_text='Liberado para o comercial')
    id_periodo = models.CharField(max_length=255, unique=True, primary_key=True, editable=False)


    class Meta:
        verbose_name = 'Valor do periodo'
        verbose_name_plural = '03 - Valores de diárias'

    def __str__(self):
        return self.nome_periodo


class TaxaPeriodo(models.Model):
    inicio_vigencia = models.DateField(default=timezone.now)
    final_vigencia = models.DateField(default=default_validade)
    descricao = models.TextField(blank=True)
    valor = models.DecimalField(decimal_places=2, max_digits=7, default=0.00)

    class Meta:
        verbose_name = 'Valor da taxa do periodo'
        verbose_name_plural = '04 - Valores da taxa dos periodos'


class HorariosPadroes(models.Model):
    refeicao = models.CharField(max_length=50, verbose_name='Título')
    horario = models.TimeField(verbose_name='Horário início')
    final_horario = models.TimeField(verbose_name='Horário final')
    entrada_saida = models.BooleanField()
    racional = models.DecimalField(max_digits=3, decimal_places=2, default=1.00, help_text='Número de diárias de hotelaria')
    racional_monitor = models.DecimalField(max_digits=3, decimal_places=2, default=1.00, help_text='Número de diárias de monitoria')
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
    valor_2_dia = models.DecimalField(
        max_digits=7, decimal_places=2, verbose_name='Valor de 2 dias')
    valor_3_dia = models.DecimalField(
        max_digits=7, decimal_places=2, verbose_name='Valor de 3 dias')
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
    inicio_validade = models.DateField(verbose_name='Inicio vigência dos valores', default=timezone.now)
    final_validade = models.DateField(verbose_name='Final vigência dos valores', default=default_validade)
    descricao = models.TextField(verbose_name="Descrição", default="")

    class Meta:
        verbose_name = 'Valor do transporte'
        verbose_name_plural = '06 - Valores de transporte'

    def __str__(self):
        return f'Valores do transporte de {self.inicio_validade.strftime("%d/%m/%Y")} até {self.final_validade.strftime("%d/%m/%Y")}'

    @property
    def inicio_vigencia(self):
        return self.inicio_validade.strftime('%d/%m/%Y')

    @property
    def final_vigencia(self):
        return self.final_validade.strftime('%d/%m/%Y')


class StatusOrcamento(models.Model):
    status = models.CharField(max_length=100)

    def __str__(self):
        return self.status


class DadosDePacotes(models.Model):
    nome_do_pacote = models.CharField(max_length=255, verbose_name="Nome do Pacote")
    limite_desconto_geral = models.DecimalField(verbose_name="Limite de desconto geral", decimal_places=2, max_digits=5)
    minimo_de_diarias = models.PositiveIntegerField(verbose_name="Minimo de diarias")
    maximo_de_diarias = models.PositiveIntegerField(verbose_name="Maximo de diarias")
    minimo_de_pagantes = models.PositiveIntegerField(verbose_name="Minimo de pagantes")
    produtos_elegiveis = models.ManyToManyField(ProdutosPeraltas, verbose_name="Produtos elegíveis")
    cortesia = models.BooleanField(default=False, verbose_name="Cortesia")
    limite_cortesia = models.PositiveIntegerField(verbose_name="Limite de cortesias", blank=True, null=True)
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

        if dados.getlist('produtos_elegiveis[]'):
            lista = [int(i) for i in dados.getlist('produtos_elegiveis[]')]
        else:
            lista = [int(dados.get('produtos_elegiveis'))]

        dados_tratados['produtos_elegiveis'] = lista
        dados_tratados['periodos_aplicaveis'] = DadosDePacotes.juntar_periodos(dados)

        return dados_tratados

    @staticmethod
    def juntar_periodos(dados_pacote):
        periodo_n = 1
        periodos = []

        while True:
            if dados_pacote.get(f'periodo_{periodo_n}', None):
                periodos.append({
                    f'periodo_{periodo_n}': dados_pacote.get(f'periodo_{periodo_n}')
                })
            else:
                break

            periodo_n += 1

        return periodos

    def serializar_objetos(self):
        obj = self
        dados = serializers.serialize('json', [obj, ])

        return json.loads(dados)[0]


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
    produto = models.ForeignKey(
        ProdutosPeraltas,
        on_delete=models.CASCADE,
        verbose_name='Produto Peraltas',
        blank=True,
        null=True)
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
    motivo_recusa = models.CharField(blank=True, null=True, max_length=255, verbose_name='Motivo da recusa')
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
    promocional = models.BooleanField(default=False)
    status_orcamento = models.ForeignKey(
        StatusOrcamento,
        on_delete=models.DO_NOTHING,
        blank=True,
        null=True,
        verbose_name='Status'
    )
    previa = models.BooleanField(default=True)
    data_preenchimento = models.DateField(auto_now_add=True, verbose_name='Data de preenchimento')
    data_vencimento = models.DateField(verbose_name='Data de vencimento')
    data_ultima_edicao = models.DateField(
        blank=True,
        null=True,
        auto_now=True,
        verbose_name='Data da ultima edição'
    )

    class Meta:
        verbose_name = 'Orçamento'
        verbose_name_plural = '09 - Orçamentos criados'

    def __str__(self):
        if not self.promocional:
            return f'Orçamento de {self.cliente}'
        else:
            return f'Orçamento promocional {self.id}'

    @property
    def oficina_de_foguetes(self):
        foguetes = self.opcionais_ceu.all().filter(atividade__icontains='foguete')

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
            'responsavel_operacional': str(self.responsavel.id),
            'colaborador': self.colaborador.id,
            'monitoria': 0 if 'sem monitoria' in self.tipo_monitoria.nome_monitoria else 1,
            'onibus': 0 if self.transporte == 'não' else 1,
            'check_in': self.check_in,
            'check_out': self.check_out,
            'comissao': '0,00%',
            'valor_a_vista': str(self.valor).replace('.', ','),
            'inicio_vencimento': datetime.datetime.strptime(self.objeto_gerencia['data_pagamento'], '%Y-%m-%d'),
            'final_vencimento': datetime.datetime.strptime(self.objeto_gerencia['data_pagamento'], '%Y-%m-%d'),
            'razao_social': self.cliente.razao_social,
            'endereco': self.cliente.endereco,
            'cnpj': self.cliente.cnpj,
            'observacoes_orcamento': self.observacoes,
        }

    def listar_opcionais(self):
        return self.objeto_orcamento['descricao_opcionais']

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
            data += datetime.timedelta(days=1)

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
            'valor_final': f"{transporte['valor_final']:.2f}".replace('.', ','),
            'dia_dia': dia_dia,
        }

    def valores_ceu(self):
        valores_atividades = self.objeto_orcamento['valores']['opcionais_ceu']
        descritivo_atividades = self.objeto_orcamento['descricao_opcionais']
        dia_dia = list(map(lambda a: str(round(a, 2)).replace('.', ','), valores_atividades['valores']))
        atividades_ceu = []

        for atividade in descritivo_atividades:
            if atividade['categoria'] == 'ceu':
                dia_dia_ativ = list(map(lambda a: str(round(a, 2)).replace('.', ','), atividade['valores']))

                atividades_ceu.append({
                    'id': atividade['id'],
                    'atividade': atividade['nome'],
                    'valor_neto': f"{atividade['valor']:.2f}".replace('.', ','),
                    'valor_desconto': f"{atividade['valor_com_desconto']:.2f}".replace('.', ','),
                    'taxas': f"{atividade['taxa_comercial']:.2f}".replace('.', ','),
                    'cov': f"{atividade['comissao_de_vendas']:.2f}".replace('.', ','),
                    'desconto': f"{atividade['desconto']:.2f}".replace('.', ','),
                    'valor_final': f"{atividade['valor_final']:.2f}".replace('.', ','),
                    'dia_dia': dia_dia_ativ
                })

        return {
            'valor_neto': f"{valores_atividades['valor']:.2f}".replace('.', ','),
            'taxas': f"{valores_atividades['taxa_comercial']:.2f}".replace('.', ','),
            'cov': f"{valores_atividades['comissao_de_vendas']:.2f}".replace('.', ','),
            'desconto': f"{valores_atividades['desconto']:.2f}".replace('.', ','),
            'valor_final': f"{valores_atividades['valor_final']:.2f}".replace('.', ','),
            'descritivo_atividades': atividades_ceu,
            'dia_dia': dia_dia,
        }

    def valores_peraltas(self):
        valores_atividades = self.objeto_orcamento['valores']['opcionais_ecoturismo']
        descritivo_atividades = self.objeto_orcamento['descricao_opcionais']
        dia_dia = list(map(lambda a: str(round(a, 2)).replace('.', ','), valores_atividades['valores']))
        atividades_peraltas = []

        for atividade in descritivo_atividades:
            if atividade['categoria'] == 'outros':
                dia_dia_ativ = list(map(lambda a: str(round(a, 2)).replace('.', ','), atividade['valores']))

                atividades_peraltas.append({
                    'id': atividade['id'],
                    'atividade': atividade['nome'],
                    'valor_neto': f"{atividade['valor']:.2f}".replace('.', ','),
                    'valor_desconto': f"{atividade['valor_com_desconto']:.2f}".replace('.', ','),
                    'taxas': f"{atividade['taxa_comercial']:.2f}".replace('.', ','),
                    'cov': f"{atividade['comissao_de_vendas']:.2f}".replace('.', ','),
                    'desconto': f"{atividade['desconto']:.2f}".replace('.', ','),
                    'valor_final': f"{atividade['valor_final']:.2f}".replace('.', ','),
                    'dia_dia': dia_dia_ativ,
                })

        return {
            'valor_neto': f"{valores_atividades['valor']:.2f}".replace('.', ','),
            'taxas': f"{valores_atividades['taxa_comercial']:.2f}".replace('.', ','),
            'cov': f"{valores_atividades['comissao_de_vendas']:.2f}".replace('.', ','),
            'desconto': f"{valores_atividades['desconto']:.2f}".replace('.', ','),
            'valor_final': f"{valores_atividades['valor_final']:.2f}".replace('.', ','),
            'descritivo_atividades': atividades_peraltas,
            'dia_dia': dia_dia,
        }

    def valores_opcionais(self):
        valores_opcionais = self.objeto_orcamento['valores']['outros_opcionais']
        descritivo_opcionais = self.objeto_orcamento['descricao_opcionais']
        dia_dia = list(map(lambda a: str(round(a, 2)).replace('.', ','), valores_opcionais['valores']))
        opcionais = []

        for opcional in descritivo_opcionais:
            if opcional['categoria'] == 'extras':
                dia_dia_op = list(map(lambda a: str(round(a, 2)).replace('.', ','), opcional['valores']))

                opcionais.append({
                    'id': opcional['id'],
                    'atividade': opcional['nome'],
                    'valor_neto': f"{opcional['valor']:.2f}".replace('.', ','),
                    'valor_desconto': f"{opcional['valor_com_desconto']:.2f}".replace('.', ','),
                    'taxas': f"{opcional['taxa_comercial']:.2f}".replace('.', ','),
                    'cov': f"{opcional['comissao_de_vendas']:.2f}".replace('.', ','),
                    'desconto': f"{opcional['desconto']:.2f}".replace('.', ','),
                    'valor_final': f"{opcional['valor_final']:.2f}".replace('.', ','),
                    'dia_dia': dia_dia_op,
                })

        return {
            'valor_neto': f"{valores_opcionais['valor']:.2f}".replace('.', ','),
            'taxas': f"{valores_opcionais['taxa_comercial']:.2f}".replace('.', ','),
            'cov': f"{valores_opcionais['comissao_de_vendas']:.2f}".replace('.', ','),
            'desconto': f"{valores_opcionais['desconto']:.2f}".replace('.', ','),
            'valor_final': f"{valores_opcionais['valor_final']:.2f}".replace('.', ','),
            'descritivo_atividades': opcionais,
            'dia_dia': dia_dia,
        }

    def valores_outros(self):
        valores_outros = self.objeto_orcamento['valores']['opcionais_extras']
        descritivo_outros = self.objeto_orcamento['descricao_opcionais']
        dia_dia = list(map(lambda a: str(round(a, 2)).replace('.', ','), valores_outros['valores']))
        outros = []

        for outro in descritivo_outros:
            if outro.get('outros'):
                for atividade_extra in outro.get('outros'):
                    dia_dia_ativ = list(map(lambda a: str(round(a, 2)).replace('.', ','), atividade_extra['valores']))

                    outros.append({
                        'id': atividade_extra['id'],
                        'atividade': atividade_extra['nome'],
                        'valor_neto': f"{atividade_extra['valor']:.2f}".replace('.', ','),
                        'taxas': f"{atividade_extra['taxa_comercial']:.2f}".replace('.', ','),
                        'cov': f"{atividade_extra['comissao_de_vendas']:.2f}".replace('.', ','),
                        'desconto': f"{atividade_extra['desconto']:.2f}".replace('.', ','),
                        'valor_final': f"{atividade_extra['valor_final']:.2f}".replace('.', ','),
                        'dia_dia': dia_dia_ativ,
                    })

        return {
            'valor_neto': f"{valores_outros['valor']:.2f}".replace('.', ','),
            'taxas': f"{valores_outros['taxa_comercial']:.2f}".replace('.', ','),
            'cov': f"{valores_outros['comissao_de_vendas']:.2f}".replace('.', ','),
            'desconto': f"{valores_outros['desconto']:.2f}".replace('.', ','),
            'valor_final': f"{valores_outros['valor_final']:.2f}".replace('.', ','),
            'descritivo_atividades': outros,
            'dia_dia': dia_dia,
        }

    def valores_totais(self):
        totais = self.objeto_orcamento['total']
        dia_dia = list(map(lambda a: str(round(a, 2)).replace('.', ','), totais['valores']))

        return {
            'valor_neto': f"{totais['valor']:.2f}".replace('.', ','),
            'taxas': f"{(totais['taxa_comercial'] + self.objeto_orcamento['periodo_viagem']['valor']):.2f}".replace('.', ','),
            'cov': f"{totais['comissao_de_vendas']:.2f}".replace('.', ','),
            'desconto': f"{totais['desconto']:.2f}".replace('.', ','),
            'valor_final': f"{totais['valor_final']:.2f}".replace('.', ','),
            'dia_dia': dia_dia,
        }


class OrcamentosPromocionais(models.Model):
    dados_pacote = models.ForeignKey(DadosDePacotes, on_delete=models.CASCADE)
    orcamento = models.ForeignKey(Orcamento, on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Pacotes promocionais'
        verbose_name_plural = '08 - Pacotes construidos'

    def __str__(self):
        return self.dados_pacote.nome_do_pacote

    def valor_base(self):
        return self.orcamento.valor

    def validade(self):
        return self.orcamento.data_vencimento.strftime('%d/%m/%Y')

    @classmethod
    def pegar_pacotes_promocionais(cls, n_dias, id_produto, check_in, check_out):
        def comparar_intervalo():
            intervalos = [valor for p in pacote.dados_pacote.periodos_aplicaveis for valor in p.values()]

            for intervalo in intervalos:
                cin, cout = intervalo.split(' - ')
                i_check_in = datetime.datetime.strptime(cin, '%d/%m/%Y').date()
                i_check_out = datetime.datetime.strptime(cout, '%d/%m/%Y').date()
                check_in_formatado = datetime.datetime.strptime(check_in, '%Y-%m-%d %H:%M').date()
                check_out_formatado = datetime.datetime.strptime(check_out, '%Y-%m-%d %H:%M').date()

                if check_in_formatado >= i_check_in and check_out_formatado <= i_check_out:
                    return True

            return False

        pacotes = cls.objects.filter(
            orcamento__data_vencimento__gte=datetime.date.today(),
            orcamento__previa=False,
        )
        pacotes_validos = []

        for pacote in pacotes:
            if comparar_intervalo():
                if pacote.dados_pacote.minimo_de_diarias <= n_dias <= pacote.dados_pacote.maximo_de_diarias:
                    if id_produto in [p.id for p in pacote.dados_pacote.produtos_elegiveis.all()]:
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
    orcamentos = models.ManyToManyField(Orcamento, verbose_name="Orcamentos", related_name='orcamentos')
    status = models.ForeignKey(StatusOrcamento, on_delete=models.DO_NOTHING, verbose_name='Status da Tratativa',
                               default=1)
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
            data = datetime.datetime.now().date().strftime('%d%m%Y')
            fim = randint(11111111, 99999999)
            self.id_tratativa = f'{data}_{re.sub(r"[^a-zA-Z0-9]", "", cnpj)}_{fim}'

        super().save(*args, **kwargs)

    def pegar_orcamentos(self):
        orcamentos = []

        for orcamento in self.orcamentos.all():
            if not orcamento.previa:
                orcamentos.append({
                    'id_orcamento': orcamento.id,
                    'status': orcamento.status_orcamento.status,
                    'vencimento': orcamento.data_vencimento.strftime('%d/%m/%Y'),
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

    def perder_orcamentos(self):
        satus_perdido = StatusOrcamento.objects.get(status__icontains='perdido')
        self.orcamentos.all().update(status_orcamento=satus_perdido)

    def ganhar_orcamento(self, id_orcamento_ganho):
        status_ganho = StatusOrcamento.objects.get(status__icontains='ganho')
        status_perdido = StatusOrcamento.objects.get(status__icontains='perdido')

        for orcamento in self.orcamentos.all():
            if orcamento.id == id_orcamento_ganho:
                orcamento.status_orcamento = status_ganho
                self.orcamento_aceito = orcamento
            else:
                orcamento.status_orcamento = status_perdido

            orcamento.save()

        self.status = status_ganho
        self.save()

    def orcamentos_abertos(self):
        if self.orcamento_aceito:
            return [self.orcamento_aceito]

        status_perdido = StatusOrcamento.objects.get(status__icontains='perdido')

        return self.orcamento_aceito if self.orcamento_aceito else self.orcamentos.all().exclude(
            status_orcamento=status_perdido)


class CadastroPacotePromocional(forms.ModelForm):
    class Meta:
        model = DadosDePacotes
        exclude = ()

        widgets = {
            'cortesia': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
                'onchange': 'mostrar_limite_cortesia(this)'
            }),
            'limite_desconto_geral': forms.TextInput(),
        }


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
            'promocional': forms.CheckboxInput(attrs={'class': 'form-check-input', 'onchange': 'montar_pacote(this)'}),
            'produto': forms.Select(attrs={'disabled': True, 'onchange': 'verificar_produto()'}),
            'transporte': forms.RadioSelect(),
            'cliente': forms.Select(attrs={'onchange': 'gerar_responsaveis(this)'}),
            'responsavel': forms.Select(attrs={'disabled': True, 'onchange': 'liberar_periodo(this)'}),
            'orcamento_promocional': forms.Select(attrs={'disabled': True, 'onchange': 'mostrar_dados_pacote(this)'}),
        }

    def __init__(self, *args, **kwargs):
        super(CadastroOrcamento, self).__init__(*args, **kwargs)
        clientes = ClienteColegio.objects.all()
        responsaveis = Responsavel.objects.all()
        responsaveis_cargo = [('', '')]
        clientes_cnpj = [('', '')]

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

        self.fields['cliente'].choices = clientes_cnpj
        self.fields['responsavel'].choices = responsaveis_cargo

        # Inicializa um dicionário para armazenar os campos opcionais por categoria
        self.opcionais_por_categoria = {}

        # Itera sobre todas as categorias de opcionais
        for categoria in CategoriaOpcionais.objects.all():
            # Obtém os opcionais pertencentes a essa categoria
            opcionais = OrcamentoOpicional.objects.filter(
                categoria=categoria,
                inicio_vigencia__lte=timezone.now().date(),
                final_vigencia__gte=timezone.now().date()
            )
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
