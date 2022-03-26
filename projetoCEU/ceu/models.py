from django.contrib.auth.models import User
from django.db import models
from django import forms


class Professores(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE)
    telefone = models.CharField(max_length=11)
    diarista = models.BooleanField(default=False)
    nota = models.FloatField(default=0.00)

    def __str__(self):
        return self.usuario.get_full_name()

    def nome_completo(self):
        return self.usuario.get_full_name()


class Estruturas(models.Model):
    estrutura = models.CharField(max_length=100)
    locavel = models.BooleanField(default=False)
    lotacao = models.IntegerField()

    def __str__(self):
        return self.estrutura


class Locaveis(models.Model):
    local = models.ForeignKey(Estruturas, on_delete=models.CASCADE, unique=True)

    def __str__(self):
        return self.local.estrutura


class Limitacoes(models.Model):
    limitacao = models.CharField(max_length=100)

    def __str__(self):
        return self.limitacao


class Atividades(models.Model):
    atividade = models.CharField(max_length=100)
    local_da_atividade = models.ForeignKey(Estruturas, on_delete=models.DO_NOTHING, related_name='local')
    numero_de_participantes_minimo = models.IntegerField()
    numero_de_participantes_maximo = models.IntegerField()
    duracao = models.DurationField()
    limitacao = models.ManyToManyField(Limitacoes)
    publico = models.BooleanField(default=False)

    def __str__(self):
        return self.atividade
