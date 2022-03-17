from django.db import models

from ceu.models import Atividades


class Monitor(models.Model):
    nome = models.CharField(max_length=255)

    def __str__(self):
        return self.nome


class Vendedor(models.Model):
    nome_vendedor = models.CharField(max_length=255)

    def __str__(self):
        return self.nome_vendedor


class AtividadesEco(models.Model):
    atividade = models.CharField(max_length=255)


class ProdutosPeraltas(models.Model):
    produto = models.CharField(max_length=255)


class PerfilsParticipantes(models.Model):
    ano = models.CharField(max_length=255)
    idade = models.CharField(max_length=255)


class ResumoFinanceiro(models.Model):
    tipo_contrato = (
        (1, 'Grupo'),
        (2, 'Individual')
    )

    valor = models.FloatField()
    forma_pagamento = models.CharField(max_length=255)
    vencimentos = models.CharField(max_length=255)
    contrato = models.IntegerField(choices=tipo_contrato)
    nota_fiscal = models.BooleanField()


class CodigosApp(models.Model):
    cliente_pj = models.CharField(max_length=20)
    cliente_pf = models.CharField(max_length=20)
    evento = models.CharField(max_length=20)
    reserva = models.CharField(max_length=20)


class InformacoesAdcionais(models.Model):
    servicos_de_bordo = (
        (1, 'Padrão'),
        (2, 'Diferenciado')
    )

    tipos_monitoria = (
        (1, '1/2 monitoria (fora de quarto - 1/20)'),
        (2, '1/2 monitoria (dentro de quarto - 1/20'),
        (3, 'Monitoria completa (em quarto - 1/10)')
    )

    tipos_enfermaria = (
        (1, 'Padrão'),
        (2, 'Garantia')
    )

    transporte = models.BooleanField()
    endereco_embarque = models.CharField(max_length=255)
    etiquetas_embarque = models.BooleanField()
    servico_bordo = models.IntegerField(choices=servicos_de_bordo)
    monitoria = models.IntegerField(choices=tipos_monitoria)
    biologo = models.BooleanField()
    quais_atividades = models.CharField(max_length=255, blank=True)
    seguro = models.BooleanField()
    exclusividade = models.BooleanField()
    fotos_site = models.BooleanField()
    abada = models.BooleanField()
    camiseta = models.BooleanField()
    enfermaria = models.IntegerField()
    horario_garantia = models.TimeField(blank=True, null=True)
    roupa_de_cama = models.BooleanField()
    camera_on_line = models.BooleanField()
    cd_para_aluno = models.BooleanField()
    bate_bate = models.BooleanField()
    fogueira = models.BooleanField()
    atividades_ceu = models.ManyToManyField(Atividades)
    atividades_eco = models.ManyToManyField(AtividadesEco)
    outros = models.CharField(max_length=300, blank=True)


class ClienteColegio(models.Model):
    razao_social = models.CharField(max_length=255)
    cnpj = models.CharField(max_length=18)
    nome_fantasia = models.CharField(max_length=255)
    endereco = models.CharField(max_length=600)
    bairro = models.CharField(max_length=255)
    cidade = models.CharField(max_length=255)
    estado = models.CharField(max_length=255)
    cep = models.CharField(max_length=8)


class FichaDeEvento(models.Model):
    responsavel_evento = models.CharField(max_length=255)
    cargo = models.CharField(max_length=255)
    fone = models.CharField(max_length=9)
    email_responsavel_evento = models.EmailField()
    produto = models.ManyToManyField(ProdutosPeraltas)
    check_in = models.DateTimeField()
    check_out = models.DateTimeField()
    professores_com_alunos = models.BooleanField()
    qtd_convidada = models.PositiveIntegerField()
    qtd_confirmada = models.PositiveIntegerField(blank=True, null=True)
    perfil_participantes = models.ManyToManyField(PerfilsParticipantes)
    refeicoes = models.JSONField(blank=True, null=True)
    informacoes_adcionais = models.ForeignKey(InformacoesAdcionais, on_delete=models.CASCADE)
    observacoes = models.TextField(blank=True)
    resumo_financeiro = models.ForeignKey(ResumoFinanceiro, on_delete=models.CASCADE)
    vendedora = models.ForeignKey(Vendedor, on_delete=models.DO_NOTHING)
