from django.db import models

from peraltas.models import ClienteColegio


class DetectorDeBombas(models.Model):
    grupos = models.ManyToManyField(ClienteColegio)
    data_inicio = models.DateField(blank=True)
    data_final = models.DateField(blank=True)
    dados_atividades = models.JSONField()
    observacoes = models.TextField(blank=True)

    def mostrar_grupos(self):
        lista_grupos = []

        for grupo in self.grupos.all():
            lista_grupos.append(grupo.nome_fantasia)

        return ', '.join(lista_grupos)
