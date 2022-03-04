from django.db import models
from ceu.models import Professores


class Escala(models.Model):
    equipe = models.CharField(max_length=300)
    data = models.DateField()

    def __str__(self):
        return self.equipe

    def separar_equipe(self):
        return self.equipe.split(', ')


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
