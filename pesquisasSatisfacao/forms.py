from django import forms
from django.forms import modelformset_factory

from pesquisasSatisfacao.models import CoordenacaoAvaliandoMonitoria, AvaliacaoIndividualMonitor, DestaqueAtividades, \
    DesempenhoAcimaMedia


# ----------------------------------------------------------------------------------------------------------------------
# -------------------------------- Formulário da Coordenação -> equipe de montoria -------------------------------------
# ----------------------------------------------------------------------------------------------------------------------
class CoordenacaoAvaliandoMonitoriaForm(forms.ModelForm):
    class Meta:
        model = CoordenacaoAvaliandoMonitoria
        exclude = ['monitores_destaque_atividades', 'monitores_acima_media']
        widgets = {
            'coordenador': forms.HiddenInput(),
            'ordem_de_servico': forms.HiddenInput(),
            'escala_peraltas': forms.HiddenInput(),
        }

    def __init__(self, *args, **kwargs):
        monitores = kwargs.pop('monitores', None)
        super().__init__(*args, **kwargs)

        for i in range(1, 6):
            self.fields[f'palavra_{i}'] = forms.CharField(
                max_length=50,
                required=False,
                label=f'Palavra-chave {i}',
                initial=self.instance.palavras_descricao[i - 1] if self.instance.palavras_descricao and len(
                    self.instance.palavras_descricao) >= i else ''
            )

        # Personalizações dos campos
        for field_name, field in self.fields.items():
            classes = []

            # Configuração base por tipo de campo
            if isinstance(field, forms.BooleanField):
                classes.append('form-check-input')
            elif isinstance(field, forms.IntegerField):
                classes.append('form-control')
                field.widget.attrs.update({'min': 1, 'max': 5})
            else:
                classes.append('form-control')

            # Adiciona classes específicas
            if field_name.endswith('obs'):
                classes.append('campo-obs')
                field.widget.attrs.update({'cols': 40, 'rows': 4})
            else:
                classes.append('campo-avaliacao')

            # Atualiza atributos sem sobrescrever
            field.widget.attrs['class'] = ' '.join(classes)

        if monitores:
            # Filtra os monitores da escala (ajuste o relacionamento conforme seu modelo)
            self.fields['monitores_destaque_evento'].queryset = monitores
            self.fields['monitores_destaque_pedagogicas'].queryset = monitores

    def clean(self):
        cleaned_data = super().clean()

        # Valida campos que requerem observação quando a avaliação é Regular ou Ruim
        campos_avaliacao = [
            ('pontualidade_chegada', 'pontualidade_chegada_obs'),
            ('pontualidade_atividades', 'pontualidade_atividades_obs'),
            ('programacao_aplicada', 'programacao_aplicada_obs'),
            ('seguiu_programacao', 'seguiu_programacao_obs'),
            ('cuidados_materiais', 'cuidados_materiais_obs'),
        ]

        for campo, campo_obs in campos_avaliacao:
            if cleaned_data.get(campo) in [1, 2] and not cleaned_data.get(campo_obs):
                self.add_error(campo_obs, "Observação obrigatória para avaliações Regular ou Ruim")

        # Valida campos booleanos que requerem observação
        campos_booleanos = [
            ('captou_orientacoes', 'captou_orientacoes_obs'),
            ('iniciativa_empenho', 'iniciativa_empenho_obs'),
        ]

        for campo, campo_obs in campos_booleanos:
            if not cleaned_data.get(campo) and cleaned_data.get(campo_obs) == "":
                self.add_error(campo_obs, "Campo de observação obrigatório")

        palavras = [
            cleaned_data.get(f'palavra_{i}').strip()
            for i in range(1, 6)
            if cleaned_data.get(f'palavra_{i}') and cleaned_data.get(f'palavra_{i}').strip()
        ]
        cleaned_data['palavras_descricao'] = palavras

        return cleaned_data


class AvaliacaoIndividualMonitorForm(forms.ModelForm):
    class Meta:
        model = AvaliacaoIndividualMonitor
        fields = ['monitor', 'avaliacao', 'observacao']

    def get_monitor_nome(self):
        if self.instance.pk and self.instance.monitor:
            return self.instance.monitor.usuario.get_full_name()
        # elif self.initial.get('monitor'):
        #     # Busca o nome manualmente
        #     from app.models import MonitorEscala  # ou onde estiver o model
        #     try:
        #         monitor = MonitorEscala.objects.get(pk=self.initial['monitor'])
        #         return monitor.usuario.get_full_name()
        #     except MonitorEscala.DoesNotExist:
        #         return 'Monitor não encontrado'

        return 'Nome não disponível'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['monitor'].widget.attrs.update({'class': 'form-select nome-monitor appearance-none'})
        self.fields['avaliacao'].widget.attrs.update({'class': 'form-select campo-avaliacao'})
        self.fields['observacao'].widget.attrs.update({'class': 'form-control campo-obs', 'rows': 3})

    def clean(self):
        cleaned_data = super().clean()

        if cleaned_data.get('avaliacao') in [1, 2] and not cleaned_data.get('observacao'):
            self.add_error('observacao', "Observação obrigatória para avaliações Regular ou Ruim")

        return cleaned_data


class DestaqueAtividadesForm(forms.ModelForm):
    class Meta:
        model = DestaqueAtividades
        fields = ['monitor', 'posicao']

    def __init__(self, *args, avaliacao_id=None, **kwargs):
        monitores = kwargs.pop('monitores', None)  # Remove 'escala' dos kwargs
        super().__init__(*args, **kwargs)
        self.fields['monitor'].widget.attrs.update({'class': 'form-select monitor-select', 'onchange': 'validateAllMonitors("destaque")'})
        self.fields['posicao'].widget.attrs.update({'class': 'form-control', 'min': 1})

        if monitores:
            # Filtra os monitores da escala (ajuste o relacionamento conforme seu modelo)
            self.fields['monitor'].queryset = monitores


class DesempenhoAcimaMediaForm(forms.ModelForm):
    class Meta:
        model = DesempenhoAcimaMedia
        fields = ['monitor', 'posicao']

    def __init__(self, *args, avaliacao_id=None, **kwargs):
        monitores = kwargs.pop('monitores', None)  # Remove 'escala' dos kwargs
        super().__init__(*args, **kwargs)
        self.fields['monitor'].widget.attrs.update({'class': 'form-select', 'onchange': 'validateAllMonitors("desempenho")'})
        self.fields['posicao'].widget.attrs.update({'class': 'form-control', 'min': 1})

        if monitores:
            # Filtra os monitores da escala (ajuste o relacionamento conforme seu modelo)
            self.fields['monitor'].queryset = monitores


AvaliacaoIndividualMonitorFormSet = modelformset_factory(
    AvaliacaoIndividualMonitor,  # Ou o modelo que você está usando
    form=AvaliacaoIndividualMonitorForm,
    extra=1,  # Quantidade de forms extras (pode ser 0 se já tiver monitores)
)

DestaqueAtividadesFormSet = modelformset_factory(
    DestaqueAtividades,
    form=DestaqueAtividadesForm,
    extra=1,
)

DesempenhoAcimaMediaFormSet = modelformset_factory(
    DesempenhoAcimaMedia,
    form=DesempenhoAcimaMediaForm,
    extra=1,
)
