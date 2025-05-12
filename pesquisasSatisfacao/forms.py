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
        exclude = ['monitores_destaque_atividades', 'monitores_destaque_pedagogicas',
                   'monitores_destaque_evento', 'monitores_acima_media']
        widgets = {
            'coordenador': forms.HiddenInput(),
            'ordem_de_servico': forms.HiddenInput(),
            'escala_peraltas': forms.HiddenInput(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Personalizações dos campos
        for field_name, field in self.fields.items():
            if isinstance(field, forms.BooleanField):
                field.widget.attrs.update({'class': 'form-check-input'})
            elif isinstance(field, forms.IntegerField):
                field.widget.attrs.update({'class': 'form-control', 'min': 1, 'max': 5})
            else:
                field.widget.attrs.update({'class': 'form-control'})

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
            if cleaned_data.get(campo) is not None and not cleaned_data.get(campo_obs):
                self.add_error(campo_obs, "Campo de observação obrigatório")

        return cleaned_data


class AvaliacaoIndividualMonitorForm(forms.ModelForm):
    class Meta:
        model = AvaliacaoIndividualMonitor
        fields = ['monitor', 'avaliacao', 'observacao']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['monitor'].widget.attrs.update({'class': 'form-select'})
        self.fields['avaliacao'].widget.attrs.update({'class': 'form-select'})
        self.fields['observacao'].widget.attrs.update({'class': 'form-control', 'rows': 3})

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
        escala = kwargs.pop('escala', None)  # Remove 'escala' dos kwargs
        super().__init__(*args, **kwargs)
        self.fields['monitor'].widget.attrs.update({'class': 'form-select monitor-select', 'onchange': 'validateAllMonitors()'})
        self.fields['posicao'].widget.attrs.update({'class': 'form-control', 'min': 1})

        if escala:
            # Filtra os monitores da escala (ajuste o relacionamento conforme seu modelo)
            self.fields['monitor'].queryset = escala.monitores_acampamento.all()


class DesempenhoAcimaMediaForm(forms.ModelForm):
    class Meta:
        model = DesempenhoAcimaMedia
        fields = ['monitor', 'posicao']

    def __init__(self, *args, avaliacao_id=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['monitor'].widget.attrs.update({'class': 'form-select'})
        self.fields['posicao'].widget.attrs.update({'class': 'form-control', 'min': 1})


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
