import json

from django import forms
from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.contrib.postgres.fields import ArrayField
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from ceu.models import Atividades
from ordemDeServico.models import OrdemDeServico
from peraltas.models import EscalaAcampamento, Monitor, Responsavel, AtividadesEco


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

    choices_retorno_grupo = (
        ('', '-----------'),
        ('primeiro_semestre', 'Sim - Primeiro semestre do ano seguinte'),
        ('segundo_semestre', 'Sim - Segundo semestre do ano seguinte'),
        ('daqui_dois_anos', f'Sim - Daqui dois anos'),
        ('talvez', 'Talvez'),
        ('nao', 'Não'),
    )

    ordem_de_servico = models.ForeignKey(OrdemDeServico, on_delete=models.PROTECT)
    escala_peraltas = models.ForeignKey(EscalaAcampamento, on_delete=models.PROTECT)
    data_hora_resposta = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True

    @classmethod
    def get_choices_dinamicos(cls):
        """Gera choices com anos atualizados para forms/templates."""
        ano_atual = timezone.now().year
        return (
            ('', '-----------'),
            ('primeiro_semestre', f'Sim - Primeiro semestre de {ano_atual + 1}'),
            ('segundo_semestre', f'Sim - Segundo semestre de {ano_atual + 1}'),
            ('daqui_dois_anos', f'Sim - {ano_atual + 2}'),
            ('talvez', 'Talvez'),
            ('nao', 'Não'),
        )

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


class AvaliacaoIndividualCoordenador(models.Model):
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()  # Armazena o ID do modelo relacionado
    pesquisa = GenericForeignKey('content_type', 'object_id')  # Nome mantido para compatibilidade
    coordenador = models.ForeignKey(Monitor, on_delete=models.PROTECT, related_name='avaliacoes_recebidas')
    avaliacao = models.IntegerField(choices=PesquisaDeSatisfacao.choices_avaliacoes)
    observacao = models.TextField(blank=True, null=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['content_type', 'object_id', 'coordenador'],
                name='avaliacao_unica_por_coordenador'
            ),
        ]

    def __str__(self):
        return f"Avaliação de {self.coordenador} por {self.pesquisa.monitor}"


class AvaliacaoIndividualAtividade(models.Model):
    pesquisa_content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        related_name='pesquisa_avaliacoes'
    )
    pesquisa_object_id = models.PositiveIntegerField()
    pesquisa = GenericForeignKey('pesquisa_content_type', 'pesquisa_object_id')
    atividade_content_type = models.ForeignKey(
        ContentType,
        on_delete=models.PROTECT,
        related_name='atividade_avaliacoes'
    )
    atividade_object_id = models.PositiveIntegerField()
    atividade = GenericForeignKey('atividade_content_type', 'atividade_object_id')
    avaliacao = models.IntegerField(choices=PesquisaDeSatisfacao.choices_avaliacoes)
    observacao = models.TextField(blank=True, null=True)

    class Meta:
        indexes = [
            models.Index(fields=['pesquisa_content_type', 'pesquisa_object_id']),
            models.Index(fields=['atividade_content_type', 'atividade_object_id']),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['pesquisa_content_type', 'pesquisa_object_id', 'atividade_content_type',
                        'atividade_object_id'],
                name='avaliacao_unica_por_atividade'
            ),
        ]

    @classmethod
    def get_all_atividades(cls):
        """Retorna todas as atividades de todos os tipos"""
        atividades = []

        # Adiciona AtividadesEco
        ct_eco = ContentType.objects.get_for_model(AtividadesEco)
        for atv in AtividadesEco.objects.all():
            atividades.append({
                'id': atv.id,
                'content_type_id': ct_eco.id,
                'nome': str(atv),
                'tipo': 'ECO'
            })

        # Adiciona AtividadesCeu
        ct_ceu = ContentType.objects.get_for_model(Atividades)
        for atv in Atividades.objects.all():
            atividades.append({
                'id': atv.id,
                'content_type_id': ct_ceu.id,
                'nome': str(atv),
                'tipo': 'CEU'
            })

        return atividades

    @staticmethod
    def process_atividades(json_field, model):
        atividades = json_field or {}

        return [
            {
                'atividade_content_type': ContentType.objects.get_for_model(model).id,
                'atividade_object_id': info['atividade']
            }
            for info in atividades.values()
            if info.get('atividade')
        ]

    def __str__(self):
        return f"Avaliação de {self.atividade} por {self.pesquisa}"


class AvaliacaoIndividualSala(models.Model):
    pesquisa_corporativo_content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        related_name='pesquisa_corporativo_avaliacoes'
    )
    pesquisa_corporativo_object_id = models.PositiveIntegerField()
    pesquisa = GenericForeignKey('pesquisa_corporativo_content_type', 'pesquisa_corporativo_object_id')
    sala_content_type = models.ForeignKey(
        ContentType,
        on_delete=models.PROTECT,
        related_name='sala_avaliacoes'
    )
    sala_object_id = models.PositiveIntegerField()
    sala = GenericForeignKey('sala_content_type', 'sala_object_id')
    avaliacao = models.IntegerField(choices=PesquisaDeSatisfacao.choices_avaliacoes)
    observacao = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Avaliação de {self.sala} por {self.pesquisa.avaliador}"


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
    observacoes_equipe = models.TextField(help_text='Conte um pouco sobre a sinergia da equipe perante o evento')

    # Pergunta 4 - Captação de orientações
    captou_orientacoes = models.BooleanField(
        choices=PesquisaDeSatisfacao.sim_nao_choices,
        verbose_name='A equipe captou todas as orientações passadas durante o evento?'
    )
    captou_orientacoes_obs = models.TextField(blank=True)

    # Pergunta 5 - Pontualidade na chegada
    pontualidade_chegada = models.IntegerField(
        choices=PesquisaDeSatisfacao.choices_avaliacoes,
        verbose_name='Pontualidade da equipe como um todo na chegada'
    )
    pontualidade_chegada_obs = models.TextField(blank=True)

    # Pergunta 6 - Pontualidade nas atividades
    pontualidade_atividades = models.IntegerField(
        choices=PesquisaDeSatisfacao.choices_avaliacoes,
        verbose_name='Pontualidade nas atividades'
    )
    pontualidade_atividades_obs = models.TextField(blank=True)

    # Pergunta 7 - Programação aplicada
    programacao_aplicada = models.IntegerField(choices=PesquisaDeSatisfacao.choices_avaliacoes)
    programacao_aplicada_obs = models.TextField(blank=True)

    # Pergunta 8 - Seguiu a programação
    seguiu_programacao = models.IntegerField(
        choices=PesquisaDeSatisfacao.choices_avaliacoes,
        verbose_name='Seguiu a Programação proposta para o período?'
    )
    seguiu_programacao_obs = models.TextField(blank=True)

    # Pergunta 9 - Cuidados com materiais
    cuidados_materiais = models.IntegerField(
        choices=PesquisaDeSatisfacao.choices_avaliacoes,
        verbose_name='Cuidados com os materiais da empresa - Equipe como um todo.'
    )
    cuidados_materiais_obs = models.TextField(blank=True)

    # Pergunta 10 - Iniciativa e empenho
    iniciativa_empenho = models.BooleanField(
        choices=PesquisaDeSatisfacao.sim_nao_choices,
        verbose_name='A equipe demonstrou iniciativa e empenho no trabalho realizado?'
    )
    iniciativa_empenho_obs = models.TextField(blank=True)

    # Pergunta 11 - Monitores destacados em atividades pedagógicas
    monitores_destaque_pedagogicas = models.ManyToManyField(
        Monitor,
        related_name='avaliacoes_destaque_pedagogicas',
        blank=True,
        verbose_name='Algum monitor se destacou durante as atividades pedagógicas?'
    )

    # Pergunta 12 - Monitores com destaque no evento
    monitores_destaque_evento = models.ManyToManyField(
        Monitor,
        related_name='avaliacoes_destaque_evento',
        blank=True,
        verbose_name='Algum monitor teve destaque no evento em questão?'
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
    pontualidade_chegada = models.IntegerField(
        choices=PesquisaDeSatisfacao.choices_avaliacoes,
        verbose_name='Pontualidade na chegada (dos coordenadores)'
    )
    pontualidade_chegada_obs = models.TextField(blank=True)

    # Pergunta 3 - Pontualidade nas atividades
    pontualidade_atividades = models.IntegerField(
        choices=PesquisaDeSatisfacao.choices_avaliacoes,
        verbose_name='Pontualidade nas atividades'
    )
    pontualidade_atividades_obs = models.TextField(blank=True)

    # Pergunta 4 - Cuidados com materiais
    cuidados_materiais = models.IntegerField(
        choices=PesquisaDeSatisfacao.choices_avaliacoes,
        verbose_name='Cuidado com os materiais da empresa'
    )
    cuidados_materiais_obs = models.TextField(blank=True)

    # Pergunta 5 - Desenvoltura com a equipe
    desenvoltura_equipe = models.IntegerField(
        choices=PesquisaDeSatisfacao.choices_avaliacoes,
        verbose_name='Desenvoltura com a equipe de monitoria'
    )
    desenvoltura_equipe_obs = models.TextField(blank=True)

    # Pergunta 6 - Organização do evento
    organizacao_evento = models.IntegerField(
        choices=PesquisaDeSatisfacao.choices_avaliacoes,
        verbose_name='Organização do evento como um todo'
    )
    organizacao_evento_obs = models.TextField(blank=True)

    # Pergunta 7 - Programação aplicada
    programacao_aplicada = models.IntegerField(choices=PesquisaDeSatisfacao.choices_avaliacoes)
    programacao_aplicada_obs = models.TextField(blank=True)

    # Pergunta 8 - Seguiu a programação
    seguiu_programacao = models.IntegerField(
        choices=PesquisaDeSatisfacao.choices_avaliacoes,
        verbose_name='Seguiu a Programação proposta para o período?'
    )
    seguiu_programacao_obs = models.TextField(blank=True)

    # Pergunta 9 - Briefing prévio
    teve_briefing = models.BooleanField(
        choices=PesquisaDeSatisfacao.sim_nao_choices,
        verbose_name='Teve briefing prévio ao evento? Foram passadas todas as informações necessárias para o evento no briefing inicial?'
    )

    # Pergunta 10 - Feedback final
    teve_feedback = models.BooleanField(
        choices=PesquisaDeSatisfacao.sim_nao_choices,
        verbose_name='O coordenador deu feedback para a equipe no final do evento?'
    )

    # Pergunta 11 - Participação nas atividades
    coordenador_participou = models.BooleanField(
        choices=PesquisaDeSatisfacao.sim_nao_choices,
        verbose_name='Os coordenadores participaram das atividades?'
    )

    # Pergunta 12 - Considerações sobre atividades pedagógicas
    tem_consideracoes_pedagogicas = models.TextField(
        blank=True,
        verbose_name='Tem alguma consideração sobre as atividades pedagógicas propostas?'
    )

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
        ])


# ----------------------------------------------------------------------------------------------------------------------
# ------------------------------------------- Avaliação colégio --------------------------------------------------------
class OpcoesMotivacao(models.Model):
    motivo = models.CharField(max_length=100)

    def __str__(self):
        return self.motivo


class AvaliacaoColegio(PesquisaDeSatisfacao):
    avaliador = models.ForeignKey(Responsavel, on_delete=models.PROTECT)

    # Pergunta 1
    processo_vendas = models.IntegerField(
        choices=PesquisaDeSatisfacao.choices_avaliacoes,
        verbose_name='Comente sobre o processo de vendas'
    )
    processo_vendas_obs = models.TextField(blank=True)

    # Pergunta 2
    transporte_utilizado = models.IntegerField(
        choices=PesquisaDeSatisfacao.choices_avaliacoes,
        verbose_name='Comente sobre o transporte utilizado'
    )
    transporte_utilizado_obs = models.TextField(blank=True)

    # Pergunta 3 -  Avaliação dos coordenadores (será tratada em model separado)
    # Pergunta 4
    equipe_monitoria = models.IntegerField(
        choices=PesquisaDeSatisfacao.choices_avaliacoes,
        verbose_name='Comente sobre o equipe de monitores como um todo'
    )
    equipe_monitoria_obs = models.TextField(blank=True)

    # Pergunta 5
    atendimento_enfermeira = models.IntegerField(
        choices=PesquisaDeSatisfacao.choices_avaliacoes,
        verbose_name='Avalie o atendimento de enfermeira durante o evento'
    )
    atendimento_enfermeira_obs = models.TextField(blank=True)

    # Pergunta 6
    atividades_recreativas = models.IntegerField(
        choices=PesquisaDeSatisfacao.choices_avaliacoes,
        verbose_name='Avalie as atividades recreativas propostas pela monitoria'
    )
    atividades_recreativas_obs = models.TextField(blank=True)

    # Pergunta 7
    cafe_manha = models.IntegerField(
        choices=PesquisaDeSatisfacao.choices_avaliacoes,
        verbose_name='Comente sobre o café da manhã',
        blank=True, null=True
    )
    cafe_manha_obs = models.TextField(blank=True)

    # Pergunta 8
    almoco = models.IntegerField(
        choices=PesquisaDeSatisfacao.choices_avaliacoes,
        verbose_name='Comente sobre o almoco',
        blank=True, null=True
    )
    almoco_obs = models.TextField(blank=True)

    # Pergunta 9
    jantar = models.IntegerField(
        choices=PesquisaDeSatisfacao.choices_avaliacoes,
        verbose_name='Comente sobre o jantar',
        blank=True, null=True
    )
    jantar_obs = models.TextField(blank=True)

    # Pergunta 10
    lanche_noite = models.IntegerField(
        choices=PesquisaDeSatisfacao.choices_avaliacoes,
        verbose_name='Comente sobre o lanche da noite',
        blank=True, null=True
    )
    lanche_noite_obs = models.TextField(blank=True)

    # Pergunta 11
    estrutura_geral = models.IntegerField(
        choices=PesquisaDeSatisfacao.choices_avaliacoes,
        verbose_name='Comente sobre o estrutura em geral',
    )
    estrutura_geral_obs = models.TextField(blank=True)

    # Pergunta 12
    quartos = models.IntegerField(
        choices=PesquisaDeSatisfacao.choices_avaliacoes,
        verbose_name='Comente sobre a estrutura dos quartos',
    )
    quartos_obs = models.TextField(blank=True)

    # Pergunta 13
    piscina = models.IntegerField(
        choices=PesquisaDeSatisfacao.choices_avaliacoes,
        verbose_name='Comente sobre a estrutura da piscina',
    )
    piscina_obs = models.TextField(blank=True)

    # Pergunta 14 - Avaliação das atividades (será tratada em model separado)
    # Pergunta 15
    destaque = models.TextField()

    # Pergunta 16
    sugestoes = models.TextField(blank=True)

    # Pergunta 17
    motivo_trazer_grupo = models.ManyToManyField(OpcoesMotivacao)
    outros_motivos = models.TextField(blank=True)

    # Pergunta 18
    volta_proximo_ano = models.CharField(
        max_length=50,
        choices=PesquisaDeSatisfacao.choices_retorno_grupo,
    )
    volta_proximo_ano_obs = models.TextField(blank=True)

    # Pergunta 19
    material_divigulgacao = models.BooleanField(
        choices=PesquisaDeSatisfacao.sim_nao_choices,
        verbose_name='Quer receber material com as novidades e promoções para o próximo ano?'
    )

    # Pergunta 20
    interesse_hospedar_com_familia = models.BooleanField(
        choices=PesquisaDeSatisfacao.sim_nao_choices,
        verbose_name='Tem interesse em se hospedar com o familia?',
        help_text='Caso sim, temos descontos exclusivos para pedagogos.'
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._meta.get_field('volta_proximo_ano').verbose_name = (
            f'Faria outro evento aqui no Peraltas, em {timezone.now().year + 1}?'
        )


# ----------------------------------------------------------------------------------------------------------------------
# ------------------------------------------ Avaliação corporativo -----------------------------------------------------
class AvaliacaoCorporativo(PesquisaDeSatisfacao):
    avaliador = models.ForeignKey(Responsavel, models.PROTECT)

    # Pergunta 1 - Avaliações dos coordenadores será feito em outro model
    # Perguta 2
    equipe_monitoria = models.IntegerField(
        choices=PesquisaDeSatisfacao.choices_avaliacoes,
        verbose_name='Comente sobre o equipe de monitores como um todo'
    )
    equipe_monitoria_obs = models.TextField(blank=True)

    # Pergunta 3
    estrutura_ceu = models.IntegerField(
        choices=PesquisaDeSatisfacao.choices_avaliacoes,
        verbose_name='Comente sobre a estrutura do Centro de Estudos do Universo'
    )
    estrutura_ceu_obs = models.TextField(blank=True)

    # Pergunta 4 - Avaliações de sala será feita separadamente
    # Pergunta 5
    cafe_manha = models.IntegerField(
        choices=PesquisaDeSatisfacao.choices_avaliacoes,
        verbose_name='Comente sobre o café da manhã',
        blank=True, null=True
    )
    cafe_manha_obs = models.TextField(blank=True)

    # Pergunta 6
    coffee_break = models.IntegerField(
        choices=PesquisaDeSatisfacao.choices_avaliacoes,
        verbose_name='Comente sobre o coffee break',
    )
    coffee_break_obs = models.TextField(blank=True)

    # Pergunta 7
    almoco = models.IntegerField(
        choices=PesquisaDeSatisfacao.choices_avaliacoes,
        verbose_name='Comente sobre o almoco',
        blank=True, null=True
    )
    almoco_obs = models.TextField(blank=True)

    # Pergunta 8
    jantar = models.IntegerField(
        choices=PesquisaDeSatisfacao.choices_avaliacoes,
        verbose_name='Comente sobre o jantar',
        blank=True, null=True
    )
    jantar_obs = models.TextField(blank=True)

    # Pergunta 9
    estrutura_geral = models.IntegerField(
        choices=PesquisaDeSatisfacao.choices_avaliacoes,
        verbose_name='Comente sobre o estrutura em geral',
    )
    estrutura_geral_obs = models.TextField(blank=True)

    # Pergunta 10
    quartos = models.IntegerField(
        choices=PesquisaDeSatisfacao.choices_avaliacoes,
        verbose_name='Avalie a habitação que esteve hospedada',
    )
    quarto_obs = models.TextField(blank=True)

    # Pergunta 11
    atendimento_bar = models.IntegerField(
        choices=PesquisaDeSatisfacao.choices_avaliacoes,
        verbose_name='Comente sobre o atendimento do bar',
    )
    atendimento_obs = models.TextField(blank=True)

    # Pergunta 12
    mais_valorizou = models.TextField(verbose_name='O que você mais valorizou durante a sua estadia no Brotas eco?')

    # Pergunta 13
    sugestoes = models.TextField(blank=True, verbose_name='Sugestões para melhorias')

    # Pergeunta 14
    volta_proximo_ano = models.CharField(
        max_length=50,
        choices=PesquisaDeSatisfacao.choices_retorno_grupo,
    )
    volta_proximo_ano_obs = models.TextField(blank=True)

    # Perguta 15
    material_divigulgacao = models.BooleanField(
        choices=PesquisaDeSatisfacao.sim_nao_choices,
        verbose_name='Quer receber material com as novidades e promoções para o próximo ano?'
    )

    # Pergunta 16
    interesse_hospedar_com_familia = models.BooleanField(
        choices=PesquisaDeSatisfacao.sim_nao_choices,
        verbose_name='Tem interesse em trazer a sua família ao Brotas eco?',
        help_text='Caso a resposta seja sim, vamos gerar um cupom de desconto para você!'
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._meta.get_field('volta_proximo_ano').verbose_name = (
            f'Faria outro evento no Brotas ECO, em {timezone.now().year + 1}?'
        )
