from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone

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

    @staticmethod
    def dividir_refeicoes(dados_refeicoes):
        refeicoes= {}

        for refeicao_dia in dados_refeicoes.keys():
            if '-' in refeicao_dia:
                refeicao, dia = refeicao_dia.split('-')
                participantes = dados_refeicoes.getlist(refeicao_dia)

                if refeicao not in refeicoes:
                    refeicoes[refeicao] = []

                refeicoes[refeicao].append({
                    'dia': dia,
                    'hora': participantes[0],
                    'participantes': {
                        'adultos': participantes[1],
                        'criancas': participantes[2],
                        'monitoria': participantes[3],
                        'total': participantes[4],
                    }
                })

        return refeicoes

    def salvar_refeicoes(self, lista_refeicoes):
        refeicoes = lista_refeicoes.keys()

        if 'cafe_manha' in refeicoes:
            self.dados_cafe_da_manha = lista_refeicoes['cafe_manha']

        if 'lanche_manha' in refeicoes:
            self.dados_lanche_da_manha = lista_refeicoes['lanche_manha']

        if 'almoco' in refeicoes:
            self.dados_almoco = lista_refeicoes['almoco']

        if 'lanche_tarde' in refeicoes:
            self.dados_lanche_da_tarde = lista_refeicoes['lanche_tarde']

        if 'jantar' in refeicoes:
            self.dados_jantar = lista_refeicoes['jantar']

        if 'lanche_noite' in refeicoes:
            self.dados_lanche_da_noite = lista_refeicoes['lanche_noite']

    def save(self, *args, **kwargs):
        self.total_pax = self.pax_adulto + self.pax_crianca + self.pax_monitoria
        super().save(*args, **kwargs)


class RelatorioDia(models.Model):
    fichas_de_evento = models.ManyToManyField(FichaDeEvento)
    grupos = models.ManyToManyField(ClienteColegio)
    data = models.DateField(default=timezone.now)
    total_pax_adulto = models.PositiveIntegerField(default=0)
    total_pax_crianca = models.PositiveIntegerField(default=0)
    total_pax_monitoria = models.PositiveIntegerField(default=0)
    total_geral_pax = models.PositiveIntegerField(default=0, editable=False)
    dados_cafe_da_manha = models.JSONField(null=True, blank=True)
    dados_lanche_da_manha = models.JSONField(null=True, blank=True)
    dados_almoco = models.JSONField(null=True, blank=True)
    dados_lanche_da_tarde = models.JSONField(null=True, blank=True)
    dados_jantar = models.JSONField(null=True, blank=True)
    dados_lanche_da_noite = models.JSONField(null=True, blank=True)

    def __str__(self):
        return f'Relatorio rfeicoes {self.data.strftime("%d/%m/%Y")}'

    def save(self, *args, **kwargs):
        self.total_geral_pax = self.total_pax_adulto + self.total_pax_crianca + self.total_pax_monitoria
        super().save(*args, **kwargs)
