from django import forms
from django.contrib.contenttypes.models import ContentType

from ceu.models import Atividades
from peraltas.models import AtividadesEco
from pesquisasSatisfacao.models import CoordenacaoAvaliandoMonitoria, AvaliacaoIndividualMonitor, DestaqueAtividades, \
    DesempenhoAcimaMedia, AvaliacaoIndividualCoordenador, MonitorAvaliandoCoordenacao, AvaliacaoColegio, \
    PesquisaDeSatisfacao, AvaliacaoIndividualAtividade


# ----------------------------------------------------------------------------------------------------------------------
# -------------------------------- Formulário da Coordenação -> equipe de montoria -------------------------------------
# ----------------------------------------------------------------------------------------------------------------------
class AvaliacaoColegioForm(forms.ModelForm):
    class Meta:
        model = AvaliacaoColegio
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
            'cafe_manha': 'Café',
            'almoco': 'Almoço',
            'jantar': 'Jantar',
            'lanche_noite': 'Lanche noite',
        }

        for field_name, label in campos_refeicoes.items():
            if label not in refeicoes_realizadas:
                self.fields.pop(field_name, None)
                self.fields.pop(f'{field_name}_obs', None)  # caso use campos *_obs

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

        self.fields['outros_motivos'].widget.attrs.update({'cols': 40, 'rows': 4})
        self.fields['destaque'].widget.attrs.update({'cols': 40, 'rows': 4})
        self.fields['sugestoes'].widget.attrs.update({'cols': 40, 'rows': 4})

    def clean(self):
        cleaned_data = super().clean()

        # Valida campos que requerem observação quando a avaliação é Regular ou Ruim
        campos_avaliacao = [
            ('processo_vendas', 'processo_vendas_obs'),
            ('transporte_utilizado', 'transporte_utilizado_obs'),
            ('equipe_monitoria', 'equipe_monitoria_obs'),
            ('atendimento_enfermeira', 'atendimento_enfermeira_obs'),
            ('atividades_recreativas', 'atividades_recreativas_obs'),
            ('cafe_manha', 'cafe_manha_obs'),
            ('almoco', 'almoco_obs'),
            ('jantar', 'jantar_obs'),
            ('lanche_noite', 'lanche_noite_obs'),
            ('estrutura_geral', 'estrutura_geral_obs'),
            ('quartos', 'quartos_obs'),
            ('piscina', 'piscina_obs'),
        ]

        for campo, campo_obs in campos_avaliacao:
            if cleaned_data.get(campo) in [1, 2] and not cleaned_data.get(campo_obs):
                self.add_error(campo_obs, "Observação obrigatória para avaliações Regular ou Ruim.")

        if cleaned_data.get('volta_proximo_ano') == 'nao' and not cleaned_data.get('volta_proximo_ano_obs'):
            self.add_error('volta_proximo_ano_obs', 'Observação obrigatória em caso de escolher não voltar.')

        return cleaned_data


class AvaliacaoIndividualAtividadeForm(forms.ModelForm):
    atividade_combinada = forms.ChoiceField(
        choices=[],
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    class Meta:
        model = AvaliacaoIndividualAtividade
        exclude = ['pesquisa_content_type', 'pesquisa_object_id']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Configura as opções do select
        atividades = []
        for model_class in [AtividadesEco, Atividades]:
            content_type = ContentType.objects.get_for_model(model_class)

            for obj in model_class.objects.all():
                if isinstance(obj, AtividadesEco):
                    atividades.append((
                        f"{content_type.id}-{obj.id}",
                        f"[ECO] {obj.nome_atividade_eco}"
                    ))
                else:
                    atividades.append((
                        f"{content_type.id}-{obj.id}",
                        f"[CEU]{obj.atividade}"
                    ))

        self.fields['atividade_combinada'].choices = [('', '---------')] + atividades
        self.fields['atividade_combinada'].widget.attrs.update({'class': 'form-select nome-monitor appearance-none'})
        self.fields['avaliacao'].widget.attrs.update({'class': 'form-select campo-avaliacao'})
        self.fields['observacao'].widget.attrs.update({'class': 'form-control campo-obs', 'rows': 3})

        # Recupera os valores do initial OU instance
        atividade_ct_id = getattr(self.instance, 'atividade_content_type_id', None) or self.initial.get('atividade_content_type')
        atividade_obj_id = getattr(self.instance, 'atividade_object_id', None) or self.initial.get('atividade_object_id')

        if atividade_ct_id and atividade_obj_id:
            initial_value = f"{atividade_ct_id}-{atividade_obj_id}"
            self.fields['atividade_combinada'].initial = initial_value
