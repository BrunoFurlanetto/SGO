from django.contrib.auth.models import User
from django.db import models

from peraltas.models import ClienteColegio, FichaDeEvento, ProdutosPeraltas


class Cozinheiro(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    telefone = models.CharField(max_length=11)


class Relatorio(models.Model):
    ficha_de_evento = models.OneToOneField(FichaDeEvento, on_delete=models.CASCADE)
    grupo = models.ForeignKey(ClienteColegio, on_delete=models.CASCADE)
    tipo_evento = models.ForeignKey(ProdutosPeraltas, on_delete=models.PROTECT)
    pax_adulto = models.PositiveIntegerField(default=0)
    pax_crianca = models.PositiveIntegerField(default=0)
    pax_monitoria = models.PositiveIntegerField(default=0)
    total_pax = models.PositiveIntegerField(default=0, editable=False)
    dados_cafe_da_manha = models.JSONField(null=True, blank=True)
    dados_lanche_da_manha = models.JSONField(null=True, blank=True)
    dados_almoco = models.JSONField(null=True, blank=True)
    dados_lanche_da_tarde = models.JSONField(null=True, blank=True)
    dados_jantar = models.JSONField(null=True, blank=True)
    dados_lanche_da_noite = models.JSONField(null=True, blank=True)

    def __str__(self):
        return f'Dados refeições {self.grupo}'

    def save(self, *args, **kwargs):
        self.total_pax = self.pax_adulto + self.pax_crianca + self.pax_monitoria
        super().save(*args, **kwargs)
