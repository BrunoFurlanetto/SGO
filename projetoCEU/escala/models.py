from datetime import datetime

from django.db import models
from django import forms

from ceu.models import Professores
from peraltas.models import ClienteColegio


class Escala(models.Model):
    tipo_escala_choice = (
        (0, ''),
        (1, 'Público'),
        (2, 'Grupo'),
    )

    tipo_escala = models.IntegerField(choices=tipo_escala_choice, default=0)
    cliente = models.ForeignKey(ClienteColegio, on_delete=models.CASCADE, blank=True, null=True)
    equipe = models.ManyToManyField(Professores)  # {'coordenador': ,'professor_1: , 'professor_2': , 'professor_3':...}
    check_in_grupo = models.DateTimeField(blank=True)
    check_out_grupo = models.DateTimeField(blank=True)

    def __str__(self):
        return f'Escala de(o) {self.cliente}'

    def separar_equipe(self):
        for key in self.equipe:
            return self.equipe[key]


class Disponibilidade(models.Model):
    meses = {
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
    }

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
