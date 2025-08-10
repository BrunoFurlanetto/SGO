from collections import defaultdict
from decimal import Decimal
from math import ceil

from django import forms
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.forms import Select

from coreFinanceiro.models import ClassificacoesItens, TiposPagamentos
from orcamento.models import Orcamento, OrcamentoPeriodo
from peraltas.models import ClienteColegio, Responsavel, Vendedor, RelacaoClienteResponsavel


class DadosEvento(models.Model):
    sim_e_nao = (
        (0, 'Não'),
        (1, 'Sim'),
    )

    responsavel_operacional = models.ForeignKey(
        Responsavel,
        on_delete=models.PROTECT,
        verbose_name='Responsável operacional',
        related_name='responsavel_operacional'
    )
    responsavel_financeiro = models.ForeignKey(
        Responsavel,
        verbose_name='Responsável financeiro',
        related_name='responsavel_financeiro',
        on_delete=models.PROTECT,
    )
    pgto_neto = models.IntegerField(choices=sim_e_nao, verbose_name='Pgto neto')
    coordenacao = models.IntegerField(choices=sim_e_nao, default=1, verbose_name='Coordenação')
    monitoria = models.IntegerField(choices=sim_e_nao, verbose_name='Monitoria')
    onibus = models.IntegerField(choices=sim_e_nao, verbose_name='Ônibus')
    colaborador = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Colaborador')
    comissao = models.DecimalField(max_digits=4, decimal_places=2, verbose_name='Comissão', default=0.00, blank=True, null=True)
    check_in = models.DateTimeField(verbose_name='Check in')
    check_out = models.DateTimeField(verbose_name='Check out')
    qtd_reservada = models.PositiveIntegerField(verbose_name='Qtd reservada')
    cortesia_alunos = models.PositiveIntegerField(verbose_name='Cortesia de alunos', default=0)
    cortesia_responsaveis = models.PositiveIntegerField(verbose_name='Cortesia de professores', default=0)
    cortesias_externas = models.JSONField(blank=True, null=True, verbose_name='Cortesias externas', editable=False)

    @classmethod
    def preencher_cortesias_externas(cls, dados):
        cortesias_externas = []
        cortesia = 1

        while True:
            if dados.get(f'cortesias_externas_atividade_{cortesia}', None):
                cortesias_externas.append({
                    'id_atividade': int(dados.get(f'id_atividade_{cortesia}')),
                    'alunos': int(dados.getlist(f'cortesias_externas_atividade_{cortesia}')[0]),
                    'professores': int(dados.getlist(f'cortesias_externas_atividade_{cortesia}')[1]),
                })
            else:
                break

            cortesia += 1

        return cortesias_externas


class DadosPagamento(models.Model):
    # produto = models.DecimalField(decimal_places=2, max_digits=8, verbose_name='Produto') TODO: Veficiar esse campo
    valor_periodo = models.DecimalField(max_digits=8, decimal_places=2, verbose_name='Período')
    descritivo_periodo = models.JSONField(editable=False)
    valor_transporte = models.DecimalField(max_digits=8, decimal_places=2, verbose_name='Transporte')
    descritivo_transporte = models.JSONField(editable=False)
    valor_monitoria = models.DecimalField(max_digits=8, decimal_places=2, verbose_name='Monitoria')
    descritivo_monitoria = models.JSONField(editable=False)
    valor_opcionais = models.DecimalField(max_digits=8, decimal_places=2, verbose_name='Opcionais')
    descritivo_opcionais = models.JSONField(editable=False)
    valor_op_extra = models.DecimalField(max_digits=8, decimal_places=2, verbose_name='Opcionais extra')
    descritivo_extra = models.JSONField(editable=False)

    @classmethod
    def auto_preenchimento(cls, orcamento):
        dados_pagamento = cls.objects.create(
            valor_periodo=Decimal(orcamento.valores_diaria()['valor_final'].replace(',', '.')),
            descritivo_periodo=orcamento.valores_diaria(),
            valor_transporte=Decimal(orcamento.valores_transporte()['valor_final'].replace(',', '.')),
            descritivo_transporte=orcamento.valores_transporte(),
            valor_monitoria=Decimal(orcamento.valores_monitoria()['valor_final'].replace(',', '.')),
            descritivo_monitoria=orcamento.valores_monitoria(),
            valor_opcionais=Decimal(orcamento.valores_opcionais()['valor_final'].replace(',', '.')),
            descritivo_opcionais=orcamento.valores_opcionais(),
            valor_op_extra=Decimal(orcamento.valores_outros()['valor_final'].replace(',', '.')),
            descritivo_extra=orcamento.valores_outros(),
        )

        return dados_pagamento


class PlanosPagamento(models.Model):
    valor_a_vista = models.DecimalField(max_digits=8, decimal_places=2, verbose_name='Valor à vista')
    forma_pagamento = models.ForeignKey(TiposPagamentos, on_delete=models.CASCADE,
                                        verbose_name='Forma de pagamento')
    codigo_eficha = models.CharField(max_length=255, verbose_name='Codigo E-Ficha', blank=True, null=True)
    parcelas = models.IntegerField(verbose_name='Parcelas', default=1)
    inicio_vencimento = models.DateField(verbose_name='Início vencimento')
    final_vencimento = models.DateField(verbose_name='Final vencimento')
    comissoes_externas = models.JSONField(verbose_name='Comissões externas', blank=True, null=True, editable=False)

    def verficar_eficha(self):
        return self.forma_pagamento.eficha

    @classmethod
    def preencher_dados_comissionados(cls, dados):
        comissionados = []
        comissionado = 1

        while True:
            if dados.get(f'comissionado_{comissionado}', None):
                comissionados.append({
                    'nome': dados.getlist(f'comissionado_{comissionado}')[0],
                    'telefone': dados.getlist(f'comissionado_{comissionado}')[1],
                    'email': dados.getlist(f'comissionado_{comissionado}')[2],
                    'comissao': float(dados.getlist(f'comissionado_{comissionado}')[3].replace('%', '').replace(',', '.')),
                })
            else:
                break

            comissionado += 1

        return comissionados


class NotaFiscal(models.Model):
    razao_social = models.CharField(max_length=255, verbose_name='Razao social', blank=True, null=True)
    endereco = models.CharField(max_length=255, verbose_name='Endereço', blank=True, null=True)
    cnpj = models.CharField(max_length=255, verbose_name='CNPJ', blank=True, null=True)

    def __str__(self):
        return f'Dados nota fiscal de {self.razao_social}'


class FichaFinanceira(models.Model):
    orcamento = models.ForeignKey(Orcamento, on_delete=models.CASCADE, verbose_name='Orçamento', null=False)
    cliente = models.ForeignKey(ClienteColegio, on_delete=models.CASCADE, verbose_name='Cliente', null=False)
    enviado_ac = models.ForeignKey(Responsavel, verbose_name='Enviado a/c', on_delete=models.SET_NULL, null=True, blank=True)
    dados_evento = models.ForeignKey(DadosEvento, on_delete=models.CASCADE, verbose_name='Dados do evento')
    dados_pagamento = models.ForeignKey(DadosPagamento, on_delete=models.CASCADE, verbose_name='Dados do pagamento')
    planos_pagamento = models.ForeignKey(
        PlanosPagamento,
        on_delete=models.DO_NOTHING,
        verbose_name='Planos de pagamento',
        blank=True,
        null=True
    )
    nf = models.BooleanField(default=False, verbose_name='NF')
    dados_nota_fiscal = models.ForeignKey(
        NotaFiscal,
        on_delete=models.DO_NOTHING,
        verbose_name='Dados da nota fiscal',
        blank=True,
        null=True
    )
    motivo_recusa = models.TextField(verbose_name='Motivo da recusa', blank=True, null=True)
    negado = models.BooleanField(default=False, verbose_name='Negado')
    comentario_diretoria = models.TextField(verbose_name='Comentário para o financeiro', blank=True, null=True)
    valor_final = models.DecimalField(max_digits=8, decimal_places=2, verbose_name='Valor final')
    observacoes_ficha_financeira = models.TextField(verbose_name='Observações ficha financeira', blank=True)
    descritivo_ficha_financeira = models.JSONField(editable=False)
    autorizado_diretoria = models.BooleanField(default=False, verbose_name='Autorizado pela diretoria')
    faturado = models.BooleanField(default=False, verbose_name='Faturado')
    data_preenchimento_comercial = models.DateTimeField(verbose_name='Data de Preenchimento pelo comercial')
    data_aprovacao_diretoria = models.DateTimeField(verbose_name='Data de aprovacao pela diretoria', blank=True, null=True)
    data_faturamento = models.DateTimeField(verbose_name='Data de Preenchimento de faturamento', blank=True, null=True)

    class Meta:
        permissions = (
            ('pode_aprovar_ficha_financeira', 'Pode aprovar ficha financeira'),
            ('pode_faturar_ficha_financeira', 'Pode faturar ficha financeira'),
        )

    def __str__(self):
        return f'Ficha financeira de {self.cliente}'

    @staticmethod
    def calcular_totais_com_arredondamento(total_por_classificacao):
        totais = {
            'valor': 0.0,
            'valor_final': 0.0,
            'comissao_de_vendas': 0.0,
            'taxa_comercial': 0.0,
            'desconto': 0.0,
            'acrescimo': 0.0,
        }
        soma_valor_final = 0

        for classificacao, valores in total_por_classificacao.items():
            soma_valor_final += valores['valor_final']
            totais['valor'] += valores['valor']
            totais['comissao_de_vendas'] += valores['comissao_de_vendas']
            totais['taxa_comercial'] += valores['taxa_comercial']
            totais['desconto'] += valores['desconto']
            totais['acrescimo'] += valores['acrescimo']

        totais['valor_final'] = ceil(round(soma_valor_final, 5))
        totais['arredondamento'] = round(totais['valor_final'] - soma_valor_final, 2)

        return totais

    def dados_totalizacao(self):
        # codigos_classificaca_db = ClassificacoesItens.objects.all()
        total_por_classificacao = defaultdict(lambda: {
            'valor': 0.0,
            'valor_final': 0.0,
            'comissao_de_vendas': 0.0,
            'taxa_comercial': 0.0,
            'desconto': 0.0,
            'acrescimo': 0.0,
        })

        taxa_periodo = self.orcamento.objeto_orcamento['periodo_viagem']

        if taxa_periodo['codigo_classificacao_item']:
            try:
                ct = ContentType.objects.get(app_label=taxa_periodo['codigo_classificacao_item']["app_id"], model=taxa_periodo['codigo_classificacao_item']["model_id"])
                objeto = ct.get_object_for_this_type(pk=taxa_periodo['codigo_classificacao_item']["object_id"])
                cod = objeto.classificacao
            except ClassificacoesItens.DoesNotExist:
                ...
            else:
                total_por_classificacao[f'{cod.codigo_simplificado} ({cod.codigo_padrao})']['valor'] += taxa_periodo.get('valor', 0.0)
                total_por_classificacao[f'{cod.codigo_simplificado} ({cod.codigo_padrao})']['valor_final'] += taxa_periodo.get('valor_final', 0.0)
                total_por_classificacao[f'{cod.codigo_simplificado} ({cod.codigo_padrao})']['comissao_de_vendas'] += taxa_periodo.get('comissao_de_vendas', 0.0)
                total_por_classificacao[f'{cod.codigo_simplificado} ({cod.codigo_padrao})']['taxa_comercial'] += taxa_periodo.get('taxa_comercial', 0.0)
                total_por_classificacao[f'{cod.codigo_simplificado} ({cod.codigo_padrao})']['desconto'] += taxa_periodo.get('desconto', 0.0)

        # Processa os dados do dicionário principal
        for item in self.orcamento.objeto_orcamento['valores'].values():
            codigo = item['codigo_classificacao_item']

            if not codigo:
                continue

            ct = ContentType.objects.get(app_label=codigo["app_id"], model=codigo["model_id"])
            objeto = ct.get_object_for_this_type(pk=codigo["object_id"])
            cod = objeto.classificacao
            total_por_classificacao[f'{cod.codigo_simplificado} ({cod.codigo_padrao})']['valor'] += item.get('valor', 0.0)
            total_por_classificacao[f'{cod.codigo_simplificado} ({cod.codigo_padrao})']['valor_final'] += item.get('valor_final', 0.0)
            total_por_classificacao[f'{cod.codigo_simplificado} ({cod.codigo_padrao})']['comissao_de_vendas'] += item.get('comissao_de_vendas', 0.0)
            total_por_classificacao[f'{cod.codigo_simplificado} ({cod.codigo_padrao})']['taxa_comercial'] += item.get('taxa_comercial', 0.0)
            total_por_classificacao[f'{cod.codigo_simplificado} ({cod.codigo_padrao})']['desconto'] += item.get('desconto', 0.0)

        # Processa a lista de opcionais
        for item in self.orcamento.objeto_orcamento['descricao_opcionais']:
            codigo = item['codigo_classificacao_item']

            if not codigo['object_id']:
                total_por_classificacao['Sem Classificação']['valor'] += item.get('valor', 0.0)
                total_por_classificacao['Sem Classificação']['valor_final'] += item.get('valor_final', 0.0)
                total_por_classificacao['Sem Classificação']['comissao_de_vendas'] += item.get('comissao_de_vendas', 0.0)
                total_por_classificacao['Sem Classificação']['taxa_comercial'] += item.get('taxa_comercial', 0.0)
                total_por_classificacao['Sem Classificação']['desconto'] += item.get('desconto', 0.0)

                continue

            ct = ContentType.objects.get(app_label=codigo["app_id"], model=codigo["model_id"])
            objeto = ct.get_object_for_this_type(pk=codigo["object_id"])
            cod = objeto.classificacao
            total_por_classificacao[f'{cod.codigo_simplificado} ({cod.codigo_padrao})']['valor'] += item.get('valor', 0.0)
            total_por_classificacao[f'{cod.codigo_simplificado} ({cod.codigo_padrao})']['valor_final'] += item.get('valor_final', 0.0)
            total_por_classificacao[f'{cod.codigo_simplificado} ({cod.codigo_padrao})']['comissao_de_vendas'] += item.get('comissao_de_vendas', 0.0)
            total_por_classificacao[f'{cod.codigo_simplificado} ({cod.codigo_padrao})']['taxa_comercial'] += item.get('taxa_comercial', 0.0)
            total_por_classificacao[f'{cod.codigo_simplificado} ({cod.codigo_padrao})']['desconto'] += item.get('desconto', 0.0)

        codigo_arredondamento = ClassificacoesItens.objects.get(arredondamento=True)
        total_por_classificacao[f'{codigo_arredondamento.codigo_simplificado} ({codigo_arredondamento.codigo_padrao})']['valor'] += self.orcamento.objeto_orcamento['total']['arredondamento']
        total_por_classificacao[f'{codigo_arredondamento.codigo_simplificado} ({codigo_arredondamento.codigo_padrao})']['valor_final'] += self.orcamento.objeto_orcamento['total']['arredondamento']

        totais = self.calcular_totais_com_arredondamento(total_por_classificacao)

        return {'totalizacao': dict(total_por_classificacao), 'totais': totais}


# ------------------------------------------------ Forms ---------------------------------------------------------------
class CadastroDadosEvento(forms.ModelForm):
    class Meta:
        model = DadosEvento
        fields = '__all__'

        widgets = {
            'responsavel_financeiro': forms.Select(attrs={'onchange': 'buscar_dados_financeiro()'}),
            'telefone_financeiro': forms.TextInput(attrs={'onfocus': 'mascara_telefone(this)'}),
            'monitoria': forms.Select(attrs={'class': 'inalteravel'}),
            'onibus': forms.Select(attrs={'class': 'inalteravel'}),
            'colaborador': forms.Select(attrs={'class': 'inalteravel'}),
            'comissao': forms.TextInput(attrs={'class': 'porcentagem', 'onchange': 'setar_comissao()'}),
            'check_in': forms.TextInput(attrs={'type': 'datetime-local', 'readonly': True}),
            'check_out': forms.TextInput(attrs={'type': 'datetime-local', 'readonly': True}),
        }

    def __init__(self, *args, **kwargs):
        super(CadastroDadosEvento, self).__init__(*args, **kwargs)
        vendedoras = Vendedor.objects.all()
        responsaveis = Responsavel.objects.all()
        select_colaborador = [('', '')]
        select_responsavel = [('', '')]

        for vendedora in vendedoras:
            select_colaborador.append((vendedora.usuario.id, vendedora.usuario.get_full_name()))

        for responsavel in responsaveis:
            select_responsavel.append((responsavel.id, f'{responsavel} - {responsavel.fone}'))

        self.fields['colaborador'].choices = select_colaborador
        self.fields['responsavel_operacional'].choices = select_responsavel


class EFichaSelect(Select):
    def create_option(self, name, value, label, selected, index, subindex=None, attrs=None):
        option = super().create_option(name, value, label, selected, index, subindex, attrs)

        if value:
            try:
                tipo_pagamento = TiposPagamentos.objects.get(id=value)
                option['attrs']['data-eficha'] = tipo_pagamento.eficha
            except (ValueError, TiposPagamentos.DoesNotExist):
                pass

        return option


class CadastroPlanosPagamento(forms.ModelForm):
    class Meta:
        model = PlanosPagamento
        fields = '__all__'

        widgets = {
            'valor_a_vista': forms.TextInput(attrs={'class': 'inalteravel'}),
            'codigo_eficha': forms.TextInput(attrs={'onkeyup': 'this.value=this.value.toUpperCase()'}),
            'inicio_vencimento': forms.DateInput(attrs={'type': 'date', 'onchange': 'verificar_vencimentos(this)'}),
            'final_vencimento': forms.DateInput(attrs={'type': 'date', 'onchange': 'verificar_vencimentos(this)'}),
            'parcelas': forms.NumberInput(attrs={'min': '1', 'onchange': 'verificar_vencimentos(this)'}),
        }

    def __init__(self, *args, **kwargs):
        super(CadastroPlanosPagamento, self).__init__(*args, **kwargs)
        valor_a_vista = self.initial.get('valor_a_vista', '')
        valor = str(valor_a_vista).replace('.', ',')
        self.initial['valor_a_vista'] = valor
        tipos_pagamento = TiposPagamentos.objects.all()
        select_tipos_pagamento = [('', '')]

        for tipo_pagamento in tipos_pagamento:
            select_tipos_pagamento.append((tipo_pagamento.id, tipo_pagamento.tipo_pagamento))

        self.fields['forma_pagamento'].widget = EFichaSelect()
        self.fields['forma_pagamento'].widget.attrs.update({'onchange': 'verificar_metodo_pagamento()'})
        self.fields['forma_pagamento'].choices = select_tipos_pagamento



class CadastroNotaFiscal(forms.ModelForm):
    class Meta:
        model = NotaFiscal
        fields = '__all__'


class CadastroFichaFinanceira(forms.ModelForm):
    class Meta:
        model = FichaFinanceira
        fields = '__all__'

        widgets = {
            'nf': forms.CheckboxInput(
                attrs={
                    'class': 'form-check-input',
                    'onchange': '$(".nota_fiscal").toggleClass("none")',
                    'onclick': 'tornar_campos_obrigatorios()'
                }),
            'observacoes_ficha_financeira': forms.Textarea(attrs={'rows': '6'}),
            'observacoes_orcamento': forms.Textarea(attrs={'rows': '6', 'readonly': True}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        responsaveis = Responsavel.objects.all()
        select_responsavel = [('', '')]

        for responsavel in responsaveis:
            select_responsavel.append((responsavel.id, f'{responsavel} - {responsavel.fone}'))

        self.fields['enviado_ac'].choices = select_responsavel

        if self.instance.pk:  # Quando um objeto existente está sendo editado
            # Remover opções inválidas do campo "enviado_ac"
            self.fields['enviado_ac'].queryset = Responsavel.objects.none()
            relacoes = RelacaoClienteResponsavel.objects.filter(cliente_id=self.instance.cliente.id)
            responsaveis = Responsavel.objects.filter(id__in=relacoes.values_list("responsavel", flat=True)).distinct()
            self.fields['enviado_ac'].queryset = responsaveis
