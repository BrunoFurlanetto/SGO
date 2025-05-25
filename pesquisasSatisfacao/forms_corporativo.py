from django import forms

from pesquisasSatisfacao.models import CoordenacaoAvaliandoMonitoria, AvaliacaoIndividualMonitor, DestaqueAtividades, \
    DesempenhoAcimaMedia, AvaliacaoIndividualCoordenador, MonitorAvaliandoCoordenacao, AvaliacaoColegio, \
    PesquisaDeSatisfacao, AvaliacaoCorporativo, AvaliacaoIndividualSala


# ----------------------------------------------------------------------------------------------------------------------
# -------------------------------- Formulário da Coordenação -> equipe de montoria -------------------------------------
# ----------------------------------------------------------------------------------------------------------------------
class AvaliacaoCorporativoForm(forms.ModelForm):
    class Meta:
        model = AvaliacaoCorporativo
        fields = '__all__'
        widgets = {
            'avaliador': forms.HiddenInput(),
            'ordem_de_servico': forms.HiddenInput(),
            'escala_peraltas': forms.HiddenInput(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['volta_proximo_ano'].choices = (
            PesquisaDeSatisfacao.get_choices_dinamicos()
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
            ('equipe_monitoria', 'equipe_monitoria_obs'),
            ('estrutura_ceu', 'estrutura_ceu_obs'),
            ('cafe_manha', 'cafe_manha_obs'),
            ('coffee_break', 'coffee_break_obs'),
            ('almoco', 'almoco_obs'),
            ('jantar', 'jantar_obs'),
            ('estrutura_geral', 'estrutura_geral_obs'),
            ('quartos', 'quartos_obs'),
            ('atendimento_bar', 'atendimento_bar_obs'),
        ]

        for campo, campo_obs in campos_avaliacao:
            if cleaned_data.get(campo) in [1, 2] and not cleaned_data.get(campo_obs):
                self.add_error(campo_obs, "Observação obrigatória para avaliações Regular ou Ruim.")

        if cleaned_data.get('volta_proximo_ano') == 'nao' and not cleaned_data.get('volta_proximo_ano_obs'):
            self.add_error('volta_proximo_ano_obs', 'Observação obrigatória em caso de escolher não voltar.')

        return cleaned_data


class AvaliacaoIndividualSalaForm(forms.ModelForm):
    class Meta:
        model = AvaliacaoIndividualSala
        fields = ['sala', 'avaliacao', 'observacao']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['sala'].widget.attrs.update({'class': 'form-select nome-monitor appearance-none'})
        self.fields['avaliacao'].widget.attrs.update({'class': 'form-select campo-avaliacao'})
        self.fields['observacao'].widget.attrs.update({'class': 'form-control campo-obs', 'rows': 3})

    def clean(self):
        cleaned_data = super().clean()

        if cleaned_data.get('sala') in [1, 2] and not cleaned_data.get('observacao'):
            self.add_error('observacao', "Observação obrigatória para avaliações Regular ou Ruim")

        return cleaned_data
