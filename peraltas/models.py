import datetime

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.postgres.fields import JSONField
from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone

from ceu.models import Atividades, Locaveis


class NivelMonitoria(models.Model):
    nivel = models.CharField(max_length=100)

    def __str__(self):
        return self.nivel


class Monitor(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE)
    telefone = models.CharField(max_length=11)
    cidade_horigem = models.CharField(max_length=255, verbose_name='Moradia', blank=True)
    nivel = models.ForeignKey(NivelMonitoria, on_delete=models.DO_NOTHING, default=1)
    biologo = models.BooleanField(default=False)
    tecnica = models.BooleanField(default=False)
    som = models.BooleanField(default=False)
    video = models.BooleanField(default=False)
    fotos_e_filmagens = models.BooleanField(default=False)
    nota = models.FloatField(default=0.00)
    n_avaliacoes = models.IntegerField(default=0)

    def __str__(self):
        return self.usuario.get_full_name()

    def nome_completo(self):
        return self.usuario.get_full_name()


class Enfermeira(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE)
    telefone = models.CharField(max_length=11)
    pode_pernoitar = models.BooleanField(default=False)

    def __str__(self):
        return self.usuario.get_full_name()


class TipoAtividade(models.Model):
    tipo_atividade = models.CharField(max_length=255)

    def __str__(self):
        return self.tipo_atividade


class GrupoAtividade(models.Model):
    grupo = models.CharField(max_length=100)

    def __str__(self):
        return self.grupo


class AtividadePeraltas(models.Model):
    nome_atividade = models.CharField(max_length=255, verbose_name='Nome da atividade')
    local = models.CharField(max_length=255)
    grupo = models.ForeignKey(GrupoAtividade, on_delete=models.CASCADE, null=True)
    idade_min = models.PositiveIntegerField(verbose_name='Idade mínima')
    idade_max = models.PositiveIntegerField(verbose_name='Idade máxima')
    participantes_min = models.PositiveIntegerField(verbose_name='Número mínimo de participantes')
    participantes_max = models.PositiveIntegerField(verbose_name='Número máximo de participantes')
    monitores_min = models.PositiveIntegerField(verbose_name='Número mínimo de monitores')
    monitores_max = models.PositiveIntegerField(verbose_name='Número máximo de monitores')
    duracao = models.DurationField(blank=True, null=True)
    lista_materiais = models.CharField(max_length=255, verbose_name='Lista de materiais')
    tipo_atividade = models.ManyToManyField(TipoAtividade, verbose_name='Tipo da atividade')
    nivel_atividade = models.ForeignKey(NivelMonitoria, on_delete=models.DO_NOTHING, verbose_name='Nível da atividade')
    manual_atividade = models.FileField(blank=True, upload_to='manuais_atividades_acampamento/%Y/%m/%d',
                                        verbose_name='Manual')

    def __str__(self):
        return self.nome_atividade


class Vendedor(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE, blank=True, null=True)
    telefone = models.CharField(max_length=11)
    nota = models.FloatField(default=0.00)
    n_avaliacoes = models.IntegerField(default=0)

    def __str__(self):
        return self.usuario.get_full_name()

    def nome_completo(self):
        return self.usuario.get_full_name()


class AtividadesEco(models.Model):
    nome_atividade_eco = models.CharField(max_length=255, verbose_name='Nome da atividade')
    local = models.CharField(max_length=255)
    idade_min = models.PositiveIntegerField(verbose_name='Idade mínima')
    idade_max = models.PositiveIntegerField(verbose_name='Idade máxima')
    participantes_min = models.PositiveIntegerField(verbose_name='Número mínimo de participantes')
    participantes_max = models.PositiveIntegerField(verbose_name='Número máximo de participantes')
    monitores_min = models.PositiveIntegerField(verbose_name='Número mínimo de monitores')
    monitores_max = models.PositiveIntegerField(verbose_name='Número máximo de monitores')
    duracao = models.DurationField(blank=True, null=True)
    lista_materiais = models.CharField(max_length=255, verbose_name='Lista de materiais')
    biologo = models.BooleanField(default=False)
    manual_atividade = models.FileField(blank=True, upload_to='manuais_atividades_eco/%Y/%m/%d', verbose_name='Manual')

    def __str__(self):
        return self.nome_atividade_eco


class ProdutosPeraltas(models.Model):
    produto = models.CharField(max_length=255)
    pernoite = models.BooleanField(default=True)
    colegio = models.BooleanField(default=True)
    hora_padrao_check_in = models.TimeField(blank=True, null=True)
    hora_padrao_check_out = models.TimeField(blank=True, null=True)

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


class CodigosApp(models.Model):
    cliente_pj = models.IntegerField()
    cliente_pf = models.IntegerField()
    evento = models.CharField(max_length=255)
    reserva = models.CharField(max_length=255)
    pagamento = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return f'Cliente PJ: {self.cliente_pj}, cliente PF: {self.cliente_pf}'


class ClienteColegio(models.Model):
    razao_social = models.CharField(max_length=255)
    cnpj = models.CharField(max_length=18, unique=True)
    nome_fantasia = models.CharField(max_length=255)
    nickname = models.CharField(max_length=255, blank=True, null=True)
    codigo_app_pj = models.IntegerField(unique=True, blank=True, null=True)
    codigo_app_pf = models.IntegerField(unique=True, blank=True, null=True)
    endereco = models.CharField(max_length=600)
    bairro = models.CharField(max_length=255)
    cidade = models.CharField(max_length=255)
    estado = models.CharField(max_length=255)
    cep = models.CharField(max_length=10)
    responsavel_alteracao = models.ForeignKey(User, on_delete=models.DO_NOTHING, blank=True, null=True)

    def __str__(self):
        return self.nome_fantasia


class ListaDeCargos(models.Model):
    cargo = models.CharField(max_length=255)

    def __str__(self):
        return self.cargo


class Responsavel(models.Model):
    nome = models.CharField(max_length=255)
    cargo = models.ManyToManyField(ListaDeCargos)
    fone = models.CharField(max_length=16)
    email_responsavel_evento = models.EmailField()

    def __str__(self):
        return self.nome


class EmpresaOnibus(models.Model):
    viacao = models.CharField(max_length=255)
    cnpj = models.CharField(max_length=18, unique=True)
    endereco = models.CharField(max_length=255)
    bairro = models.CharField(max_length=255)
    cidade = models.CharField(max_length=255)
    estado = models.CharField(max_length=255)
    cep = models.CharField(max_length=10)

    def __str__(self):
        return self.viacao


class DadosTransporte(models.Model):
    sim_nao = (
        ('', ''),
        (0, 'Não'),
        (1, 'Sim'),
    )

    transporte_fechado_internamente = models.IntegerField(choices=sim_nao, default='', blank=True, null=True)
    empresa_onibus = models.ForeignKey(EmpresaOnibus, on_delete=models.CASCADE, blank=True, null=True)
    endereco_embarque = models.CharField(max_length=255, blank=True, null=True)
    horario_embarque = models.TimeField(blank=True, null=True)
    dados_veiculos = models.JSONField(blank=True, null=True)  # {'qtd_veiculo': int, 'tipo_veiculo': str}

    def valor_veiculos(self):
        return [
            {'veiculo': 'micro', 'n': self.dados_veiculos['micro_onibus']},
            {'veiculo': '46', 'n': self.dados_veiculos['onibus_46']},
            {'veiculo': '50', 'n': self.dados_veiculos['onibus_50']}
        ]


class OpcionaisGerais(models.Model):
    opcional_geral = models.CharField(max_length=100)

    def __str__(self):
        return self.opcional_geral


class OpcionaisFormatura(models.Model):
    opcional_formatura = models.CharField(max_length=100)

    def __str__(self):
        return self.opcional_formatura


class InformacoesAdcionais(models.Model):
    tipos_monitoria = (
        (1, '1/2 monitoria (fora de quarto - 1/20)'),
        (2, '1/2 monitoria (dentro de quarto - 1/20'),
        (3, 'Monitoria completa (em quarto - 1/12)')
    )

    tipos_enfermaria = (
        (2, '8h às 22h'),
        (3, '8h às 8h (24h)'),
        (1, 'Sem enfermeira')
    )

    sim_nao = (
        ('', ''),
        (0, 'Não'),
        (1, 'Sim')
    )

    transporte = models.BooleanField()
    informacoes_transporte = models.ForeignKey(DadosTransporte, null=True, blank=True, on_delete=models.CASCADE)
    seguro = models.BooleanField()
    lista_segurados = models.FileField(blank=True, upload_to='seguros/%Y/%m/%d')
    monitoria = models.IntegerField(choices=tipos_monitoria, blank=True, null=True)
    biologo = models.BooleanField()
    quais_atividades = models.ManyToManyField(AtividadesEco, blank=True)
    enfermaria = models.IntegerField(choices=tipos_enfermaria, default=1)
    cantina = models.IntegerField(choices=sim_nao, default='')
    roupa_de_cama = models.IntegerField(choices=sim_nao, default='')
    opcionais_geral = models.ManyToManyField(OpcionaisGerais, blank=True)
    opcionais_formatura = models.ManyToManyField(OpcionaisFormatura, blank=True)

    def __str__(self):
        return f'Informações adicionais id: {self.id}'


class RelacaoClienteResponsavel(models.Model):
    cliente = models.ForeignKey(ClienteColegio, on_delete=models.CASCADE)
    responsavel = models.ManyToManyField(Responsavel)


class FichaDeEvento(models.Model):
    empresa_choices = (
        ('Peraltas', 'Peraltas'),
        ('CEU', 'Fundação CEU'),
        ('Peraltas CEU', 'Peraltas + Fundação CEU')
    )

    cliente = models.ForeignKey(ClienteColegio, on_delete=models.CASCADE)
    responsavel_evento = models.ForeignKey(Responsavel, on_delete=models.CASCADE)
    produto = models.ForeignKey(ProdutosPeraltas, on_delete=models.DO_NOTHING)
    outro_produto = models.CharField(max_length=255, blank=True, null=True)
    check_in = models.DateTimeField()
    check_out = models.DateTimeField()
    professores_com_alunos = models.BooleanField(default=False)
    qtd_professores = models.PositiveIntegerField(blank=True, null=True)
    qtd_profs_homens = models.PositiveIntegerField(blank=True, null=True)
    qtd_profs_mulheres = models.PositiveIntegerField(blank=True, null=True)
    qtd_convidada = models.PositiveIntegerField(blank=True, null=True)
    qtd_confirmada = models.PositiveIntegerField(blank=True, null=True)
    qtd_meninos = models.PositiveIntegerField(blank=True, null=True)
    qtd_meninas = models.PositiveIntegerField(blank=True, null=True)
    qtd_homens = models.PositiveIntegerField(blank=True, null=True)
    qtd_mulheres = models.PositiveIntegerField(blank=True, null=True)
    perfil_participantes = models.ManyToManyField(PerfilsParticipantes, blank=True)
    refeicoes = models.JSONField(blank=True, null=True)
    observacoes_refeicoes = models.TextField(blank=True, null=True)
    informacoes_adcionais = models.ForeignKey(InformacoesAdcionais, on_delete=models.CASCADE, blank=True, null=True)
    observacoes = models.TextField(blank=True)
    atividades_ceu = models.ManyToManyField(Atividades, blank=True)
    locacoes_ceu = models.ManyToManyField(Locaveis, blank=True)
    atividades_eco = models.ManyToManyField(AtividadesEco, blank=True)
    atividades_peraltas = models.ManyToManyField(GrupoAtividade, blank=True)
    vendedora = models.ForeignKey(Vendedor, on_delete=models.DO_NOTHING, blank=True, null=True)  # TODO: Verificar caso de exclusão de colaborador
    data_final_inscricao = models.DateField(blank=True, null=True)
    empresa = models.CharField(choices=empresa_choices, max_length=100, blank=True, null=True)
    material_apoio = models.FileField(blank=True, null=True, upload_to='materiais_apoio/%Y/%m/%d')
    data_preenchimento = models.DateField(blank=True, null=True)
    codigos_app = models.ForeignKey(CodigosApp, on_delete=models.DO_NOTHING, blank=True, null=True)
    pre_reserva = models.BooleanField(default=False)
    agendado = models.BooleanField(default=False)
    os = models.BooleanField(default=False)
    escala = models.BooleanField(default=False)
    ficha_financeira = models.BooleanField(default=False)

    def __str__(self):
        return f'Ficha de evento de {self.cliente}'

    def nickname_cliente(self):
        return self.cliente.nickname if self.cliente.nickname else self.cliente.nome_fantasia

    def tabelar_refeicoes(self):
        dados = []

        for dia in self.refeicoes:
            dados_refeicoes = []

            dados_refeicoes = [
                'Café' in self.refeicoes[dia],
                'Coffee manhã' in self.refeicoes[dia],
                'Almoço' in self.refeicoes[dia],
                'Lanche tarde' in self.refeicoes[dia],
                'Coffee tarde' in self.refeicoes[dia],
                'Jantar' in self.refeicoes[dia],
                'Lanche noite' in self.refeicoes[dia],
            ]

            dados.append({'dia': dia, 'refeicoes': dados_refeicoes})

        return dados


class DisponibilidadeAcampamento(models.Model):
    meses = (
        (1, 'Janeiro'),
        (2, 'Fevereiro'),
        (3, 'Março'),
        (4, 'Abril'),
        (5, 'Maio'),
        (6, 'Junho'),
        (7, 'Julho'),
        (8, 'Agosto'),
        (9, 'Setembro'),
        (10, 'Outubro'),
        (11, 'Novembro'),
        (12, 'Dezembro'),
    )

    monitor = models.ForeignKey(Monitor, on_delete=models.CASCADE)
    dias_disponiveis = models.TextField(max_length=500)
    mes = models.IntegerField(choices=meses)
    ano = models.CharField(max_length=20)
    n_dias = models.IntegerField()


class DisponibilidadeHotelaria(models.Model):
    meses = (
        (1, 'Janeiro'),
        (2, 'Fevereiro'),
        (3, 'Março'),
        (4, 'Abril'),
        (5, 'Maio'),
        (6, 'Junho'),
        (7, 'Julho'),
        (8, 'Agosto'),
        (9, 'Setembro'),
        (10, 'Outubro'),
        (11, 'Novembro'),
        (12, 'Dezembro'),
    )

    monitor = models.ForeignKey(Monitor, on_delete=models.CASCADE)
    dias_disponiveis = models.TextField(max_length=500)
    mes = models.IntegerField(choices=meses)
    ano = models.CharField(max_length=20)
    n_dias = models.IntegerField()


class DiaLimiteAcampamento(models.Model):
    dia_limite_acampamento = models.PositiveIntegerField()


class EscalaAcampamento(models.Model):
    escolha_setor = (
        ('ceu', 'CEU'),
        ('peraltas', 'Peraltas'),
    )

    cliente = models.ForeignKey(ClienteColegio, on_delete=models.CASCADE)
    ficha_de_evento = models.ForeignKey(FichaDeEvento, on_delete=models.CASCADE, null=True)
    monitores_acampamento = models.ManyToManyField(Monitor, related_name='monitores_acampamento')
    monitores_embarque = models.ManyToManyField(Monitor, blank=True, related_name='monitores_embarque')
    enfermeiras = models.ManyToManyField(Enfermeira, blank=True, related_name='enfermeiras')
    check_in_cliente = models.DateTimeField(default=datetime.timezone)
    check_out_cliente = models.DateTimeField(default=datetime.timezone)
    setor = models.CharField(max_length=8, choices=escolha_setor)


class DiaLimiteHotelaria(models.Model):
    dia_limite_hotelaria = models.PositiveIntegerField()


class EscalaHotelaria(models.Model):
    monitores_hotelaria = models.JSONField(null=True)
    monitores_escalados = models.ManyToManyField(Monitor)
    data = models.DateField()

    def separar_monitores(self):
        monitores = []

        for id_monitor in self.monitores_hotelaria.values():
            monitor = Monitor.objects.get(id=id_monitor)

            monitores.append({'nome': monitor.usuario.get_full_name(), 'user': monitor.usuario})

        return monitores


# ------------------------------------------------ Formulários ---------------------------------------------------------
class CadastroFichaDeEvento(forms.ModelForm):
    perfil_participantes = forms.ModelMultipleChoiceField(
        queryset=PerfilsParticipantes.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False
    )
    perfil_participantes.widget.attrs['class'] = 'form-check-input'

    produto = forms.ModelChoiceField(
        queryset=ProdutosPeraltas.objects.all(),
        widget=forms.RadioSelect,
        required=True
    )
    produto.widget.attrs['class'] = 'form-check-input'
    produto.widget.attrs['onclick'] = 'verQuantidades(this)'

    class Meta:
        model = FichaDeEvento
        exclude = ()

        widgets = {
            'check_in': forms.TextInput(attrs={
                'type': 'datetime-local',
                'onChange': 'pegarDias()',
                'onkeyup': '$("#id_check_in").val("")',
                'onclick': 'this.showPicker()'
            }),
            'check_out': forms.TextInput(attrs={
                'type': 'datetime-local',
                'onChange': 'pegarDias()',
                'onkeyup': '$("#id_check_out").val("")',
                'onclick': 'this.showPicker()'
            }),
            'data_final_inscricao': forms.TextInput(attrs={'type': 'date', 'readonly': 'readonly'}),
            'professores_com_alunos': forms.TextInput(attrs={'type': 'checkbox',
                                                             'class': 'form-check-input'}),
        }


class CadastroCliente(forms.ModelForm):
    class Meta:
        model = ClienteColegio
        exclude = ()

        widgets = {
            'codigo_app_pj': forms.TextInput(attrs={
                'pattern': '\d*', 'minlength': '6', 'maxlength': '6',
                'onload': 'if (this.value != "") this.prop("readonly", false)',
            }),
            'codigo_app_pf': forms.TextInput(attrs={'pattern': '\d*', 'minlength': '6', 'maxlength': '6'}),
        }

    def __init__(self, *args, **kwargs):
        super(CadastroCliente, self).__init__(*args, **kwargs)
        self.fields['codigo_app_pj'].widget.attrs['readonly'] = True
        self.fields['codigo_app_pf'].widget.attrs['readonly'] = True


class CadastroResponsavel(forms.ModelForm):
    class Meta:
        model = Responsavel
        exclude = ()


class CadastroDadosTransporte(forms.ModelForm):
    class Meta:
        model = DadosTransporte
        exclude = ()

        widgets = {
            'transporte_fechado_internamente': forms.Select(attrs={'style': 'width: 100px'}),
            'horario_embarque': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
        }


class CadastroInfoAdicionais(forms.ModelForm):
    class Meta:
        model = InformacoesAdcionais
        exclude = ()

        widgets = {
            'transporte': forms.CheckboxInput(attrs={'onchange': 'pegarEndereco()'}),
            'etiquetas_embarque': forms.CheckboxInput(attrs={'onchange': 'servicoBordo()'}),
            'biologo': forms.CheckboxInput(attrs={'onchange': 'quaisAtividades()'}),
        }


class CadastroCodigoApp(forms.ModelForm):
    class Meta:
        model = CodigosApp
        exclude = ()

        widgets = {
            'cliente_pj': forms.TextInput(attrs={'pattern': '\d*', 'minlength': '6', 'maxlength': '6'}),
            'cliente_pf': forms.TextInput(attrs={'pattern': '\d*', 'minlength': '6', 'maxlength': '6'}),
            'evento': forms.TextInput(),
            'reserva': forms.TextInput(attrs={'pattern': '\d*', 'minlength': '6', 'maxlength': '6'}),
        }


class CadastroPreReserva(forms.ModelForm):
    class Meta:
        model = FichaDeEvento
        fields = [
            'cliente', 'responsavel_evento', 'produto', 'check_in',
            'check_out', 'qtd_convidada', 'observacoes',
            'vendedora', 'pre_reserva', 'agendado'
        ]

        widgets = {
            'cliente': forms.Select(attrs={'onChange': 'gerar_responsaveis(this)'}),
            'produto': forms.Select(attrs={'onChange': 'verQuantidades(this)'}),
            'check_in': forms.TextInput(attrs={
                'type': 'datetime-local',
                'onChange': 'pegarDias(true)',
                'onkeyup': '$("#ModalCadastroPreReserva #id_check_in").val("")',
                'onclick': 'this.showPicker()'
            }),
            'check_out': forms.TextInput(attrs={
                'type': 'datetime-local',
                'onChange': 'pegarDias(true)',
                'onkeyup': '$("#ModalCadastroPreReserva #id_check_out").val("")',
                'onclick': 'this.showPicker()'
            }),
        }

    def __init__(self, *args, **kwargs):
        super(CadastroPreReserva, self).__init__(*args, **kwargs)
        clientes = ClienteColegio.objects.all()
        clientes_cnpj = [('', '')]

        for cliente in clientes:
            clientes_cnpj.append((cliente.id, f'{cliente.nome_fantasia} ({cliente.cnpj})'))

        self.fields['cliente'].choices = clientes_cnpj
