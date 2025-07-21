from django import forms
from django.contrib.contenttypes.models import ContentType

from ceu.models import Locaveis
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
        refeicoes_realizadas = kwargs.pop('refeicoes_realizadas', [])
        super().__init__(*args, **kwargs)
        self.fields['volta_proximo_ano'].choices = (
            PesquisaDeSatisfacao.get_choices_dinamicos()
        )

        campos_refeicoes = {
            'cafe_manha': ['Café'],
            'coffee_break': ['Coffee manhã', 'Coffee tarde'],
            'almoco': ['Almoço'],
            'jantar': ['Jantar'],
            'lanche_noite': ['Lanche noite'],
        }

        for field_name, labels in campos_refeicoes.items():
            # Verifica se TODAS as labels esperadas estão presentes
            if not any(label in refeicoes_realizadas for label in labels):
                self.fields.pop(field_name, None)
                self.fields.pop(f'{field_name}_obs', None)

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

        self.fields['mais_valorizou'].widget.attrs.update({'cols': 40, 'rows': 4})
        self.fields['sugestoes'].widget.attrs.update({'cols': 40, 'rows': 4})

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
    sala_combinada = forms.ChoiceField(
        choices=[],
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    class Meta:
        model = AvaliacaoIndividualSala
        exclude = ['pesquisa_corporativo_content_type', 'pesquisa_corporativo_object_id']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Configura as opções do select
        salas = []
        content_type = ContentType.objects.get_for_model(Locaveis)

        for obj in Locaveis.objects.all():
            salas.append((
                f"{content_type.id}-{obj.id}",
                f"{obj.local.estrutura}"
            ))

        self.fields['sala_combinada'].choices = [('', '---------')] + salas
        self.fields['sala_combinada'].widget.attrs.update({'class': 'form-select nome-monitor appearance-none'})
        self.fields['avaliacao'].widget.attrs.update({'class': 'form-select campo-avaliacao'})
        self.fields['observacao'].widget.attrs.update({'class': 'form-control campo-obs', 'rows': 3})

        # Recupera os valores do initial OU instance
        sala_ct_id = getattr(self.instance, 'sala_content_type_id', None) or self.initial.get(
            'sala_content_type')
        sala_obj_id = getattr(self.instance, 'sala_object_id', None) or self.initial.get(
            'sala_object_id')

        if sala_ct_id and sala_obj_id:
            initial_value = f"{sala_ct_id}-{sala_obj_id}"
            self.fields['sala_combinada'].initial = initial_value
