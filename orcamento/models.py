from django.db import models


# Create your models here. extend increment
class OrcamentoMonitor(models.Model):
    nome_monitoria = models.CharField(max_length=100)
    descricao_monitoria = models.TextField()
    valor = models.DecimalField(decimal_places=2, max_digits=5)


class OrcamentoOpicional(models.Model):
    nome = models.CharField(max_length=100)
    valor = models.DecimalField(decimal_places=2, max_digits=5)


class OrcamentoPeriodo(models.Model):
    nome_periodo = models.CharField(max_length=255)
    id = models.CharField(max_length=11, unique=True, primary_key=True)


class OrcamentoAlimentacao(models.Model):
    tipo_alimentacao = models.CharField(max_length=100)
    valor = models.DecimalField(decimal_places=2, max_digits=5)
