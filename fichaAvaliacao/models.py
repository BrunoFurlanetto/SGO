from django import forms
from django.contrib.postgres.fields import JSONField
from django.db import models
from django.utils import timezone

from cadastro.models import RelatorioDeAtendimentoColegioCeu
from ordemDeServico.models import OrdemDeServico
from peraltas.models import Responsavel, Vendedor, ClienteColegio


class FichaDeAvaliacao(models.Model):
    avaliacoes_choices = (
        (5, 'Excelente'),
        (4, 'Ótimo'),
        (3, 'Bom'),
        (2, 'Regular'),
        (1, 'Ruim')
    )

    ordem_de_servico = models.ForeignKey(OrdemDeServico, on_delete=models.CASCADE)
    instituicao = models.ForeignKey(ClienteColegio, on_delete=models.DO_NOTHING)
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
    estado_conservacao = models.IntegerField(choices=avaliacoes_choices)
    o_que_quer_proxima = models.TextField(blank=True)
    observacoes = models.TextField(max_length=400, blank=True)
    data_preenchimento = models.DateField(default=timezone.now, blank=True, null=True)

    @staticmethod
    def dados_iniciais(ordem):
        return {
            'ordem_de_servico': ordem.id,
            'instituicao': ordem.ficha_de_evento.cliente.id,
            'cidade': ordem.ficha_de_evento.cliente.cidade,
            'n_alunos': ordem.n_participantes,
            'n_professores': ordem.n_professores,
            'serie': ordem.serie,
            'nome_avaliador': ordem.ficha_de_evento.responsavel_evento.id,
            'cargo_avaliador': ordem.ficha_de_evento.responsavel_evento.listar_cargos,
            'email_avaliador': ordem.ficha_de_evento.responsavel_evento.email_responsavel_evento,
            'nome_vendedor': ordem.vendedor,
        }

    def nota_vendedor(self):
        return self.avaliacao_vendedor


class FichaDeAvaliacaoForm(forms.ModelForm):
    class Meta:
        model = FichaDeAvaliacao
        exclude = ()
        widgets = {
            'cidade': forms.TextInput(attrs={'readonly': True}),
            'n_alunos': forms.NumberInput(attrs={'readonly': True}),
            'n_professores': forms.NumberInput(attrs={'readonly': True}),
            'serie': forms.TextInput(attrs={'readonly': True}),
            'cargo_avaliador': forms.TextInput(attrs={'readonly': True}),
            'email_avaliador': forms.TextInput(attrs={'readonly': True}),
            'avaliacao_conteudo_pedagogico': forms.Select(attrs={'class': 'avaliacao'}),
            'limpeza_instalacoes': forms.Select(attrs={'class': 'avaliacao'}),
            'estado_conservacao': forms.Select(attrs={'class': 'avaliacao'}),
        }
