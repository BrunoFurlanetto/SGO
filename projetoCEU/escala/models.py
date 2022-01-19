from django.db import models


class Escala(models.Model):
    equipe = models.CharField(max_length=300)
    data = models.DateField()

    def __str__(self):
        return self.equipe

    def separar_equipe(self):
        return self.equipe.split(', ')
