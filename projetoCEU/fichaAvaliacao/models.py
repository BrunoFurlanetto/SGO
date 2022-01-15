from datetime import datetime

import django
from django import forms
from django.db import models
from django.forms import DateInput

from cadastro.models import Atividades, Professores


class FichaDeAvaliacao(models.Model):
    avaliacoes_choices = (
        ('', ''),
        ('Excelente', 'Excelente'),
        ('Ótimo', 'Ótimo'),
        ('Bom', 'Bom'),
        ('Regular', 'Regular'),
        ('Ruim', 'Ruim'))

    instituicao = models.CharField(max_length=400, blank=True, null=True)
    cidade = models.CharField(max_length=300)
    n_alunos = models.IntegerField(default=0)
    n_educadores = models.IntegerField(default=0)
    serie = models.CharField(max_length=300)
    nome_educador_1 = models.CharField(max_length=400)
    cargo_educador_1 = models.CharField(max_length=400)
    email_educador_1 = models.EmailField()
    nome_educador_2 = models.CharField(max_length=400, blank=True, null=True)
    cargo_educador_2 = models.CharField(max_length=400, blank=True, null=True)
    email_educador_2 = models.EmailField(blank=True, null=True)
    nome_vendedor = models.CharField(max_length=400, blank=True, null=True)
    avaliacao_vendedor = models.CharField(max_length=10, choices=avaliacoes_choices, blank=True, null=True)
    justificativa_avaliacao_vendedor = models.TextField(max_length=300, blank=True)

    # --------------------------- Campos para a atividade 1 -------------------------------------
    data_atividade_1 = models.DateField(default=django.utils.timezone.now, blank=True, null=True)
    atividade_1 = models.ForeignKey(Atividades, on_delete=models.DO_NOTHING, related_name='avaliacao_atividade_1',
                                    blank=True, null=True)
    avaliacao_atividade_1 = models.CharField(max_length=10, choices=avaliacoes_choices)

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

    # --------------------------- Campos para a atividade 5 -------------------------------------
    data_atividade_5 = models.DateField(blank=True, null=True)
    atividade_5 = models.ForeignKey(Atividades, on_delete=models.DO_NOTHING, blank=True,
                                    null=True, related_name='avaliacao_atividade_5')
    avaliacao_atividade_5 = models.CharField(max_length=10, choices=avaliacoes_choices, blank=True, null=True)

    # --------------------------- Campos para a atividade 6 -------------------------------------
    data_atividade_6 = models.DateField(blank=True, null=True)
    atividade_6 = models.ForeignKey(Atividades, on_delete=models.DO_NOTHING, blank=True,
                                    null=True, related_name='avaliacao_atividade_6')
    avaliacao_atividade_6 = models.CharField(max_length=10, choices=avaliacoes_choices, blank=True, null=True)

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
    justificativa_avaliacao_atividades = models.TextField(max_length=400, blank=True)

    # --------------------- Campos para as avaliações dos professores do CEU -----------------------------
    professor_1 = models.ForeignKey(Professores, on_delete=models.DO_NOTHING, related_name='avaliacao_professor_1',
                                    blank=True, null=True)
    avaliacao_professor_1 = models.CharField(max_length=10, choices=avaliacoes_choices, blank=True)

    professor_2 = models.ForeignKey(Professores, on_delete=models.DO_NOTHING, related_name='avaliacao_professor_2',
                                    blank=True, null=True)
    avaliacao_professor_2 = models.CharField(max_length=10, choices=avaliacoes_choices, blank=True)

    professor_3 = models.ForeignKey(Professores, on_delete=models.DO_NOTHING, related_name='avaliacao_professor_3',
                                    blank=True, null=True)
    avaliacao_professor_3 = models.CharField(max_length=10, choices=avaliacoes_choices, blank=True)

    professor_4 = models.ForeignKey(Professores, on_delete=models.DO_NOTHING, related_name='avaliacao_professor_4',
                                    blank=True, null=True)
    avaliacao_professor_4 = models.CharField(max_length=10, choices=avaliacoes_choices, blank=True)

    professor_5 = models.ForeignKey(Professores, on_delete=models.DO_NOTHING, related_name='avaliacao_professor_5',
                                    blank=True, null=True)
    avaliacao_professor_5 = models.CharField(max_length=10, choices=avaliacoes_choices, blank=True)

    professor_6 = models.ForeignKey(Professores, on_delete=models.DO_NOTHING, related_name='avaliacao_professor_6',
                                    blank=True, null=True)
    avaliacao_professor_6 = models.CharField(max_length=10, choices=avaliacoes_choices, blank=True)

    justificativa_avaliacao_professores = models.TextField(max_length=400, blank=True)

    # ------------------------------- Campos da avaliação geral -----------------------------------
    motivo_trazer_grupo = models.TextField(max_length=400, blank=True)
    avaliacao_conteudo_pedagogico = models.CharField(max_length=10, choices=avaliacoes_choices)
    limpeza_instalacoes = models.CharField(max_length=10, choices=avaliacoes_choices)
    estado_jardim = models.CharField(max_length=10, choices=avaliacoes_choices)
    observacoes = models.TextField(max_length=400, blank=True)
    data_preenchimento = models.DateField(default=django.utils.timezone.now, blank=True, null=True)


class FichaDeAvaliacaoForm(forms.ModelForm):
    class Meta:
        model = FichaDeAvaliacao
        exclude = ()
        widgets = {
            'instituicao': forms.TextInput(attrs={'readolny': 'readonly'}),
            'cidade': forms.TextInput(attrs={'placeholder': 'Cidade'}),
            'nome_educador_1': forms.TextInput(attrs={'placeholder': 'Nome'}),
            'cargo_educador_1': forms.TextInput(attrs={'placeholder': 'Cargo'}),
            'email_educador_1': forms.TextInput(attrs={'placeholder': 'Email'}),
            'nome_educador_2': forms.TextInput(attrs={'placeholder': 'Nome'}),
            'cargo_educador_2': forms.TextInput(attrs={'placeholder': 'Cargo'}),
            'email_educador_2': forms.TextInput(attrs={'placeholder': 'Email'}),
             'atividade_1': forms.TextInput(), 'atividade_2': forms.TextInput(),
            'atividade_3': forms.TextInput(), 'atividade_4': forms.TextInput(),
            'atividade_5': forms.TextInput(), 'atividade_6': forms.TextInput(),
            'atividade_7': forms.TextInput(), 'atividade_8': forms.TextInput(),
            'professor_1': forms.TextInput(), 'professor_2': forms.TextInput(),
            'professor_3': forms.TextInput(), 'professor_4': forms.TextInput(),
            'professor_5': forms.TextInput(), 'professor_6': forms.TextInput(),
            'data_atividade_1': forms.DateTimeInput(attrs={'type': 'date'}),
            'data_atividade_2': forms.DateTimeInput(attrs={'type': 'date'}),
            'data_atividade_3': forms.DateTimeInput(attrs={'type': 'date'}),
            'data_atividade_4': forms.DateTimeInput(attrs={'type': 'date'}),
            'data_atividade_5': forms.DateTimeInput(attrs={'type': 'date'}),
            'data_atividade_6': forms.DateTimeInput(attrs={'type': 'date'}),
            'data_atividade_7': forms.DateTimeInput(attrs={'type': 'date'}),
            'data_atividade_8': forms.DateTimeInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['instituicao'].disabled = True
        self.fields['atividade_1'].disabled = True
        self.fields['data_atividade_1'].disabled = True
        self.fields['atividade_2'].disabled = True
        self.fields['data_atividade_2'].disabled = True
        self.fields['atividade_3'].disabled = True
        self.fields['data_atividade_3'].disabled = True
        self.fields['atividade_4'].disabled = True
        self.fields['data_atividade_4'].disabled = True
        self.fields['atividade_5'].disabled = True
        self.fields['data_atividade_5'].disabled = True
        self.fields['atividade_6'].disabled = True
        self.fields['data_atividade_6'].disabled = True
        self.fields['atividade_7'].disabled = True
        self.fields['data_atividade_7'].disabled = True
        self.fields['atividade_8'].disabled = True
        self.fields['data_atividade_8'].disabled = True
        self.fields['professor_1'].disabled = True
        self.fields['professor_2'].disabled = True
        self.fields['professor_3'].disabled = True
        self.fields['professor_4'].disabled = True
        self.fields['professor_5'].disabled = True
        self.fields['professor_6'].disabled = True
