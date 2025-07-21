from datetime import datetime

from django.core.exceptions import ValidationError
from django.db import models
from django import forms

from ceu.models import Professores
from peraltas.models import ClienteColegio


class Escala(models.Model):
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

    equipe = models.JSONField(blank=True, null=True)  # {'professores': [id_professores]}
    data_escala = models.DateField(null=True)
    mes = models.IntegerField(choices=meses)
    ano = models.IntegerField()

    def __str__(self):
        return f'Escala do dia {self.data_escala}'

    def separar_equipe(self):
        return [Professores.objects.get(pk=id_professor).usuario.get_full_name() for id_professor in self.equipe]

    def pegar_equipe(self):
        lista_equipe = [Professores.objects.get(pk=id_professor).usuario.get_full_name() for id_professor in self.equipe]

        return ', '.join(lista_equipe)


class Disponibilidade(models.Model):
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

    professor = models.ForeignKey(Professores, on_delete=models.CASCADE)
    dias_disponiveis = models.TextField(max_length=500)
    mes = models.IntegerField(choices=meses)
    ano = models.CharField(max_length=20)
    n_dias = models.IntegerField()

    def __str__(self):
        return f'Disponibilidade de {self.professor.usuario.first_name} para o mês {self.mes}'

# ----- Função responsávvel por verificar a disponibilidade para o dia selecionado na aba de escala ---------
    @staticmethod
    def verificar_dias(mes, data):
        professores_disponiveis = []

        for teste in mes:
            dias = teste.dias_disponiveis.split(', ')

            if data in dias:
                professores_disponiveis.append(teste.professor.usuario.first_name)

        return ', '.join(professores_disponiveis)
# -----------------------------------------------------------------------------------------------------------


class DiaLimite(models.Model):
    dia_limite = models.PositiveIntegerField()


# ------------------------------------ Formulários ----------------------------------------------------------
class FormularioEscalaCeu(forms.ModelForm):
    class Meta:
        model = Escala
        exclude = ()

        widgets = {
            'check_in_grupo': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'check_out_grupo': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'tipo_escala': forms.Select(attrs={'onChange': 'ver_tipo_escala(this)'}),
        }


class DisponibilidadeForm(forms.ModelForm):
    dias_disponiveis = forms.MultipleChoiceField(
        choices=[],
        widget=forms.CheckboxSelectMultiple,
        help_text='Seleciona as datas que desejar retirar a disponibilidade do professor.'
    )

    class Meta:
        model = Disponibilidade
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(DisponibilidadeForm, self).__init__(*args, **kwargs)

        if self.instance.dias_disponiveis:
            dias_salvos = [dia.strip() for dia in self.instance.dias_disponiveis.split(',')]
        else:
            dias_salvos = []

        self.fields['dias_disponiveis'].choices = [(dia, dia) for dia in dias_salvos]

    def clean(self):
        cleaned_data = super().clean()

        if not cleaned_data.get('dias_disponiveis'):
            raise ValidationError('Seleciona ao menos uma data para remover da disponibilidade do professor.')

        dias_disponiveis_inicial = self.initial.get('dias_disponiveis', '').split(', ')
        nova_disponibilidade = [dia.strip() for dia in dias_disponiveis_inicial if dia not in cleaned_data['dias_disponiveis']]
        cleaned_data['dias_disponiveis'] = ', '.join(nova_disponibilidade)
        cleaned_data['n_dias'] = len(nova_disponibilidade)

        if cleaned_data['n_dias'] == 0:
            raise ValidationError('Para retirar a disponibilidade do professor para estes mês em questão, exclua na tela anterior!')

        return cleaned_data


