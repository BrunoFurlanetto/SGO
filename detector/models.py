from django.db import models

from peraltas.models import ClienteColegio


class DetectorDeBombas(models.Model):
    setores = (
        ('', ''),
        ('ceu', 'CEU'),
        ('peraltas', 'Peraltas'),
    )

    grupos = models.ManyToManyField(ClienteColegio)
    data_inicio = models.DateField(blank=True)
    data_final = models.DateField(blank=True)
    dados_atividades = models.JSONField()
    setor = models.CharField(max_length=8, choices=setores)
    observacoes = models.TextField(blank=True)

    def mostrar_grupos(self):
        lista_grupos = []

        for grupo in self.grupos.all():
            lista_grupos.append(grupo.nome_fantasia)

        return ', '.join(lista_grupos)
