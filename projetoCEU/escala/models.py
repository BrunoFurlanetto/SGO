from django.db import models

from cadastro.models import Professores


class Escala(models.Model):
    equipe = models.CharField(max_length=300)
    data = models.DateField()

    def __str__(self):
        return self.equipe

    def separar_equipe(self):
        return self.equipe.split(', ')


class Disponibilidade(models.Model):
    professor = models.ForeignKey(Professores, on_delete=models.CASCADE)
    dias_disponiveis = models.TextField(max_length=500)
    mes = models.CharField(max_length=20)
    ano = models.CharField(max_length=20)
    n_dias = models.IntegerField()

    def separar_dias(self):
        return self.dias_disponiveis.split(', ')
