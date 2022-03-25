import datetime

from django import forms
from django.db import models

from ceu.models import Atividades


class Monitor(models.Model):
    nome = models.CharField(max_length=255)

    def __str__(self):
        return self.nome


class AtividadePeraltas(models.Model):
    ...


class Vendedor(models.Model):
    nome_vendedor = models.CharField(max_length=255)

    def __str__(self):
        return self.nome_vendedor


class AtividadesEco(models.Model):
    atividade = models.CharField(max_length=255)

    def __str__(self):
        return self.atividade


class ProdutosPeraltas(models.Model):
    produto = models.CharField(max_length=255)

    def __str__(self):
        return self.produto


class PerfilsParticipantes(models.Model):
    fase = models.CharField(max_length=255)
    ano = models.CharField(max_length=255, blank=True)
    idade = models.CharField(max_length=255)

    def __str__(self):

        if self.ano != '':
            return f'{self.ano}({self.idade})'
        else:
            return f'{self.fase}({self.idade})'


class ResumoFinanceiro(models.Model):
    tipo_contrato = (
        (1, 'Grupo'),
        (2, 'Individual')
    )

    valor = models.FloatField(blank=True, null=True)
    valor_por_participantes = models.FloatField(blank=True, null=True)
    forma_pagamento = models.CharField(max_length=255, blank=True)
    vencimentos = models.CharField(max_length=255, blank=True)
    contrato = models.IntegerField(choices=tipo_contrato)
    nota_fiscal = models.BooleanField()
    observacoes_financeiras = models.TextField(blank=True)


class CodigosApp(models.Model):
    cliente_pj = models.CharField(max_length=20, blank=True)
    cliente_pf = models.CharField(max_length=20, blank=True)
    evento = models.CharField(max_length=20, blank=True)
    reserva = models.CharField(max_length=20, blank=True)


class InformacoesAdcionais(models.Model):
    servicos_de_bordo = (
        (1, 'Padrão'),
        (2, 'Diferenciado')
    )

    tipos_monitoria = (
        (1, '1/2 monitoria (fora de quarto - 1/20)'),
        (2, '1/2 monitoria (dentro de quarto - 1/20'),
        (3, 'Monitoria completa (em quarto - 1/10)')
    )

    tipos_enfermaria = (
        (1, 'Padrão'),
        (2, 'Garantia')
    )

    transporte = models.BooleanField()
    endereco_embarque = models.CharField(max_length=255, blank=True)
    etiquetas_embarque = models.BooleanField()
    servico_bordo = models.IntegerField(choices=servicos_de_bordo, blank=True, null=True)
    monitoria = models.IntegerField(choices=tipos_monitoria, blank=True, null=True)
    biologo = models.BooleanField()
    quais_atividades = models.CharField(max_length=255, blank=True)
    seguro = models.BooleanField()
    exclusividade = models.BooleanField()
    fotos_site = models.BooleanField()
    abada = models.BooleanField()
    camiseta = models.BooleanField()
    festas = models.BooleanField()
    enfermaria = models.IntegerField(choices=tipos_enfermaria, blank=True, null=True)
    horario_garantia = models.TimeField(blank=True, null=True)
    roupa_de_cama = models.BooleanField()
    camera_on_line = models.BooleanField()
    cd_para_aluno = models.BooleanField()
    bate_bate = models.BooleanField()
    fogueira = models.BooleanField()
    atividades_ceu = models.ManyToManyField(Atividades, blank=True)
    atividades_eco = models.ManyToManyField(AtividadesEco, blank=True)
    outros = models.CharField(max_length=300, blank=True)


class ClienteColegio(models.Model):
    razao_social = models.CharField(max_length=255)
    cnpj = models.CharField(max_length=14, unique=True)
    nome_fantasia = models.CharField(max_length=255)
    endereco = models.CharField(max_length=600)
    bairro = models.CharField(max_length=255)
    cidade = models.CharField(max_length=255)
    estado = models.CharField(max_length=255)
    cep = models.CharField(max_length=8)
    responsavel_evento = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.nome_fantasia


class Responsavel(models.Model):
    responsavel_por = models.ForeignKey(ClienteColegio, on_delete=models.DO_NOTHING)
    nome = models.CharField(max_length=255)
    cargo = models.CharField(max_length=255)
    fone = models.IntegerField()
    email_responsavel_evento = models.EmailField()

    def __str__(self):
        return self.nome


class FichaDeEvento(models.Model):
    cliente = models.ForeignKey(ClienteColegio, on_delete=models.DO_NOTHING)
    responsavel_evento = models.ForeignKey(Responsavel, on_delete=models.DO_NOTHING)
    produto = models.ManyToManyField(ProdutosPeraltas)
    outro_produto = models.CharField(max_length=255, blank=True, null=True)
    check_in = models.DateTimeField()
    check_out = models.DateTimeField()
    professores_com_alunos = models.BooleanField()
    qtd_professores = models.IntegerField(blank=True, null=True)
    qtd_convidada = models.PositiveIntegerField(blank=True, null=True)
    qtd_confirmada = models.PositiveIntegerField(blank=True, null=True)
    perfil_participantes = models.ManyToManyField(PerfilsParticipantes)
    refeicoes = models.JSONField(blank=True, null=True)
    informacoes_adcionais = models.ForeignKey(InformacoesAdcionais, on_delete=models.CASCADE)
    observacoes = models.TextField(blank=True)
    vendedora = models.ForeignKey(Vendedor, on_delete=models.DO_NOTHING)
    data_preenchimento = models.DateField(default=datetime.datetime.now, blank=True, null=True)
    resumo_financeiro = models.ForeignKey(ResumoFinanceiro, on_delete=models.CASCADE)
    codigos_app = models.ForeignKey(CodigosApp, on_delete=models.DO_NOTHING, blank=True, null=True)
    os = models.BooleanField(default=False)


# ------------------------------------------------ Formulários ---------------------------------------------------------
class CadastroFichaDeEvento(forms.ModelForm):
    perfil_participantes = forms.ModelMultipleChoiceField(
        queryset=PerfilsParticipantes.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=True
    )
    perfil_participantes.widget.attrs['class'] = 'form-check-input'

    produto = forms.ModelMultipleChoiceField(
        queryset=ProdutosPeraltas.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=True
    )
    produto.widget.attrs['class'] = 'form-check-input'

    class Meta:
        model = FichaDeEvento
        exclude = ()

        widgets = {
            'cliente': forms.TextInput(attrs={'readolny': 'readonly'}),
            'responsavel_evento': forms.TextInput(attrs={'readolny': 'readonly'}),
            'check_in': forms.TextInput(attrs={'type': 'datetime-local', 'onchange': 'pegarDias()'}),
            'check_out': forms.TextInput(attrs={'type': 'datetime-local', 'onchange': 'pegarDias()'}),
            'professores_com_alunos': forms.TextInput(attrs={'type': 'checkbox',
                                                             'class': 'form-check-input'}),
        }


class CadastroCliente(forms.ModelForm):
    class Meta:
        model = ClienteColegio
        exclude = ()

        widgets = {
            'cnpj': forms.NumberInput()
        }


class CadastroResponsavel(forms.ModelForm):
    class Meta:
        model = Responsavel
        exclude = ()

        widgets = {
            'fone': forms.NumberInput(),
        }


class CadastroInfoAdicionais(forms.ModelForm):
    atividades_ceu = forms.ModelMultipleChoiceField(
        queryset=Atividades.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
    )

    atividades_eco = forms.ModelMultipleChoiceField(
        queryset=AtividadesEco.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False
    )

    class Meta:
        model = InformacoesAdcionais
        exclude = ()

        widgets = {
            'transporte': forms.CheckboxInput(attrs={'onchange': 'pegarEndereco()'}),
            'etiquetas_embarque': forms.CheckboxInput(attrs={'onchange': 'servicoBordo()'}),
            'biologo': forms.CheckboxInput(attrs={'onchange': 'quaisAtividades()'}),
            'enfermaria': forms.Select(attrs={'onchange': 'horario(this)'}),
            'horario_garantia': forms.TextInput(attrs={'type': 'time'}),
        }


class CadastroCodigoApp(forms.ModelForm):
    class Meta:
        model = CodigosApp
        exclude = ()


class CadastroResumoFinanceiro(forms.ModelForm):
    class Meta:
        model = ResumoFinanceiro
        exclude = ()
