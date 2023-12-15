import datetime

from django import forms
from django.contrib.auth.models import User
from django.db import models
from django.db.models import PositiveIntegerField

from ceu.models import Atividades
from peraltas.models import ClienteColegio, Responsavel, EmpresaOnibus, Vendedor, ProdutosPeraltas, AtividadesEco


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
    nome_periodo = models.CharField(max_length=255)
    valor = models.DecimalField(decimal_places=2, max_digits=5, default=0.00)
    descricao = models.TextField(blank=True)
    id = models.CharField(max_length=11, unique=True, primary_key=True)

    def __str__(self):
        return self.nome_periodo


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
                    dado_float = float(value.replace(',', '.'))
                except ValueError:
                    dados_tratados[campo] = value
                else:
                    dados_tratados[campo] = dado_float
            else:
                dados_tratados[campo] = dado_int
        lista = [int(i) for i in dados.getlist('produtos_elegiveis[]')]

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
    check_in = models.DateTimeField(verbose_name='Check in')
    check_out = models.DateTimeField(verbose_name='Check out')
    produto = models.ForeignKey(ProdutosPeraltas, on_delete=models.CASCADE, verbose_name='Produto Peraltas')
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
                attrs={'class': 'form-check-input', 'onchange': 'mostrar_dados_pacote(this)'}),
            'nome_promocional': forms.TextInput(attrs={'onkeyup': 'liberar_periodo()'}),
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
