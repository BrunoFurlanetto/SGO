from datetime import datetime

from django.db import models
from django import forms

from ceu.models import Professores
from peraltas.models import ClienteColegio


class Escala(models.Model):
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

    equipe = models.JSONField(blank=True, null=True)  # {'professores': [id_professores]}
    data_escala = models.DateField(null=True)
    mes = models.IntegerField(choices=meses, default=datetime.now().month + 1)
    ano = models.IntegerField(default=datetime.now().year)

    def __str__(self):
        return f'Escala do dia {self.data_escala}'

    def separar_equipe(self):
        professores = []

        for valor in self.equipe.values():
            professor = Professores.objects.get(id=valor)
            professores.append(professor.usuario.get_full_name())

        return professores

    def pegar_equipe(self):
        lista_equipe = []

        for valor in self.equipe.values():
            professor = Professores.objects.get(id=valor)
            lista_equipe.append(professor.usuario.get_full_name())

        return ', '.join(lista_equipe)


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
