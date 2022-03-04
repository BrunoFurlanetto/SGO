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


class Locaveis(models.Model):
    estrutura = models.CharField(max_length=100)

    def __str__(self):
        return self.estrutura


class Limitacoes(models.Model):
    limitacao = models.CharField(max_length=100)

    def __str__(self):
        return self.limitacao


class Atividades(models.Model):
    atividade = models.CharField(max_length=100)
    local_da_atividade = models.ForeignKey(Locaveis, on_delete=models.DO_NOTHING, related_name='local')
    numero_de_participantes_minimo = models.IntegerField()
    numero_de_participantes_maximo = models.IntegerField()
    duracao = models.DurationField()
    limitacao = models.ManyToManyField(Limitacoes)
    publico = models.BooleanField(default=False)

    def __str__(self):
        return self.atividade
