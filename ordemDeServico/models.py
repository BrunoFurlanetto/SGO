import datetime
import os.path

from django import forms
from django.db import models

from ceu.models import Atividades
from peraltas.models import Monitor, AtividadesEco, AtividadePeraltas, FichaDeEvento, GrupoAtividade, EmpresaOnibus
from peraltas.models import Vendedor


def atribuir_diretoria_vendedor():
    return Vendedor.objects.filter(usuario__groups__name__icontains='diretoria').first().id


class TipoVeiculo(models.Model):
    tipo_veiculo = models.CharField(max_length=255, verbose_name='Tipo de veículo')

    def __str__(self):
        return self.tipo_veiculo


class DadosTransporte(models.Model):
    empresa_onibus = models.ForeignKey(EmpresaOnibus, on_delete=models.CASCADE, blank=True, null=True)
    endereco_embarque = models.CharField(max_length=255, blank=True, null=True)
    horario_embarque = models.TimeField(blank=True, null=True)
    nome_motorista = models.CharField(max_length=255, blank=True, null=True)
    telefone_motorista = models.CharField(max_length=16, blank=True, null=True)
    monitor_embarque = models.ForeignKey(Monitor, blank=True, null=True, on_delete=models.SET_NULL)
    dados_veiculos = models.JSONField(blank=True, null=True)  # {'qtd_veiculo': int, 'tipo_veiculo': int}

    @staticmethod
    def salvar_dados(dados_transporte):
        def listar_veiculos(n):
            return [
                {
                    'veiculo': int(dados_transporte.getlist(f'veiculo_1_viacao_{n}')[0]) if dados_transporte.getlist(f'veiculo_1_viacao_{n}')[0] != '' else '',
                    'n': int(dados_transporte.getlist(f'veiculo_1_viacao_{n}')[1]) if dados_transporte.getlist(f'veiculo_1_viacao_{n}')[1] != '' else ''
                },
                {
                    'veiculo': int(dados_transporte.getlist(f'veiculo_2_viacao_{n}')[0]) if dados_transporte.getlist(f'veiculo_2_viacao_{n}')[0] != '' else '',
                    'n': int(dados_transporte.getlist(f'veiculo_2_viacao_{n}')[1]) if dados_transporte.getlist(f'veiculo_2_viacao_{n}')[1] != '' else ''
                },
                {
                    'veiculo': int(dados_transporte.getlist(f'veiculo_3_viacao_{n}')[0]) if dados_transporte.getlist(f'veiculo_3_viacao_{n}')[0] != '' else '',
                    'n': int(dados_transporte.getlist(f'veiculo_3_viacao_{n}')[1]) if dados_transporte.getlist(f'veiculo_3_viacao_{n}')[1] != '' else ''
                }
            ]

        def salvar_formularios():
            id_salvos = []

            for n, dado in enumerate(lista_dados):
                try:
                    dados_transporte_salvo = DadosTransporte.objects.get(pk=id_instancias[n])
                    form = CadastroDadosTransporte(dado, instance=dados_transporte_salvo).save()
                    id_salvos.append(form.id)
                except IndexError:
                    form = CadastroDadosTransporte(dado).save()
                    id_salvos.append(form.id)

            return id_salvos

        campos = list(CadastroDadosTransporte().fields.keys())
        lista_dados = []
        id_instancias = list(map(int, dados_transporte.getlist('id_dados_transporte')))
        n_transportes = len([
            int(id_viacao) for id_viacao in dados_transporte.getlist('empresa_onibus') if id_viacao != ''
        ])

        for transporte in range(0, n_transportes):
            dados = {}

            for campo in campos:
                if campo == 'dados_veiculos':
                    dados[campo] = listar_veiculos(transporte + 1)
                else:
                    dados[campo] = dados_transporte.getlist(campo)[transporte]

            lista_dados.append(dados)

        return salvar_formularios()

    def valor_veiculos(self):
        return [
            {'veiculo': 'micro', 'n': self.dados_veiculos['micro_onibus']},
            {'veiculo': '46', 'n': self.dados_veiculos['onibus_46']},
            {'veiculo': '50', 'n': self.dados_veiculos['onibus_50']}
        ]

    @staticmethod
    def reunir_veiculos(dados_transporte):
        return {
            'micro_onibus': int(dados_transporte.get('n_micro')) if dados_transporte.get('n_micro') else 0,
            'onibus_46': int(dados_transporte.get('n_46')) if dados_transporte.get('n_46') else 0,
            'onibus_50': int(dados_transporte.get('n_50')) if dados_transporte.get('n_50') else 0,
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
    vendedor = models.ForeignKey(Vendedor, on_delete=models.SET_DEFAULT, default=atribuir_diretoria_vendedor)
    empresa = models.CharField(choices=empresa_choices, max_length=15)
    monitor_responsavel = models.ManyToManyField(Monitor)
    dados_transporte = models.ManyToManyField(DadosTransporte, blank=True)
    check_in_ceu = models.DateTimeField(blank=True, null=True)
    check_out_ceu = models.DateTimeField(blank=True, null=True)
    atividades_eco = models.JSONField(blank=True, null=True)
    atividades_peraltas = models.ManyToManyField(AtividadePeraltas, blank=True)
    atividades_ceu = models.JSONField(blank=True, null=True)
    locacao_ceu = models.JSONField(blank=True, null=True)
    cronograma_peraltas = models.FileField(blank=True, upload_to='cronogramas/%Y/%m/%d')
    ficha_de_avaliacao = models.FileField(blank=True, null=True, upload_to='avaliacoes/%Y/%m/%d')
    observacoes_ficha_de_evento = models.TextField(blank=True, null=True)
    observacoes = models.TextField(blank=True, null=True)
    relatorio_ceu_entregue = models.BooleanField(default=False)
    ficha_avaliacao = models.BooleanField(default=False)
    escala_ceu = models.BooleanField(default=False)
    escala = models.BooleanField(default=False)
    racional_coordenadores = models.IntegerField(default=120, blank=True)
    permicao_coordenadores = models.BooleanField(default=False)
    data_preenchimento = models.DateField(default=datetime.date.today, editable=False)

    def __str__(self):
        return f'Ordem de serviço de {self.ficha_de_evento.cliente}'

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

    def listar_id_monitor_responsavel(self):
        return [monitor.id for monitor in self.monitor_responsavel.all()]

    @classmethod
    def atividades_ceu_nao_definidas(cls):
        ordens = cls.objects.filter(check_in_ceu__date__gte=datetime.date.today())
        atividades = []

        for ordem in ordens:
            dados_ativdiades = {
                'id': ordem.id,
                'cliente': ordem.ficha_de_evento.cliente.__str__(),
                'check_in_ceu': ordem.check_in_ceu,
                'qtd_evento': ordem.n_participantes,
                'vendedora': ordem.vendedor.usuario.get_full_name(),
                'atividades_sem_definicao': [],
                'a_definir': 0,
            }

            for atividade in ordem.atividades_ceu.values():
                atividade_bd = Atividades.objects.get(pk=atividade['atividade'])

                if atividade_bd.a_definir:
                    dados_ativdiades['a_definir'] += 1
                elif not atividade_bd.sem_atividade and atividade['data_e_hora'] == '':
                    dados_ativdiades['atividades_sem_definicao'].append(atividade_bd.atividade)

            if len(dados_ativdiades['atividades_sem_definicao']) != 0 or dados_ativdiades['a_definir'] != 0:
                atividades.append(dados_ativdiades)

        return atividades


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

        monitores = Monitor.objects.filter(nivel_acampamento__coordenacao=True)
        monitores_selecao = []

        for monitor in monitores:
            monitores_selecao.append((monitor.id, monitor.usuario.get_full_name()))

        self.fields['monitor_responsavel'].choices = monitores_selecao

    def clean(self):
        cleaned_data = super(CadastroOrdemDeServico, self).clean()
        print(cleaned_data)

        return cleaned_data

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
            'horario_embarque': forms.TimeInput(attrs={'type': 'time', 'step': '60'}),
            'telefone_motorista': forms.TextInput(attrs={'onfocus': 'mascara_telefone(this)'})
        }
