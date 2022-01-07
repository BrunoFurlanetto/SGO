from django.db import models
from cadastro.models import Atividades, Professores


class FichaDeAvaliacao(models.Model):
    avaliacoes_choices = (
        (5, 'excelente'),
        (4, 'Ótimo'),
        (3, 'Bom'),
        (2, 'Regular'),
        (1, 'Ruim'))

    instituicao = models.CharField(max_length=400)
    cidade = models.CharField(max_length=300)
    n_alunos = models.CharField(max_length=4)
    n_educadores = models.CharField(max_length=4)
    serie = models.CharField(max_length=300)
    nome_educador_1 = models.CharField(max_length=400)
    cargo_educador_1 = models.CharField(max_length=400)
    email_educador_1 = models.EmailField()
    nome_educador_2 = models.CharField(max_length=400, blank=True, null=True)
    cargo_educador_2 = models.CharField(max_length=400, blank=True, null=True)
    email_educador_2 = models.EmailField(blank=True, null=True)
    nome_vendedor = models.CharField(max_length=400, blank=True, null=True)
    avaliacao_vendedor = models.CharField(max_length=10, choices=avaliacoes_choices, blank=True, null=True)
    justificativa_avaliacao_vendedor = models.TextField(max_length=300)

    # --------------------------- Campos para a atividade 1 -------------------------------------
    data_atividade_1 = models.DateField()
    atividade_1 = models.ForeignKey(Atividades, on_delete=models.DO_NOTHING,
                                    default='', related_name='avaliacao_atividade_1')
    avaliacao_atividade_1 = models.CharField(max_length=10, choices=avaliacoes_choices, default='')

    # --------------------------- Campos para a atividade 2 -------------------------------------
    data_atividade_2 = models.DateField(blank=True, null=True)
    atividade_2 = models.ForeignKey(Atividades, on_delete=models.DO_NOTHING, blank=True,
                                    null=True, related_name='avaliacao_atividade_2')
    avaliacao_atividade_2 = models.CharField(max_length=10, choices=avaliacoes_choices, blank=True, null=True)

    # --------------------------- Campos para a atividade 3 -------------------------------------
    data_atividade_3 = models.DateField(blank=True, null=True)
    atividade_3 = models.ForeignKey(Atividades, on_delete=models.DO_NOTHING, blank=True,
                                    null=True, related_name='avaliacao_atividade_3')
    avaliacao_atividade_3 = models.CharField(max_length=10, choices=avaliacoes_choices, blank=True, null=True)

    # --------------------------- Campos para a atividade 4 -------------------------------------
    data_atividade_4 = models.DateField(blank=True, null=True)
    atividade_4 = models.ForeignKey(Atividades, on_delete=models.DO_NOTHING, blank=True,
                                    null=True, related_name='avaliacao_atividade_4')
    avaliacao_atividade_4 = models.CharField(max_length=10, choices=avaliacoes_choices, blank=True, null=True)

    # --------------------------- Campos para a atividade 6 -------------------------------------
    data_atividade_5 = models.DateField(blank=True, null=True)
    atividade_5 = models.ForeignKey(Atividades, on_delete=models.DO_NOTHING, blank=True,
                                    null=True, related_name='avaliacao_atividade_5')
    avaliacao_atividade_5 = models.CharField(max_length=10, choices=avaliacoes_choices, blank=True, null=True)

    # --------------------------- Campos para a atividade 7 -------------------------------------
    data_atividade_7 = models.DateField(blank=True, null=True)
    atividade_7 = models.ForeignKey(Atividades, on_delete=models.DO_NOTHING, blank=True,
                                    null=True, related_name='avaliacao_atividade_7')
    avaliacao_atividade_7 = models.CharField(max_length=10, choices=avaliacoes_choices, blank=True, null=True)

    # --------------------------- Campos para a atividade 8 -------------------------------------
    data_atividade_8 = models.DateField(blank=True, null=True)
    atividade_8 = models.ForeignKey(Atividades, on_delete=models.DO_NOTHING, blank=True,
                                    null=True, related_name='avaliacao_atividade_8')
    avaliacao_atividade_8 = models.CharField(max_length=10, choices=avaliacoes_choices, blank=True, null=True)
    justificativa_avaliacao_atividades = models.TextField(max_length=400)

    # --------------------- Campos para as avaliações dos professores do CEU -----------------------------
    professor_1 = models.ForeignKey(Professores, on_delete=models.DO_NOTHING, related_name='avaliacao_professor_1')
    avaliacao_professor_1 = models.CharField(max_length=10, choices=avaliacoes_choices)
    professor_2 = models.ForeignKey(Professores, on_delete=models.DO_NOTHING, related_name='avaliacao_professor_2')
    avaliacao_professor_2 = models.CharField(max_length=10, choices=avaliacoes_choices)
    professor_3 = models.ForeignKey(Professores, on_delete=models.DO_NOTHING, related_name='avaliacao_professor_3')
    avaliacao_professor_3 = models.CharField(max_length=10, choices=avaliacoes_choices)
    professor_4 = models.ForeignKey(Professores, on_delete=models.DO_NOTHING, related_name='avaliacao_professor_4')
    avaliacao_professor_4 = models.CharField(max_length=10, choices=avaliacoes_choices)
    professor_5 = models.ForeignKey(Professores, on_delete=models.DO_NOTHING, related_name='avaliacao_professor_5')
    avaliacao_professor_5 = models.CharField(max_length=10, choices=avaliacoes_choices)
    professor_6 = models.ForeignKey(Professores, on_delete=models.DO_NOTHING, related_name='avaliacao_professor_6')
    avaliacao_professor_6 = models.CharField(max_length=10, choices=avaliacoes_choices)
    justificativa_avaliacao_professores = models.TextField(max_length=400)

    # ------------------------------- Campos da avaliação geral -----------------------------------
    motivo_trazer_grupo = models.TextField(max_length=400)
    avaliacao_conteudo_pedagogico = models.CharField(max_length=10, choices=avaliacoes_choices)
    limpeza_instalacoes = models.CharField(max_length=10, choices=avaliacoes_choices)
    estado_jardim = models.CharField(max_length=10, choices=avaliacoes_choices)
    observacoes = models.CharField(max_length=400)
    data_preenchimento = models.DateField()

    def __str__(self):
        return self.instituicao
