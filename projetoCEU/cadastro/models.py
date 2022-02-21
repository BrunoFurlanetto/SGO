from django.contrib.auth.models import User
from django.db import models
from django import forms


class Professores(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    primeiro_nome = models.CharField(max_length=20)
    sobrenome = models.CharField(max_length=100)
    email = models.EmailField()
    telefone = models.CharField(max_length=11)
    diarista = models.BooleanField(default=False)
    nota = models.FloatField(default=0.00)

    def __str__(self):
        return self.usuario.first_name


class Tipo(models.Model):
    tipo = models.CharField(max_length=100)

    def __str__(self):
        return self.tipo


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


class RelatorioDeAtendimentoCeu(models.Model):
    tipo = models.ForeignKey(Tipo, on_delete=models.DO_NOTHING, blank=True, null=True)
    instituicao = models.CharField(max_length=255)
    participantes_previa = models.IntegerField()
    participantes_confirmados = models.IntegerField(default=participantes_previa, blank=True, null=True)
    responsaveis = models.IntegerField(blank=True, null=True)
    serie = models.CharField(max_length=100, blank=True)
    coordenador_peraltas = models.CharField(max_length=100, blank=True)
    equipe = models.JSONField()  # dict{'coordenador':, 'professor_2':, 'professor_3':, 'professor_4':}
    atividades = models.JSONField()  # dict{['atividade':, 'profs_ativ':[], 'data_hora_ativ':, 'n_participantes':]}
    locacoes = models.JSONField(blank=True, null=True)  # dict{['local':, 'profs_acompanhando':, 'data_hora_entrada':, 'data_hora_saida':,
    # 'soma_horas':, 'soma_horas_total':]}
    relatorio = models.TextField(max_length=400, default='Atividades realizadas com sucesso')
    solicitado = models.BooleanField(default=False)
    entregue = models.BooleanField(default=False)

    def __str__(self):
        return f'Relatório de {self.tipo}'


class OrdemDeServicoPublico(forms.ModelForm):
    class Meta:
        model = RelatorioDeAtendimentoCeu
        exclude = ('instituicao', 'responsaveis', 'serie', 'coordenador_peraltas',
                   'locacoes', 'solicitado', 'entregue')

        widgets = {'participantes_previa': forms.NumberInput(attrs={'placeholder': 'Prévia'}),
                   'participantes_confirmados': forms.NumberInput(attrs={'placeholder': 'Confirmados'}),
                   'data_atendimento': forms.DateTimeInput(attrs={'type': 'date'}),
                   }


class OrdemDeServicoColegio(forms.ModelForm):
    class Meta:
        model = RelatorioDeAtendimentoCeu
        exclude = ()

        widgets = {'participantes_previa': forms.NumberInput(attrs={'placeholder': 'Prévia'}),
                   'participantes_confirmados': forms.NumberInput(attrs={'placeholder': 'Confirmados'}),
                   }


class OrdemDeServicoEmpresa(forms.ModelForm):
    class Meta:
        model = RelatorioDeAtendimentoCeu
        exclude = ('responsaveis', 'serie', 'solicitado', 'entregue')

        widgets = {'instituicao': forms.TimeInput(attrs={'onClick': 'verificarObrigatoriedade()'}),
                   'participantes_previa': forms.NumberInput(attrs={'placeholder': 'Prévia'}),
                   'participantes_confirmados': forms.NumberInput(attrs={'placeholder': 'Confirmados'}),
                   }
