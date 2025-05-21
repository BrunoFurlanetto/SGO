from django import forms

from pesquisasSatisfacao.models import CoordenacaoAvaliandoMonitoria, AvaliacaoIndividualMonitor, DestaqueAtividades, \
    DesempenhoAcimaMedia, AvaliacaoIndividualCoordenador, MonitorAvaliandoCoordenacao


# ----------------------------------------------------------------------------------------------------------------------
# -------------------------------- Formulário da Coordenação -> equipe de montoria -------------------------------------
# ----------------------------------------------------------------------------------------------------------------------
class MonitoriaAvaliandoCoordenacaoForm(forms.ModelForm):
    class Meta:
        model = MonitorAvaliandoCoordenacao
        fields = '__all__'
        widgets = {
            'monitor': forms.HiddenInput(),
            'ordem_de_servico': forms.HiddenInput(),
            'escala_peraltas': forms.HiddenInput(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for i in range(1, 6):
            self.fields[f'palavra_{i}'] = forms.CharField(
                max_length=50,
                required=False,
                label=f'Palavra-chave {i}',
                initial=self.instance.palavras_chave[i - 1] if self.instance.palavras_chave and len(
                    self.instance.palavras_chave) >= i else ''
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

    def clean(self):
        cleaned_data = super().clean()

        # Valida campos que requerem observação quando a avaliação é Regular ou Ruim
        campos_avaliacao = [
            ('pontualidade_chegada', 'pontualidade_chegada_obs'),
            ('pontualidade_atividades', 'pontualidade_atividades_obs'),
            ('cuidados_materiais', 'cuidados_materiais_obs'),
            ('desenvoltura_equipe', 'desenvoltura_equipe_obs'),
            ('organizacao_evento', 'organizacao_evento_obs'),
            ('programacao_aplicada', 'programacao_aplicada_obs'),
            ('seguiu_programacao', 'seguiu_programacao_obs'),
        ]

        for campo, campo_obs in campos_avaliacao:
            if cleaned_data.get(campo) in [1, 2] and not cleaned_data.get(campo_obs):
                self.add_error(campo_obs, "Observação obrigatória para avaliações Regular ou Ruim")

        # Valida campos booleanos que requerem observação
        campos_booleanos = [
            ('teve_briefing', 'teve_briefing_obs'),
            ('teve_feedback', 'teve_feedback_obs'),
            ('coordenador_participou', 'coordenador_participou_obs'),
            ('tem_consideracoes_pedagogicas', 'tem_consideracoes_pedagogicas_obs'),
        ]

        for campo, campo_obs in campos_booleanos:
            if not cleaned_data.get(campo) and cleaned_data.get(campo_obs) == "":
                self.add_error(campo_obs, "Campo de observação obrigatório")

        palavras = [
            cleaned_data.get(f'palavra_{i}').strip()
            for i in range(1, 6)
            if cleaned_data.get(f'palavra_{i}') and cleaned_data.get(f'palavra_{i}').strip()
        ]
        cleaned_data['palavras_chave'] = palavras

        return cleaned_data


class AvaliacaoIndividualCoordenadorForm(forms.ModelForm):
    class Meta:
        model = AvaliacaoIndividualCoordenador
        fields = ['coordenador', 'avaliacao', 'observacao']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['coordenador'].widget.attrs.update({'class': 'form-select nome-monitor appearance-none'})
        self.fields['avaliacao'].widget.attrs.update({'class': 'form-select campo-avaliacao'})
        self.fields['observacao'].widget.attrs.update({'class': 'form-control campo-obs', 'rows': 3})

    def clean(self):
        cleaned_data = super().clean()

        if cleaned_data.get('avaliacao') in [1, 2] and not cleaned_data.get('observacao'):
            self.add_error('observacao', "Observação obrigatória para avaliações Regular ou Ruim")

        return cleaned_data
