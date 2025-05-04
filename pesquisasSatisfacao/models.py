from django import forms
from django.contrib.auth.models import User
from django.contrib.postgres.fields import ArrayField
from django.core.exceptions import ValidationError
from django.db import models

from ordemDeServico.models import OrdemDeServico
from peraltas.models import EscalaAcampamento, Monitor


# Model abstrato que é estendido por todas as pesqusas de satisfação
class PesquisaDeSatisfacao(models.Model):
    sim_nao_choices = (
        (False, 'Não'),
        (True, 'Sim')
    )

    choices_avaliacoes = (
        (1, 'Ruim'),
        (2, 'Regular'),
        (3, 'Bom'),
        (4, 'Ótimo'),
        (5, 'Excelente'),
    )

    ordem_de_servico = models.ForeignKey(OrdemDeServico, on_delete=models.PROTECT)
    escala_peraltas = models.ForeignKey(EscalaAcampamento, on_delete=models.PROTECT)
    data_hora_resposta = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True

    def validate_obs_required(self, field_pairs):
        """
        Valida campos onde observação é obrigatória para avaliações Regular/Ruim
        Args:
            field_pairs: Lista de tuplas no formato (campo_avaliacao, campo_observacao)
        """
        errors = {}

        for campo_avaliacao, campo_obs in field_pairs:
            try:
                avaliacao = getattr(self, campo_avaliacao)
                observacao = getattr(self, campo_obs)

                if isinstance(avaliacao, models.IntegerField):
                    if avaliacao in [1, 2] and not observacao:
                        errors[campo_obs] = 'Observação obrigatória para avaliações "Regular" ou "Ruim"'
                else:
                    if not avaliacao and not observacao:
                        errors[campo_obs] = 'Observação obrigatória para resposta "Não"'

            except AttributeError:
                continue  # Ignora campos inexistentes

        if errors:
            raise ValidationError(errors)


# ----------------------------------------- Coordenação -> Equipe de monitoria -----------------------------------------
class CoordenacaoAvaliandoMonitoria(PesquisaDeSatisfacao):
    coordenador = models.ForeignKey(User, on_delete=models.CASCADE)
    # Pergunta 1 está no model AvaliacaoIndividualMonitor abaixo, será tratado separadamente

    # Pergunta 2 - Desta nas atividades (Ordenado do melhor para o pior)
    monitores_destaque_atividades = models.ManyToManyField(
        Monitor,
        through='DestaqueAtividades',
        related_name='avaliacoes_destaque_atividades',
        blank=True
    )

    # Pergunta 3 - Observações sobre a equipe
    observacoes_equipe = models.TextField()

    # Pergunta 4 - Captação de orientações
    captou_orientacoes = models.BooleanField(choices=PesquisaDeSatisfacao.sim_nao_choices)
    captou_orientacoes_obs = models.TextField(blank=True)

    # Pergunta 5 - Pontualidade na chegada
    pontualidade_chegada = models.IntegerField(choices=PesquisaDeSatisfacao.choices_avaliacoes)
    pontualidade_chegada_obs = models.TextField(blank=True)

    # Pergunta 6 - Pontualidade nas atividades
    pontualidade_atividades = models.IntegerField(choices=PesquisaDeSatisfacao.choices_avaliacoes)
    pontualidade_atividades_obs = models.TextField(blank=True)

    # Pergunta 7 - Programação aplicada
    programacao_aplicada = models.IntegerField(choices=PesquisaDeSatisfacao.choices_avaliacoes)
    programacao_aplicada_obs = models.TextField(blank=True)

    # Pergunta 8 - Seguiu a programação
    seguiu_programacao = models.IntegerField(choices=PesquisaDeSatisfacao.choices_avaliacoes)
    seguiu_programacao_obs = models.TextField(blank=True)

    # Pergunta 9 - Cuidados com materiais
    cuidados_materiais = models.IntegerField(choices=PesquisaDeSatisfacao.choices_avaliacoes)
    cuidados_materiais_obs = models.TextField(blank=True)

    # Pergunta 10 - Iniciativa e empenho
    iniciativa_empenho = models.BooleanField(choices=PesquisaDeSatisfacao.sim_nao_choices)
    iniciativa_empenho_obs = models.TextField(blank=True)

    # Pergunta 11 - Monitores destacados em atividades pedagógicas
    monitores_destaque_pedagogicas = models.ManyToManyField(
        Monitor,
        related_name='avaliacoes_destaque_pedagogicas',
        blank=True
    )

    # Pergunta 12 - Monitores com destaque no evento
    monitores_destaque_evento = models.ManyToManyField(
        Monitor,
        related_name='avaliacoes_destaque_evento',
        blank=True
    )

    # Pergunta 13 - 5 palavras para descrever o serviço
    palavras_descricao = ArrayField(
        models.CharField(max_length=30),
        size=5,
        blank=True,
        default=list
    )

    # Pergunta 14 - Monitores com desempenho acima da média
    monitores_acima_media = models.ManyToManyField(
        Monitor,
        through='DesempenhoAcimaMedia',
        related_name='avaliacoes_acima_media',
        blank=True
    )

    def __str__(self):
        return f"Avaliação da equipe de monitoria por {self.coordenador}"

    def clean(self):
        super().clean()
        self.validate_obs_required([
            ('captou_orientacoes', 'captou_orientacoes_obs'),
            ('pontualidade_chegada', 'pontualidade_chegada_obs'),
            ('pontualidade_atividades', 'pontualidade_atividades_obs'),
            ('programacao_aplicada', 'programacao_aplicada_obs'),
            ('seguiu_programacao', 'seguiu_programacao_obs'),
            ('cuidados_materiais', 'cuidados_materiais_obs'),
            ('iniciativa_empenho', 'iniciativa_empenho_obs'),
        ])


class AvaliacaoIndividualMonitor(models.Model):
    avaliacao_geral = models.ForeignKey(
        CoordenacaoAvaliandoMonitoria,
        on_delete=models.CASCADE,
        related_name='avaliacoes_individuais'
    )
    monitor = models.ForeignKey(Monitor, on_delete=models.CASCADE)
    avaliacao = models.IntegerField(choices=PesquisaDeSatisfacao.choices_avaliacoes)
    observacao = models.TextField(blank=True, null=True)

    class Meta:
        unique_together = ('avaliacao_geral', 'monitor')

    def __str__(self):
        return f"Avaliação de {self.monitor} em {self.avaliacao_geral}"


class DestaqueAtividades(models.Model):
    avaliacao = models.ForeignKey(CoordenacaoAvaliandoMonitoria, on_delete=models.CASCADE)
    monitor = models.ForeignKey(Monitor, on_delete=models.CASCADE)
    posicao = models.PositiveIntegerField()  # Ordem de destaque (1 = mais destacado, 2 = segundo, etc.)

    class Meta:
        ordering = ['posicao']  # Garante que a ordem seja mantida nas consultas
        unique_together = ('avaliacao', 'monitor')  # Evita duplicatas

    def __str__(self):
        return f"{self.posicao}º - {self.monitor.usuario.get_full_name()}"


class DesempenhoAcimaMedia(models.Model):
    avaliacao = models.ForeignKey(CoordenacaoAvaliandoMonitoria, on_delete=models.CASCADE)
    monitor = models.ForeignKey(Monitor, on_delete=models.CASCADE)
    posicao = models.PositiveIntegerField()  # Ordem de desempenho

    class Meta:
        ordering = ['posicao']
        unique_together = ('avaliacao', 'monitor')


# ----------------------------------------------------------------------------------------------------------------------
# ------------------------------------ Equipe de monitoria -> Coordenação ----------------------------------------------
class MonitorAvaliandoCoordenacao(PesquisaDeSatisfacao):
    monitor = models.ForeignKey(User, on_delete=models.CASCADE)
    # Sessão 2 - Avaliação da coordenação
    # Pergunta 1 - Avaliação dos coordenadores (será tratada em model separado)

    # Pergunta 2 - Pontualidade na chegada
    pontualidade_chegada = models.IntegerField(choices=PesquisaDeSatisfacao.choices_avaliacoes)
    pontualidade_chegada_obs = models.TextField(blank=True)

    # Pergunta 3 - Pontualidade nas atividades
    pontualidade_atividades = models.IntegerField(choices=PesquisaDeSatisfacao.choices_avaliacoes)
    pontualidade_atividades_obs = models.TextField(blank=True)

    # Pergunta 4 - Cuidados com materiais
    cuidados_materiais = models.IntegerField(choices=PesquisaDeSatisfacao.choices_avaliacoes)
    cuidados_materiais_obs = models.TextField(blank=True)

    # Pergunta 5 - Desenvoltura com a equipe
    desenvoltura_equipe = models.IntegerField(choices=PesquisaDeSatisfacao.choices_avaliacoes)
    desenvoltura_equipe_obs = models.TextField(blank=True)

    # Pergunta 6 - Organização do evento
    organizacao_evento = models.IntegerField(choices=PesquisaDeSatisfacao.choices_avaliacoes)
    organizacao_evento_obs = models.TextField(blank=True)

    # Pergunta 7 - Programação aplicada
    programacao_aplicada = models.IntegerField(choices=PesquisaDeSatisfacao.choices_avaliacoes)
    programacao_aplicada_obs = models.TextField(blank=True)

    # Pergunta 8 - Seguiu a programação
    seguiu_programacao = models.IntegerField(choices=PesquisaDeSatisfacao.choices_avaliacoes)
    seguiu_programacao_obs = models.TextField(blank=True)

    # Pergunta 9 - Briefing prévio
    teve_briefing = models.BooleanField(choices=PesquisaDeSatisfacao.sim_nao_choices)
    briefing_obs = models.TextField(blank=True)

    # Pergunta 10 - Feedback final
    teve_feedback = models.BooleanField(choices=PesquisaDeSatisfacao.sim_nao_choices)
    feedback_obs = models.TextField(blank=True)

    # Pergunta 11 - Participação nas atividades
    coordenador_participou = models.BooleanField(choices=PesquisaDeSatisfacao.sim_nao_choices)
    participacao_obs = models.TextField(blank=True)

    # Pergunta 12 - Considerações sobre atividades pedagógicas
    tem_consideracoes_pedagogicas = models.BooleanField(choices=PesquisaDeSatisfacao.sim_nao_choices)
    consideracoes_pedagogicas = models.TextField(blank=True)

    # Pergunta 13 - Palavras-chave
    palavras_chave = ArrayField(
        models.CharField(max_length=30),
        size=5,
        blank=True,
        default=list
    )

    def __str__(self):
        return f"Avaliação de {self.monitor} para a equipe de coordenadores"

    def clean(self):
        super().clean()
        self.validate_obs_required([
            ('pontualidade_chegada', 'pontualidade_chegada_obs'),
            ('pontualidade_atividades', 'pontualidade_atividades_obs'),
            ('cuidados_materiais', 'cuidados_materiais_obs'),
            ('desenvolvimento_equipe', 'desenvolvimento_equipe_obs'),
            ('organizacao_evento', 'organizacao_evento_obs'),
            ('programacao_aplicada', 'programacao_aplicada_obs'),
            ('seguiu_programacao', 'seguiu_programacao_obs'),
            ('teve_briefing', 'briefing_obs'),
            ('teve_feedback', 'feedback_obs'),
            ('coordenador_participou', 'participacao_obs'),
            ('tem_consideracoes_pedagogicas', 'consideracoes_pedagogicas'),
        ])


class AvaliacaoIndividualCoordenador(models.Model):
    pesquisa = models.ForeignKey(MonitorAvaliandoCoordenacao, on_delete=models.CASCADE,
                                 related_name='avaliacoes_coordenadores')
    coordenador = models.ForeignKey(User, on_delete=models.PROTECT, related_name='avaliacoes_recebidas')
    avaliacao = models.IntegerField(choices=PesquisaDeSatisfacao.choices_avaliacoes)
    observacao = models.TextField(blank=True, null=True)

    class Meta:
        unique_together = ('pesquisa', 'coordenador')

    def __str__(self):
        return f"Avaliação de {self.coordenador} por {self.pesquisa.monitor}"


# ----------------------------------------------------------------------------------------------------------------------
# --------------------------------------------- Formulários ------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------

