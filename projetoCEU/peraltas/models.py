from django.db import models


class Monitor(models.Model):
    nome = models.CharField(max_length=255)

    def __str__(self):
        return self.nome


class Vendedor(models.Model):
    nome_vendedor = models.CharField(max_length=255)

    def __str__(self):
        return self.nome_vendedor
