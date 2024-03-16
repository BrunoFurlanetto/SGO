from decimal import Decimal

from django import forms
from django.contrib.auth.models import User
from django.db import models

from orcamento.models import Orcamento
from peraltas.models import ClienteColegio, Responsavel, Vendedor, TiposPagamentos


class DadosEvento(models.Model):
    sim_e_nao = (
        (0, 'Não'),
        (1, 'Sim'),
    )

    responsavel_operacional = models.ForeignKey(
        Responsavel,
        on_delete=models.DO_NOTHING,
        verbose_name='Responsável operacional',
        blank=True,
        null=True
    )
    responsavel_financeiro = models.CharField(max_length=250, verbose_name='Responsável financeiro', blank=True,
                                              null=True)
    telefone_financeiro = models.CharField(max_length=250, verbose_name='Telefone financeiro')
    email_financeiro = models.CharField(max_length=250, verbose_name='E-mail financeiro', blank=True, null=True)
    pgto_neto = models.IntegerField(choices=sim_e_nao, verbose_name='Pgto neto')
    coordenacao = models.IntegerField(choices=sim_e_nao, default=1, verbose_name='Coordenação')
    monitoria = models.IntegerField(choices=sim_e_nao, verbose_name='Monitoria')
    onibus = models.IntegerField(choices=sim_e_nao, verbose_name='Ônibus')
    seguro = models.IntegerField(choices=sim_e_nao, verbose_name='Seguro')
    colaborador = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Colaborador')
    comissao = models.DecimalField(max_digits=4, decimal_places=2, verbose_name='Comissão', default=0.00, blank=True, null=True)
    check_in = models.DateTimeField(verbose_name='Check in')
    check_out = models.DateTimeField(verbose_name='Check out')
    qtd_reservada = models.PositiveIntegerField(verbose_name='Qtd reservada')
    alunos_confirmados = models.PositiveIntegerField(verbose_name='Alunos confirmados', default=0)
    professores_confirmados = models.PositiveIntegerField(verbose_name='Professores confirmados', default=0)
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
    valor_atividades_ceu = models.DecimalField(max_digits=8, decimal_places=2, verbose_name='Atividades CEU')
    descritivo_atividades_ceu = models.JSONField(editable=False)
    valor_atividades_peraltas = models.DecimalField(max_digits=8, decimal_places=2, verbose_name='Atividades Peraltas')
    descritivo_atividades_peraltas = models.JSONField(editable=False)
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
            valor_atividades_ceu=Decimal(orcamento.valores_ceu()['valor_final'].replace(',', '.')),
            descritivo_atividades_ceu=orcamento.valores_ceu(),
            valor_atividades_peraltas=Decimal(orcamento.valores_peraltas()['valor_final'].replace(',', '.')),
            descritivo_atividades_peraltas=orcamento.valores_peraltas(),
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
        return 'ficha' in self.forma_pagamento.tipo_pagamento

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
    enviado_ac = models.CharField(max_length=255, verbose_name='Enviado a/c', blank=True, null=True)
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
    observacoes_orcamento = models.TextField(verbose_name='Observações orcamento', blank=True)
    observacoes_ficha_financeira = models.TextField(verbose_name='Observações ficha financeira', blank=True)
    descritivo_ficha_financeira = models.JSONField(editable=False)
    autorizado_diretoria = models.BooleanField(default=False, verbose_name='Autorizado pela diretoria')
    faturado = models.BooleanField(default=False, verbose_name='Faturado')

    def __str__(self):
        return f'Ficha financeira de {self.cliente}'


# ------------------------------------------------ Forms ---------------------------------------------------------------
class CadastroDadosEvento(forms.ModelForm):
    class Meta:
        model = DadosEvento
        fields = '__all__'

        widgets = {
            'responsavel_operacional': forms.Select(attrs={'class': 'inalteravel'}),
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


class CadastroPlanosPagamento(forms.ModelForm):
    class Meta:
        model = PlanosPagamento
        fields = '__all__'

        widgets = {
            'valor_a_vista': forms.TextInput(attrs={'class': 'inalteravel'}),
            'forma_pagamento': forms.Select(attrs={'onchange': 'verificar_metodo_pagamento()'}),
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
