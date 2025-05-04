from django import forms

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
        super().__init__(*args, **kwargs)
        self.fields['monitor'].widget.attrs.update({'class': 'form-select'})
        self.fields['posicao'].widget.attrs.update({'class': 'form-control', 'min': 1})


class DesempenhoAcimaMediaForm(forms.ModelForm):
    class Meta:
        model = DesempenhoAcimaMedia
        fields = ['monitor', 'posicao']

    def __init__(self, *args, avaliacao_id=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['monitor'].widget.attrs.update({'class': 'form-select'})
        self.fields['posicao'].widget.attrs.update({'class': 'form-control', 'min': 1})


# Formset para avaliações individuais
AvaliacaoIndividualMonitorFormSet = forms.inlineformset_factory(
    CoordenacaoAvaliandoMonitoria,
    AvaliacaoIndividualMonitor,
    form=AvaliacaoIndividualMonitorForm,
    extra=1,
    can_delete=False
)

# Formset para destaques em atividades
DestaqueAtividadesFormSet = forms.inlineformset_factory(
    CoordenacaoAvaliandoMonitoria,
    DestaqueAtividades,
    form=DestaqueAtividadesForm,
    extra=1,
    can_delete=True
)

# Formset para desempenho acima da média
DesempenhoAcimaMediaFormSet = forms.inlineformset_factory(
    CoordenacaoAvaliandoMonitoria,
    DesempenhoAcimaMedia,
    form=DesempenhoAcimaMediaForm,
    extra=1,
    can_delete=True
)