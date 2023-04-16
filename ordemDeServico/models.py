import os.path

from django import forms
from django.db import models

from peraltas.models import Monitor, AtividadesEco, AtividadePeraltas, FichaDeEvento, GrupoAtividade, EmpresaOnibus

from peraltas.models import Vendedor


class DadosTransporte(models.Model):
    empresa_onibus = models.ForeignKey(EmpresaOnibus, on_delete=models.CASCADE, blank=True, null=True)
    endereco_embarque = models.CharField(max_length=255, blank=True, null=True)
    horario_embarque = models.TimeField(blank=True, null=True)
    nome_motorista = models.CharField(max_length=255, blank=True, null=True)
    telefone_motorista = models.CharField(max_length=16, blank=True, null=True)
    dados_veiculos = models.JSONField(blank=True, null=True)  # {'qtd_veiculo': int, 'tipo_veiculo': str}

    def valor_veiculos(self):
        return [
            {'veiculo': 'micro', 'n': self.dados_veiculos['micro_onibus']},
            {'veiculo': '46', 'n': self.dados_veiculos['onibus_46']},
            {'veiculo': '50', 'n': self.dados_veiculos['onibus_50']}
        ]

    @staticmethod
    def reunir_veiculos(daddos_transporte):
        return {
            'micro_onibus': int(daddos_transporte.get('n_micro')) if daddos_transporte.get('n_micro') else 0,
            'onibus_46': int(daddos_transporte.get('n_46')) if daddos_transporte.get('n_46') else 0,
            'onibus_50': int(daddos_transporte.get('n_50')) if daddos_transporte.get('n_50') else 0,
        }


class OrdemDeServico(models.Model):
    tipo_choice = (
        ('Colégio', 'Colégio'),
        ('Empresa', 'Empresa')
    )

    empresa_choices = (
        ('Peraltas', 'Peraltas'),
        ('CEU', 'Fundação CEU'),
        ('Peraltas CEU', 'Peraltas + Fundação CEU')
    )

    tipo = models.CharField(choices=tipo_choice, max_length=7)
    ficha_de_evento = models.ForeignKey(FichaDeEvento, on_delete=models.CASCADE)
    instituicao = models.CharField(max_length=300)
    cidade = models.CharField(max_length=255)
    check_in = models.DateTimeField()
    check_out = models.DateTimeField()
    n_participantes = models.IntegerField()
    serie = models.CharField(max_length=255, blank=True, null=True)
    n_professores = models.IntegerField(blank=True, null=True)
    responsavel_grupo = models.CharField(max_length=255)
    lista_segurados = models.FileField(blank=True, upload_to='seguros/%Y/%m/%d')
    vendedor = models.ForeignKey(Vendedor, on_delete=models.DO_NOTHING, blank=True,
                                 null=True)  # TODO: Verificar cado de exclusão de colaborador
    empresa = models.CharField(choices=empresa_choices, max_length=15)
    monitor_responsavel = models.ManyToManyField(Monitor)
    dados_transporte = models.ForeignKey(DadosTransporte, null=True, blank=True, on_delete=models.CASCADE)
    monitor_embarque = models.ForeignKey(Monitor, blank=True, null=True, on_delete=models.DO_NOTHING,
                                         related_name='monitor_embarque')
    check_in_ceu = models.DateTimeField(blank=True, null=True)
    check_out_ceu = models.DateTimeField(blank=True, null=True)
    atividades_eco = models.JSONField(blank=True, null=True)
    atividades_peraltas = models.ManyToManyField(AtividadePeraltas, blank=True)
    atividades_ceu = models.JSONField(blank=True, null=True)
    locacao_ceu = models.JSONField(blank=True, null=True)
    cronograma_peraltas = models.FileField(blank=True, upload_to='cronogramas/%Y/%m/%d')
    observacoes = models.TextField(blank=True, null=True)
    relatorio_ceu_entregue = models.BooleanField(default=False)
    ficha_avaliacao = models.BooleanField(default=False)
    escala_ceu = models.BooleanField(default=False)
    escala = models.BooleanField(default=False)
    racional_coordenadores = models.IntegerField(default=120, blank=True)
    permicao_coordenadores = models.BooleanField(default=False)

    def dividir_atividades_ceu(self):
        atividades = []

        for atividade in self.atividades_ceu.values():
            atividades.append(atividade)

        return atividades

    def dividir_locacoes_ceu(self):
        locacoes = []

        for locacao in self.locacao_ceu.values():
            locacoes.append(locacao)

        return locacoes

    def dividir_atividades_eco(self):
        atividades = []

        for atividade in self.atividades_eco.values():
            atividades.append(atividade)

        return atividades

    def atividade_biologo(self):
        if self.atividades_eco:
            biologo = False

            for atividade in self.atividades_eco.values():
                if atividade['biologo'] == 'sim':
                    biologo = True

            return biologo

    @staticmethod
    def pegar_biologos():
        return Monitor.objects.filter(biologo=True)


class CadastroOrdemDeServico(forms.ModelForm):
    class Meta:
        model = OrdemDeServico
        exclude = ()

        widgets = {
            'check_in': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'check_out': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'check_in_ceu': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'check_out_ceu': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'n_participantes': forms.NumberInput(attrs={'min': '0', 'onchange': 'atualizar_participantes(this)'}),
            'tipo': forms.Select(attrs={'onchange': "$('#id_empresa').trigger('change')"}),
            'empresa': forms.Select(attrs={'onchange': 'verificar_atividades(this)'}),
        }

    def __init__(self, *args, **kwargs):
        super(CadastroOrdemDeServico, self).__init__(*args, **kwargs)
        self.fields['atividades_peraltas'].choices = self.opt_groups()
        self.fields['instituicao'].widget.attrs['readonly'] = True
        self.fields['cidade'].widget.attrs['readonly'] = True
        self.fields['responsavel_grupo'].widget.attrs['readonly'] = True

        monitores = Monitor.objects.filter(nivel__nivel__contains='Coordenador')
        monitores_selecao = []

        for monitor in monitores:
            monitores_selecao.append((monitor.id, monitor.usuario.get_full_name()))

        self.fields['monitor_responsavel'].choices = monitores_selecao

    @staticmethod
    def opt_groups():
        grupos = []

        for grupo in GrupoAtividade.objects.all():
            novo_grupo = []
            sub_grupo = []

            for atividade in AtividadePeraltas.objects.all():
                if atividade.grupo == grupo:
                    sub_grupo.append([atividade.id, atividade.nome_atividade])

            novo_grupo = [grupo, sub_grupo]
            grupos.append(novo_grupo)

        return grupos


class CadastroDadosTransporte(forms.ModelForm):
    class Meta:
        model = DadosTransporte
        exclude = ()

        widgets = {
            'horario_embarque': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'telefone_motorista': forms.TextInput(attrs={'onclick': 'mascara_telefone()'})
        }
