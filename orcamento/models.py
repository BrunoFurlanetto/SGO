import datetime
import json
import re

from django import forms
from django.contrib.auth.models import User
from django.core import serializers
from django.db import models
from django.db.models import PositiveIntegerField
from django.db.models.signals import pre_delete
from django.dispatch import receiver
from django.utils import timezone
from unidecode import unidecode

from ceu.models import Atividades
from peraltas.models import ClienteColegio, Responsavel, EmpresaOnibus, Vendedor, ProdutosPeraltas, AtividadesEco


class ValoresPadrao(models.Model):
    nome_taxa = models.CharField(max_length=255, verbose_name='Nome da taxa')
    valor = models.DecimalField(verbose_name='Valor', decimal_places=2, max_digits=4)
    descricao = models.TextField(verbose_name='Descrição da taxa')
    id_taxa = models.CharField(max_length=255, editable=False)

    def __str__(self):
        return self.nome_taxa

    def save(self, *args, **kwargs):
        self.id_taxa = unidecode(self.nome_taxa).lower().replace(' ', '_')
        super().save(*args, **kwargs)

    @classmethod
    def listar_valores(cls):
        valores = cls.objects.all()
        lista_valores = {}

        for valor in valores:
            lista_valores[valor.id_taxa] = valor.valor

        return lista_valores


class OrcamentoMonitor(models.Model):
    nome_monitoria = models.CharField(max_length=100)
    descricao_monitoria = models.TextField(blank=True)
    valor = models.DecimalField(decimal_places=2, max_digits=5, default=0.00)
    racional_monitoria = models.PositiveIntegerField(
        default=8, verbose_name="Racional Monitoria")

    def __str__(self):
        return self.nome_monitoria


class OrcamentoOpicional(models.Model):
    nome = models.CharField(max_length=100)
    descricao = models.TextField(default='Opcional combinado com o cliente')
    valor = models.DecimalField(decimal_places=2, max_digits=5, default=0.00)
    fixo = models.BooleanField(default=False, verbose_name='Opcional fixo')

    def __str__(self):
        return self.nome


class OrcamentoPeriodo(models.Model):
    semestre_choice = (
        (1, 'Primeiro'),
        (2, 'Segundo'),
    )

    dias_choice = (
        (1, 'Meio de semana'),
        (2, 'Fim de semana'),
        (3, 'Qualquer dia'),
    )

    nome_periodo = models.CharField(max_length=255)
    ano = models.PositiveIntegerField(default=timezone.now().year, verbose_name='Ano')
    semestre = models.PositiveIntegerField(choices=semestre_choice, verbose_name='Semestre', default=semestre_choice[0][0])
    dias_validos = models.IntegerField(choices=dias_choice, verbose_name='Dias validos', default=dias_choice[0][0])
    valor = models.DecimalField(decimal_places=2, max_digits=5, default=0.00)
    taxa_periodo = models.DecimalField(decimal_places=2, max_digits=5)
    descricao = models.TextField(blank=True)
    id = models.CharField(max_length=11, unique=True, primary_key=True, editable=False)

    def __str__(self):
        return self.nome_periodo

    def save(self, *args, **kwargs):
        semestre = 'PS' if self.semestre == 1 else 'SS'
        ano = self.ano

        if self.dias_validos == 1:
            dias = 'MS'
        elif self.dias_validos == 2:
            dias = 'FS'
        else:
            dias = 'QD'

        self.id = f'{dias}{semestre}{ano}'
        super().save(*args, **kwargs)


class OrcamentoAlimentacao(models.Model):
    tipo_alimentacao = models.CharField(max_length=100)
    descricao = models.TextField(blank=True)
    valor = models.DecimalField(decimal_places=2, max_digits=5, default=0.00)


class OrcamentoDiaria(models.Model):
    periodo = models.ForeignKey(
        OrcamentoPeriodo, on_delete=models.CASCADE, verbose_name='Periodo'
    )
    descricao = models.TextField(blank=True)
    valor = models.DecimalField(decimal_places=2, max_digits=7, default=0.00)


class HorariosPadroes(models.Model):
    refeicao = models.CharField(max_length=50, verbose_name='Refeição')
    horario = models.TimeField(verbose_name='Horário')
    entrada = models.BooleanField(default=True)
    racional = models.DecimalField(max_digits=3, decimal_places=2, default=1.00)
    racional_monitor = models.DecimalField(max_digits=3, decimal_places=2, default=1.00)

    def __str__(self):
        return f'Horário {self.refeicao}'


class ValoresTransporte(models.Model):
    periodo = models.ForeignKey(
        OrcamentoPeriodo, on_delete=models.CASCADE, verbose_name="Período")
    valor_1_dia = models.DecimalField(
        max_digits=7, decimal_places=2, verbose_name='Valor de 1 dia')
    valor_2_dia = models.DecimalField(
        max_digits=7, decimal_places=2, verbose_name='Valor de 2 dias')
    valor_3_dia = models.DecimalField(
        max_digits=7, decimal_places=2, verbose_name='Valor de 3 dias')
    valor_acrescimo = models.DecimalField(
        max_digits=7, decimal_places=2, verbose_name='Acréscimo')
    leva_e_busca = models.DecimalField(
        max_digits=7, decimal_places=2, verbose_name='Leva e Busca', default=0.00)
    vai_e_volta = models.DecimalField(
        max_digits=7, decimal_places=2, verbose_name='Vai e Volta', default=0.00)
    percentual = models.DecimalField(
        max_digits=3, decimal_places=2, verbose_name='Percentual', default=0.10)
    descricao = models.TextField(verbose_name="Descrição", default="")

    def __str__(self):
        return f'Valores transporte periodo {self.periodo.nome_periodo}'


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
    pacote_promocional = models.ForeignKey(
        DadosDePacotes,
        verbose_name='Pacote promocional',
        on_delete=models.DO_NOTHING,
        blank=True,
        null=True
    )
    orcamento_promocional = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        on_delete=models.DO_NOTHING,
        verbose_name='Orçamento promocional'
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
        related_name='opcionais'
    )
    opcionais_extra = models.JSONField(blank=True, null=True, verbose_name='Opcionais extra')
    atividades = models.ManyToManyField(AtividadesEco, blank=True, verbose_name='Atividades Peraltas')
    atividades_ceu = models.ManyToManyField(Atividades, blank=True, verbose_name='Atividades CEU')
    desconto = models.DecimalField(blank=True, null=True, max_digits=4, decimal_places=2, verbose_name='Desconto')
    valor = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Valor orçamento')
    colaborador = models.ForeignKey(User, on_delete=models.CASCADE, blank=True)
    observacoes = models.TextField(blank=True, verbose_name='Observações')
    motivo_recusa = models.CharField(blank=True, null=True, max_length=255, verbose_name='Motivo da recusa')
    objeto_gerencia = models.JSONField(blank=True, null=True)
    objeto_orcamento = models.JSONField(blank=True, null=True)
    promocional = models.BooleanField(default=False)
    aprovado = models.BooleanField(default=False)
    necessita_aprovacao_gerencia = models.BooleanField(default=False, verbose_name='Necessita de aprovação da gerência')
    status_orcamento = models.ForeignKey(
        StatusOrcamento,
        on_delete=models.DO_NOTHING,
        blank=True,
        null=True,
        verbose_name='Status'
    )
    data_preenchimento = models.DateField(auto_now_add=True, verbose_name='Data de preenchimento')
    data_vencimento = models.DateField(verbose_name='Data de vencimento')
    data_ultima_edicao = models.DateField(
        blank=True,
        null=True,
        default=datetime.datetime.now,
        verbose_name='Data da ultima edição'
    )

    def __str__(self):
        return f'Orçamento de {self.cliente}'

    def get_periodo(self):
        check_in = self.check_in.strftime('%d/%m/%Y %H:%M')
        check_out = self.check_out.strftime('%d/%m/%Y %H:%M')

        return f'{check_in} - {check_out}'

    @staticmethod
    def pegar_pacotes_promocionais(n_dias, id_produto, check_in, check_out):
        def comparar_intervalo():
            intervalos = [valor for p in pacote.pacote_promocional.periodos_aplicaveis for valor in p.values()]

            for intervalo in intervalos:
                cin, cout = intervalo.split(' - ')
                i_check_in = datetime.datetime.strptime(cin, '%d/%m/%Y').date()
                i_check_out = datetime.datetime.strptime(cout, '%d/%m/%Y').date()
                check_in_formatado = datetime.datetime.strptime(check_in, '%Y-%m-%d %H:%M').date()
                check_out_formatado = datetime.datetime.strptime(check_out, '%Y-%m-%d %H:%M').date()

                if check_in_formatado >= i_check_in and check_out_formatado <= i_check_out:

                    return True

            return False


        pacotes = Orcamento.objects.filter(promocional=True, data_vencimento__gte=datetime.date.today())
        pacotes_validos = []

        for pacote in pacotes:
            if comparar_intervalo():
                if pacote.pacote_promocional.minimo_de_diarias <= n_dias <= pacote.pacote_promocional.maximo_de_diarias:
                    if id_produto in [p.id for p in pacote.pacote_promocional.produtos_elegiveis.all()]:
                        dados = serializers.serialize('json', [pacote.pacote_promocional, ])
                        campos = json.loads(dados)[0]['fields']

                        pacotes_validos.append({
                            'id': pacote.id,
                            'nome': pacote.pacote_promocional.nome_do_pacote,
                        })

        return pacotes_validos

    def serializar_objetos(self):
        obj = self
        dados = serializers.serialize('json', [obj, ])

        return json.loads(dados)[0]

    def pegar_dados_pacote(self):
        ...


class Tratativas(models.Model):
    cliente = models.ForeignKey(ClienteColegio, on_delete=models.CASCADE, verbose_name='Cliente')
    colaborador = models.ForeignKey(User, on_delete=models.DO_NOTHING, verbose_name='Colaborador')
    id_tratativa = models.CharField(primary_key=True, max_length=255, editable=False)
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

    @staticmethod
    @receiver(pre_delete, sender=User)
    def redifinir_colaborador(sender, instance, **kwargs):
        diretoria = Vendedor.objects.filter(usuario__groups__icontains='diretoria')[0]
        Tratativas.objects.filter(colaborador=instance).update(colaborador=diretoria.usuario)

    def save(self, *args, **kwargs):
        if not self.id_tratativa:
            cnpj = self.cliente.cnpj
            data = datetime.datetime.now().date().strftime('%d%m%Y')
            self.id_tratativa = f'{data}_{re.sub(r"[^a-zA-Z0-9]", "", cnpj)}'

        super().save(*args, **kwargs)

    def pegar_orcamentos(self):
        orcamentos = []

        for orcamento in self.orcamentos.all():
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


class CadastroOrcamento(forms.ModelForm):
    class Meta:
        model = Orcamento
        exclude = ()

        widgets = {
            'promocional': forms.CheckboxInput(
                attrs={'class': 'form-check-input', 'onchange': 'montar_pacote(this)'}),
            'orcamento_promocional': forms.Select(attrs={'disabled': True, 'onchange': 'mostrar_dados_pacote(this)'}),
            'produto': forms.Select(attrs={'disabled': True}),
            'transporte': forms.RadioSelect(),
            'cliente': forms.Select(attrs={'onchange': 'gerar_responsaveis(this)'}),
            'responsavel': forms.Select(attrs={'disabled': True, 'onchange': 'liberar_periodo(this)'}),
            'opcionais': forms.SelectMultiple(attrs={'onchange': 'enviar_op(this)'}),
            'atividades': forms.SelectMultiple(attrs={'onchange': 'enviar_op(this)'}),
            'atividades_ceu': forms.SelectMultiple(attrs={'onchange': 'enviar_op(this)'}),
            'outros': forms.SelectMultiple(attrs={'onchange': 'enviar_op(this)'}),
        }

    def __init__(self, *args, **kwargs):
        super(CadastroOrcamento, self).__init__(*args, **kwargs)
        clientes = ClienteColegio.objects.all()
        responsaveis = Responsavel.objects.all()
        pacotes_promocionais = Orcamento.objects.filter(promocional=True, data_vencimento__gte=datetime.date.today())
        responsaveis_cargo = [('', '')]
        clientes_cnpj = [('', '')]
        orcamentos_promocionais = [('', '')]

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

        for pacote in pacotes_promocionais:
            orcamentos_promocionais.append((pacote.id, pacote.pacote_promocional.nome_do_pacote))

        self.fields['cliente'].choices = clientes_cnpj
        self.fields['responsavel'].choices = responsaveis_cargo
        self.fields['orcamento_promocional'].choices = orcamentos_promocionais
