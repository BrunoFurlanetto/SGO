from django import forms
from django.db import models

from peraltas.models import ClienteColegio, Responsavel, EmpresaOnibus


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
    decricao = models.TextField(verbose_name="Descrição", default="")

    def __str__(self):
        return f'Valores transporte periodo {self.periodo.nome_periodo}'


class Orcamento(models.Model):
    sim_e_nao = (
        ('', ''),
        ('sim', 'Sim'),
        ('nao', 'Não')
    )

    cliente = models.ForeignKey(ClienteColegio, on_delete=models.CASCADE, verbose_name='Cliente')
    responsavel = models.ForeignKey(Responsavel, on_delete=models.CASCADE, verbose_name='Responsável')
    periodo_viagem = models.ForeignKey(OrcamentoPeriodo, on_delete=models.CASCADE, verbose_name='Período da viagem')
    n_dias = models.PositiveIntegerField(default=0, verbose_name='Nº de dias')
    hora_check_in = models.ForeignKey(
        HorariosPadroes,
        on_delete=models.CASCADE,
        related_name='horario_entrada',
        verbose_name='Hora do check in'
    )
    hora_check_out = models.ForeignKey(
        HorariosPadroes,
        on_delete=models.CASCADE,
        related_name='horario_saida',
        verbose_name='Hora do check out'
    )
    tipo_monitoria = models.ForeignKey(OrcamentoMonitor, on_delete=models.CASCADE, verbose_name='Tipo de monitoria')
    transporte = models.CharField(max_length=3, default='', choices=sim_e_nao, verbose_name='Transporte')
    opcionais = models.ManyToManyField(
        OrcamentoOpicional,
        blank=True,
        verbose_name='Opcionais',
        related_name='opcionais'
    )
    outros = models.ManyToManyField(OrcamentoOpicional, blank=True, verbose_name='Outros', related_name='outros')
    desconto = models.DecimalField(blank=True, null=True, max_digits=4, decimal_places=2, verbose_name='Desconto')
    observacoes = models.TextField(blank=True, verbose_name='Observações')
    motivo_recusa = models.CharField(max_length=255, verbose_name='Motivo da recusa')
    promocional = models.BooleanField(default=False)
    aprovado = models.BooleanField(default=False)
    necessita_aprovacao_gerencia = models.BooleanField(default=False, verbose_name='Necessita de aprovação da gerência')

    def __str__(self):
        return f'Orçamento de {self.cliente}'


class CadastroOrcamento(forms.ModelForm):
    hora_check_in = forms.ModelChoiceField(
        queryset=HorariosPadroes.objects.all(),
        widget=forms.RadioSelect,
        required=True
    )
    hora_check_in.widget.attrs['class'] = 'form-check-input'

    hora_check_out = forms.ModelChoiceField(
        queryset=HorariosPadroes.objects.all(),
        widget=forms.RadioSelect,
        required=True
    )
    hora_check_out.widget.attrs['class'] = 'form-check-input'

    class Meta:
        model = Orcamento
        exclude = ()

        widgets = {
            'cliente': forms.Select(attrs={'onchange': 'gerar_responsaveis(this)'}),
            'responsavel': forms.Select(attrs={'disabled': True, 'onchange': 'liberar_periodo(this)'}),
            'opcionais': forms.SelectMultiple(attrs={'onchange': 'enviar_op(this)'}),
            'outros': forms.SelectMultiple(attrs={'onchange': 'enviar_op(this)'}),
        }

    def __init__(self, *args, **kwargs):
        super(CadastroOrcamento, self).__init__(*args, **kwargs)
        clientes = ClienteColegio.objects.all()
        responsaveis = Responsavel.objects.all()
        horarios = HorariosPadroes.objects.all()
        opcionais = OrcamentoOpicional.objects.all()
        responsaveis_cargo = [('', '')]
        clientes_cnpj = [('', '')]
        horario_refeicao = []
        opcionais_fixo = []
        outros = []

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

        for horario in horarios:
            horario_refeicao.append((horario.id, f'{horario.refeicao} ({horario.horario.strftime("%H:%M")})'))

        for opcional in opcionais:
            if opcional.fixo:
                opcionais_fixo.append((opcional.id, opcional.nome))
            else:
                outros.append((opcional.id, opcional.nome))

        self.fields['cliente'].choices = clientes_cnpj
        self.fields['responsavel'].choices = responsaveis_cargo
        self.fields['hora_check_in'].choices = horario_refeicao
        self.fields['hora_check_out'].choices = horario_refeicao
        self.fields['outros'].choices = outros
        self.fields['opcionais'].choices = opcionais_fixo
