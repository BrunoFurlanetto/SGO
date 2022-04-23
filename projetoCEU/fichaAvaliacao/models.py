import django
from django import forms
from django.db import models
from django.utils import timezone

from cadastro.models import RelatorioDeAtendimentoColegioCeu
from ordemDeServico.models import OrdemDeServico
from peraltas.models import Responsavel, Vendedor


class FichaDeAvaliacao(models.Model):
    avaliacoes_choices = (
        (5, 'Excelente'),
        (4, 'Ótimo'),
        (3, 'Bom'),
        (2, 'Regular'),
        (1, 'Ruim'))

    instituicao = models.ForeignKey(RelatorioDeAtendimentoColegioCeu, on_delete=models.DO_NOTHING)
    cidade = models.CharField(max_length=255)
    n_alunos = models.IntegerField()
    n_professores = models.IntegerField()
    serie = models.CharField(max_length=255)
    nome_avaliador = models.ForeignKey(Responsavel, on_delete=models.DO_NOTHING)
    cargo_avaliador = models.CharField(max_length=255)
    email_avaliador = models.EmailField()
    nome_vendedor = models.ForeignKey(Vendedor, on_delete=models.DO_NOTHING)
    avaliacao_vendedor = models.JSONField(blank=True, null=True)
    avaliacoes_atividades = models.JSONField(blank=True, null=True)
    avaliacoes_professores = models.JSONField(blank=True, null=True)
    motivo_trazer_grupo = models.TextField(max_length=400, blank=True)
    avaliacao_conteudo_pedagogico = models.IntegerField(choices=avaliacoes_choices)
    limpeza_instalacoes = models.IntegerField(choices=avaliacoes_choices)
    observacoes = models.TextField(max_length=400, blank=True)
    data_preenchimento = models.DateField(default=timezone.now, blank=True, null=True)


class FichaDeAvaliacaoForm(forms.ModelForm):
    class Meta:
        model = FichaDeAvaliacao
        exclude = ()
        widgets = {}
