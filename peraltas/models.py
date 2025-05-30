import calendar
import math
from collections import defaultdict
from datetime import datetime, timedelta
from heapq import nlargest
from itertools import chain

import reversion
from django import forms
from django.contrib.contenttypes.models import ContentType
from django.contrib.postgres.fields import JSONField
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.db import models, transaction
from django.db.models import ManyToManyField, Count, Q, Sum
from django.db.models.functions import TruncMonth, TruncYear
from django.urls import reverse
from django.utils import timezone
from import_export import resources
from import_export.fields import Field
from reversion.models import Version

from ceu.models import Atividades, Locaveis
from cozinha.models import HorarioRefeicoes
from cozinha.utils import filtrar_refeicoes


def atribuir_diretoria_vendedor():
    return Vendedor.objects.filter(usuario__groups__name__icontains='diretoria').first().id


def atribuir_diretoria():
    return User.objects.filter(groups__name__icontains='diretoria').first().id


def get_first_setor_monitoria():
    try:
        # Retorna o primeiro registro, ordenado pelo campo `id`
        return SetorMonitoria.objects.all().order_by('id').first().id
    except ObjectDoesNotExist:
        # Retorna `None` se não houver registros, para evitar erros
        return None


class SetorMonitoria(models.Model):
    setor = models.CharField(max_length=100)

    def __str__(self):
        return self.setor


class NivelMonitoria(models.Model):
    nivel = models.CharField(max_length=100)
    coordenacao = models.BooleanField(default=False)
    setor_monitoria = models.ForeignKey(SetorMonitoria, on_delete=models.CASCADE, default=get_first_setor_monitoria)


    def __str__(self):
        return self.nivel


class Monitor(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE)
    telefone = models.CharField(max_length=11)
    cidade_horigem = models.CharField(max_length=255, verbose_name='Moradia', blank=True)
    valor_diaria = models.DecimalField(null=True, decimal_places=2, max_digits=5)
    valor_diaria_coordenacao = models.DecimalField(null=True, decimal_places=2, max_digits=5)
    valor_diaria_biologo = models.DecimalField(null=True, decimal_places=2, max_digits=5)
    nivel_acampamento = models.ForeignKey(
        NivelMonitoria,
        on_delete=models.DO_NOTHING,
        null=True,
        blank=True,
        related_name='nivel_acampamento'
    )
    nivel_hotelaria = models.ForeignKey(
        NivelMonitoria,
        on_delete=models.DO_NOTHING,
        null=True,
        blank=True,
        related_name='nivel_hotelaria'
    )
    nivel_corporativo = models.ForeignKey(
        NivelMonitoria,
        on_delete=models.DO_NOTHING,
        null=True,
        blank=True,
        related_name='nivel_corporativo'
    )
    nivel_tecnica = models.ForeignKey(
        NivelMonitoria,
        on_delete=models.DO_NOTHING,
        null=True,
        blank=True,
        related_name='nivel_tecnica'
    )
    aceite_do_termo = models.BooleanField(default=False)
    biologo = models.BooleanField(default=False)
    tecnica = models.BooleanField(default=False)
    fixo = models.BooleanField(default=False)
    nota = models.FloatField(default=0.00)
    n_avaliacoes = models.IntegerField(default=0)

    def __str__(self):
        return self.usuario.get_full_name()

    def nome_completo(self):
        return self.usuario.get_full_name()

    @property
    def nivel(self):
        if self.tecnica:
            return self.nivel_tecnica

        if self.nivel_acampamento is not None:
            return self.nivel_acampamento

        if self.nivel_hotelaria is not None:
            return self.nivel_hotelaria

        if self.nivel_corporativo is not None:
            return self.nivel_corporativo

        else:
            return 'Sem nível atribuído'

    @property
    def setor(self):
        setores = []

        if self.nivel_acampamento is not None:
            setores.append('acampamento')

        if self.nivel_hotelaria is not None:
            setores.append('hotelaria')

        if self.nivel_corporativo is not None:
            setores.append('corporativo')

        if self.nivel_tecnica is not None:
            setores.append('tecnica')

        return setores


class Enfermeira(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE)
    telefone = models.CharField(max_length=11)
    valor_diaria = models.DecimalField(null=True, decimal_places=2, max_digits=5)
    valor_pernoite = models.DecimalField(null=True, decimal_places=2, max_digits=5)
    pode_pernoitar = models.BooleanField(default=False)
    nivel = models.ForeignKey(NivelMonitoria, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.usuario.get_full_name()


class TipoAtividade(models.Model):
    tipo_atividade = models.CharField(max_length=255)

    def __str__(self):
        return self.tipo_atividade


class GrupoAtividade(models.Model):
    grupo = models.CharField(max_length=100)
    obrigatoria = models.BooleanField(default=False)

    def __str__(self):
        return self.grupo


class AtividadePeraltas(models.Model):
    nome_atividade = models.CharField(max_length=255, verbose_name='Nome da atividade')
    local = models.CharField(max_length=255)
    grupo = models.ForeignKey(GrupoAtividade, on_delete=models.CASCADE, null=True)
    idade_min = models.PositiveIntegerField(verbose_name='Idade mínima')
    idade_max = models.PositiveIntegerField(verbose_name='Idade máxima')
    participantes_min = models.PositiveIntegerField(verbose_name='Número mínimo de participantes')
    participantes_max = models.PositiveIntegerField(verbose_name='Número máximo de participantes')
    monitores_min = models.PositiveIntegerField(verbose_name='Número mínimo de monitores')
    monitores_max = models.PositiveIntegerField(verbose_name='Número máximo de monitores')
    duracao = models.DurationField(blank=True, null=True)
    lista_materiais = models.CharField(max_length=255, verbose_name='Lista de materiais')
    tipo_atividade = models.ManyToManyField(TipoAtividade, verbose_name='Tipo da atividade')
    nivel_atividade = models.ForeignKey(
        NivelMonitoria,
        on_delete=models.SET_NULL,
        verbose_name='Nível da atividade',
        blank=True,
        null=True
    )  # TODO: Vai ser verificado o que vai ser feito com este campo
    manual_atividade = models.FileField(blank=True, upload_to='manuais_atividades_acampamento/%Y/%m/%d',
                                        verbose_name='Manual')
    valor = models.DecimalField(decimal_places=2, max_digits=5, default=0.00)

    def __str__(self):
        return self.nome_atividade


class Vendedor(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE, blank=True, null=True)
    telefone = models.CharField(max_length=11)
    supervisor = models.BooleanField(default=False)
    nota = models.FloatField(default=0.00)
    n_avaliacoes = models.IntegerField(default=0)

    def __str__(self):
        return self.usuario.get_full_name()

    def nome_completo(self):
        return self.usuario.get_full_name()


class AtividadesEco(models.Model):
    nome_atividade_eco = models.CharField(max_length=255, verbose_name='Nome da atividade')
    local = models.CharField(max_length=255)
    idade_min = models.PositiveIntegerField(verbose_name='Idade mínima')
    idade_max = models.PositiveIntegerField(verbose_name='Idade máxima')
    participantes_min = models.PositiveIntegerField(verbose_name='Número mínimo de participantes')
    participantes_max = models.PositiveIntegerField(verbose_name='Número máximo de participantes')
    monitores_min = models.PositiveIntegerField(verbose_name='Número mínimo de monitores')
    monitores_max = models.PositiveIntegerField(verbose_name='Número máximo de monitores')
    duracao = models.DurationField(blank=True, null=True)
    lista_materiais = models.CharField(max_length=255, verbose_name='Lista de materiais')
    biologo = models.BooleanField(default=False)
    manual_atividade = models.FileField(blank=True, upload_to='manuais_atividades_eco/%Y/%m/%d', verbose_name='Manual')
    valor = models.DecimalField(decimal_places=2, max_digits=5, default=0.00)

    def __str__(self):
        return self.nome_atividade_eco


class ProdutosPeraltas(models.Model):
    produto = models.CharField(max_length=255)
    pernoite = models.BooleanField(default=True)
    colegio = models.BooleanField(default=True)
    brotas_eco = models.BooleanField(default=False)
    meninos_e_meninas = models.BooleanField(default=False)
    n_dias = models.PositiveIntegerField(blank=True, null=True, verbose_name='Número de pernoites')
    hora_padrao_check_in = models.TimeField(blank=True, null=True)
    hora_padrao_check_out = models.TimeField(blank=True, null=True)

    def __str__(self):
        return self.produto


class ProdutoCorporativo(models.Model):
    produto = models.CharField(max_length=255)
    pernoite = models.BooleanField(default=True)
    n_dias = models.PositiveIntegerField(blank=True, null=True, verbose_name='Número de pernoites')
    hora_padrao_check_in = models.TimeField(blank=True, null=True)
    hora_padrao_check_out = models.TimeField(blank=True, null=True)
    brotas_eco = models.BooleanField(default=0)

    def __str__(self):
        return self.produto


class PerfilsParticipantes(models.Model):
    fase = models.CharField(max_length=255)
    ano = models.CharField(max_length=255, blank=True)
    idade = models.CharField(max_length=255)

    def __str__(self):

        if self.ano != '':
            return f'{self.ano}({self.idade})'
        else:
            return f'{self.fase}({self.idade})'


class CodigosPadrao(models.Model):
    codigo = models.CharField(unique=True, max_length=10)
    nome = models.CharField(max_length=50)


class TiposPagamentos(models.Model):
    tipo_pagamento = models.CharField(max_length=255)
    offline = models.BooleanField(default=False)

    def __str__(self):
        return self.tipo_pagamento


@reversion.register
class CodigosApp(models.Model):
    cliente_pj = models.IntegerField()
    cliente_pf = models.IntegerField()
    evento_app = models.CharField(max_length=255, null=True, blank=True)
    eficha = models.CharField(max_length=255)
    reserva = models.CharField(max_length=255)
    ficha_financeira = models.CharField(max_length=255, null=True, blank=True)
    tipo_de_pagamento = models.ManyToManyField(TiposPagamentos, blank=True)

    def __str__(self):
        return f'Cliente PJ: {self.cliente_pj}, cliente PF: {self.cliente_pf}'

    @classmethod
    def log_de_alteracoes(cls):
        ...


class ClienteColegio(models.Model):
    razao_social = models.CharField(max_length=255)
    cnpj = models.CharField(max_length=18, unique=True)
    nome_fantasia = models.CharField(max_length=255)
    nickname = models.CharField(max_length=255, blank=True, null=True)
    codigo_app_pj = models.IntegerField(unique=True, blank=True, null=True)
    endereco = models.CharField(max_length=600)
    bairro = models.CharField(max_length=255)
    cidade = models.CharField(max_length=255)
    estado = models.CharField(max_length=255)
    cep = models.CharField(max_length=10)
    responsavel_alteracao = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        blank=True, null=True,
        related_name='responsavel_alteracao'
    )
    responsavel_cadastro = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        blank=True, null=True,
        related_name='responsavel_cadastro_cliente'
    )

    def __str__(self):
        return self.nickname if self.nickname else self.nome_fantasia


class ListaDeCargos(models.Model):
    cargo = models.CharField(max_length=255)

    def __str__(self):
        return self.cargo


class Responsavel(models.Model):
    nome = models.CharField(max_length=255)
    cargo = models.ManyToManyField(ListaDeCargos)
    fone = models.CharField(max_length=16)
    email_responsavel_evento = models.EmailField()
    responsavel_cadastro = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        blank=True, null=True,
        related_name='responsavel_cadastro'
    )
    responsavel_atualizacao = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        blank=True, null=True,
        related_name='responsavel_atualizacao'
    )

    def __str__(self):
        return self.nome

    @property
    def responsavel_por_cliente(self):
        relacao = RelacaoClienteResponsavel.objects.get(responsavel=self)

        return relacao.cliente

    @property
    def listar_cargos(self):
        return ', '.join([c.cargo for c in self.cargo.all()])


class EventosCancelados(models.Model):
    estagios_evento = (
        ('pre_reserva', 'Pré reserva'),
        ('reserva_confirmada', 'Reserva confirmada'),
        ('ficha_evento', 'Ficha de evento'),
        ('ordem_servico', 'Ordem de serviço')
    )

    cliente = models.CharField(max_length=255)
    cnpj_cliente = models.CharField(max_length=18)
    estagio_evento = models.CharField(choices=estagios_evento, max_length=20)
    atendente = models.CharField(max_length=50)
    produto_contratado = models.ForeignKey(ProdutosPeraltas, on_delete=models.DO_NOTHING)
    produto_corporativo_contratado = models.ForeignKey(
        ProdutoCorporativo, on_delete=models.DO_NOTHING,
        blank=True,
        null=True
    )
    data_entrada = models.DateField()
    data_saida = models.DateField()
    data_check_in_evento = models.DateField()
    hora_check_in_evento = models.TimeField()
    data_check_out_evento = models.DateField()
    hora_check_out_evento = models.TimeField()
    dias_evento = models.PositiveIntegerField()
    codigo_pagamento = models.CharField(max_length=255)
    adesao = models.FloatField()
    veio_ano_anterior = models.BooleanField(choices=[(True, 'Sim'), (False, 'Não')], default=False)
    motivo_cancelamento = models.TextField()
    tipo_evento = models.CharField(choices=(('colegio', 'Colégio'), ('corporativo', 'Corporativo')), max_length=12)
    participantes_reservados = models.PositiveIntegerField()
    participantes_confirmados = models.PositiveIntegerField()
    colaborador_excluiu = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True,
                                            verbose_name='Colaborador que cancelou')

    def __str__(self):
        return f'Cancelamento do evento de {self.cliente}.'


class EmpresaOnibus(models.Model):
    viacao = models.CharField(max_length=255)
    cnpj = models.CharField(max_length=18, unique=True)
    endereco = models.CharField(max_length=255)
    bairro = models.CharField(max_length=255)
    cidade = models.CharField(max_length=255)
    estado = models.CharField(max_length=255)
    cep = models.CharField(max_length=10)

    def __str__(self):
        return self.viacao


class OpcionaisGerais(models.Model):
    opcional_geral = models.CharField(max_length=100)

    def __str__(self):
        return self.opcional_geral


class OpcionaisFormatura(models.Model):
    opcional_formatura = models.CharField(max_length=100)

    def __str__(self):
        return self.opcional_formatura


class OpcoesProfessoresEmQuarto(models.Model):
    tipo = models.CharField(max_length=255)
    descricao = models.TextField(blank=True)

    def __str__(self):
        return self.tipo


@reversion.register
class InformacoesAdcionais(models.Model):
    tipos_monitoria = (
        (1, '1/2 monitoria (fora de quarto - 1/20)'),
        (2, '1/2 monitoria (dentro de quarto - 1/20'),
        (3, 'Monitoria completa (em quarto - 1/12)'),
        (4, 'Monitoria completa (fora do quarto - 1/12')
    )

    tipos_enfermaria = (
        (2, '8h às 22h'),
        (3, '8h às 8h (24h)'),
        (1, 'Sem enfermeira')
    )

    sim_nao = (
        ('', ''),
        (0, 'Não'),
        (1, 'Sim')
    )

    transporte = models.BooleanField()
    transporte_fechado_internamente = models.IntegerField(choices=sim_nao, default='', blank=True, null=True)
    lanche_bordo = models.BooleanField(default=False)
    ida = models.BooleanField(default=False)
    volta = models.BooleanField(default=False)
    seguro = models.BooleanField()
    monitoria = models.IntegerField(choices=tipos_monitoria, blank=True, null=True)
    quais_atividades = models.ManyToManyField(AtividadesEco, blank=True)
    enfermaria = models.IntegerField(choices=tipos_enfermaria, default=1)
    cantina = models.IntegerField(choices=sim_nao, default='')
    roupa_de_cama = models.IntegerField(choices=sim_nao, default='')
    link_foto = models.IntegerField(choices=sim_nao, default='')
    opcionais_geral = models.ManyToManyField(OpcionaisGerais, blank=True)
    opcionais_formatura = models.ManyToManyField(OpcionaisFormatura, blank=True)
    professores_dormem_em_quarto = models.BooleanField(default=False)
    professores_em_quarto = models.ForeignKey(OpcoesProfessoresEmQuarto, on_delete=models.DO_NOTHING, blank=True, null=True)

    def __str__(self):
        return f'Informações adicionais id: {self.id}'

    @classmethod
    def log_de_alteracao(cls):
        pre_alteracoes = (
            Version.objects
            .get_for_model(cls)
            .select_related('revision')
            .order_by('-revision__date_created')[:100]
        )

    def save(self, *args, **kwargs):
        # Se professores_em_quarto estiver preenchido, forçamos o booleano como True
        if self.professores_em_quarto is not None:
            self.professores_dormem_em_quarto = True

        super().save(*args, **kwargs)


class RelacaoClienteResponsavel(models.Model):
    cliente = models.ForeignKey(ClienteColegio, on_delete=models.CASCADE)
    responsavel = models.ManyToManyField(Responsavel)


class FichaDeEvento(models.Model):
    empresa_choices = (
        ('Peraltas', 'Peraltas'),
        ('CEU', 'Fundação CEU'),
        ('Peraltas CEU', 'Peraltas + Fundação CEU')
    )

    cliente = models.ForeignKey(ClienteColegio, on_delete=models.CASCADE, verbose_name='Cliente')
    responsavel_evento = models.ForeignKey(Responsavel, on_delete=models.CASCADE,
                                           verbose_name='Responsável pelo evento')
    produto = models.ForeignKey(ProdutosPeraltas, on_delete=models.DO_NOTHING, verbose_name='Produto')
    produto_corporativo = models.ForeignKey(ProdutoCorporativo, on_delete=models.CASCADE, blank=True, null=True,
                                            verbose_name='Produto corporativo')
    check_in = models.DateTimeField(verbose_name='Check in')
    check_out = models.DateTimeField(verbose_name='Check out')
    obs_edicao_horario = models.CharField(max_length=255, blank=True, null=True,
                                          verbose_name='Observação da edição do horário')
    qtd_professores = models.PositiveIntegerField(blank=True, null=True, verbose_name='Quantidade de professores')
    qtd_profs_homens = models.PositiveIntegerField(blank=True, null=True,
                                                   verbose_name='Quantidade de professores homens')
    qtd_profs_mulheres = models.PositiveIntegerField(blank=True, null=True,
                                                     verbose_name='Quantidade de professores mulheres')
    qtd_convidada = models.PositiveIntegerField(blank=True, null=True, verbose_name='Quantidade reservada')
    qtd_confirmada = models.PositiveIntegerField(blank=True, null=True, verbose_name='Quantidade confirmada')
    qtd_eficha = models.PositiveIntegerField(blank=True, null=True, verbose_name='Quantidade E-ficha')
    qtd_offline = models.PositiveIntegerField(blank=True, null=True, verbose_name='Quantidade offline')
    qtd_meninos = models.PositiveIntegerField(blank=True, null=True, verbose_name='Quantidade de menino')
    qtd_meninas = models.PositiveIntegerField(blank=True, null=True, verbose_name='Quantidade de meninas')
    qtd_homens = models.PositiveIntegerField(blank=True, null=True, verbose_name='Quantidade de homens')
    qtd_mulheres = models.PositiveIntegerField(blank=True, null=True, verbose_name='Quantidade de mulheres')
    perfil_participantes = models.ManyToManyField(PerfilsParticipantes, blank=True,
                                                  verbose_name='Perfíl dos participantes')
    refeicoes = models.JSONField(blank=True, null=True, verbose_name='Refeições')
    observacoes_refeicoes = models.TextField(verbose_name='Observações das refeições')
    informacoes_adcionais = models.ForeignKey(InformacoesAdcionais, on_delete=models.CASCADE, blank=True, null=True,
                                              verbose_name='Informações adicionais')
    observacoes = models.TextField(blank=True, verbose_name='Observações')
    atividades_ceu = models.ManyToManyField(Atividades, blank=True, verbose_name='Atividades CEU')
    atividades_ceu_a_definir = models.IntegerField(blank=True, null=True, verbose_name='Atividades CEU a definir')
    locacoes_ceu = models.ManyToManyField(Locaveis, blank=True, verbose_name='Locações no CEU')
    informacoes_locacoes = models.JSONField(blank=True, null=True, verbose_name='Informações de locações')
    atividades_eco = models.ManyToManyField(AtividadesEco, blank=True, verbose_name='Atividades extra')
    atividades_peraltas = models.ManyToManyField(GrupoAtividade, blank=True, verbose_name='Atividades Peraltas')
    vendedora = models.ForeignKey(Vendedor, on_delete=models.SET_DEFAULT, default=atribuir_diretoria_vendedor,
                                  verbose_name='Vendedora')
    data_final_inscricao = models.DateField(blank=True, null=True, verbose_name='Data final da inscrição')
    data_divulgacao = models.DateField(blank=True, null=True, verbose_name='Data prevista para divulgação')
    empresa = models.CharField(choices=empresa_choices, max_length=100, blank=True, null=True, verbose_name='Empresa')
    material_apoio = models.FileField(blank=True, null=True, upload_to='materiais_apoio/%Y/%m/%d',
                                      verbose_name='Material de apoio')
    data_preenchimento = models.DateField(blank=True, null=True, editable=False, verbose_name='Data de preenchimento')
    codigos_app = models.ForeignKey(CodigosApp, on_delete=models.DO_NOTHING, blank=True, null=True,
                                    verbose_name='Códigos APP')
    adesao = models.FloatField(blank=True, null=True, verbose_name='Adesão')
    agencia = models.BooleanField(default=False)
    id_negocio = models.CharField(max_length=255, verbose_name='ID negócio', blank=True)
    exclusividade = models.BooleanField(default=False, verbose_name='Exclusividade')
    pre_reserva = models.BooleanField(default=False, verbose_name='Pré reserva')
    agendado = models.BooleanField(default=False, verbose_name='Evento confirmado')
    os = models.BooleanField(default=False, verbose_name='Ordem de serviço')
    escala = models.BooleanField(default=False, verbose_name='Escala')
    ficha_financeira = models.BooleanField(default=False, verbose_name='Ficha financeira')

    def __str__(self):
        return f'Ficha de evento de {self.cliente}'

    def get_all_fields(self):
        return [field.name for field in self._meta.fields]

    def get_field_verbose_name(self, field_name):
        field = self._meta.get_field(field_name)
        return field.verbose_name

    def get_field_type(self, field_name):
        field = self._meta.get_field(field_name)
        return field.get_internal_type()

    def get_many_to_many_fields(self):
        many_to_many_fields = []

        for field in self._meta.get_fields():
            if field.many_to_many:
                many_to_many_fields.append(field.name)

        return many_to_many_fields

    def listar_atividades_ceu(self):
        return ', '.join([atividade.atividade for atividade in self.atividades_ceu.all()])

    def numero_criancas(self):
        return (self.qtd_meninos if self.qtd_meninos else 0) + (self.qtd_meninas if self.qtd_meninas else 0)

    def numero_adultos(self):
        if self.produto.colegio:
            if 'visita' in self.produto.produto.lower():
                soma_adultos = self.qtd_confirmada
            else:
                soma_adultos = self.qtd_professores if self.qtd_professores else 0

        else:
            if self.produto.brotas_eco:
                soma_adultos = self.qtd_convidada
            else:
                soma_adultos = self.qtd_confirmada

        return soma_adultos

    def verificar_refeicao(self, data, refeicao):
        for data_ref, refeicoes in self.refeicoes.items():
            if data_ref == data and refeicao in refeicao in refeicoes:
                return True

        return False

    @classmethod
    def separar_refeicoes(cls, data):
        fichas_evento = cls.objects.filter(
            check_in__date__lte=data,
            check_out__date__gte=data,
            pre_reserva=False
        )
        hotelaria = FichaDeEvento.objects.filter(
            check_in__date=data,
            pre_reserva=True,
            agendado=True,
            produto__brotas_eco=True
        )
        fichas = list(chain(hotelaria, fichas_evento))
        eventos = []

        for ficha in fichas:
            numero_monitores = adultos = criancas = 0
            quantidades = {}

            if ficha.escala:
                numero_monitores = len(EscalaAcampamento.objects.get(ficha_de_evento__id=ficha.id).monitores_embarque.all())

            if ficha.produto.brotas_eco:
                refeicoes_data = ['cafe_manha', 'almoco', 'jantar']
                quantidades, adultos, criancas = filtrar_refeicoes(data)

            else:
                refeicoes_data = ficha.refeicoes[data.strftime('%Y-%m-%d')]
                criancas = ficha.numero_criancas()
                adultos = ficha.numero_adultos()

                for refeicao in refeicoes_data:
                    quantidades[refeicao] = {
                        'adultos': ficha.numero_adultos(),
                        'criancas': ficha.numero_criancas(),
                        'monitores': numero_monitores,
                        'total': ficha.numero_adultos() + ficha.numero_criancas() + numero_monitores,
                    }

            eventos.append({
                'id': ficha.id,
                'cliente': ficha.cliente,
                'produto': ficha.produto,
                'check_in': ficha.check_in,
                'check_out': ficha.check_out,
                'numero_adultos': adultos,
                'numero_criancas': criancas,
                'numero_monitores': numero_monitores,
                'contagem': quantidades,
                'refeicoes': refeicoes_data,
                'obs': ficha.observacoes_refeicoes,
            })

        return eventos

    def tabelar_refeicoes(self):
        dados = []

        for dia in self.refeicoes:
            dados_refeicoes = []

            dados_refeicoes = [
                'cafe_manha' in self.refeicoes[dia],
                'lanche_manha' in self.refeicoes[dia],
                'coffee_manha' in self.refeicoes[dia],
                'almoco' in self.refeicoes[dia],
                'lanche_tarde' in self.refeicoes[dia],
                'coffee_tarde' in self.refeicoes[dia],
                'jantar' in self.refeicoes[dia],
                'lanche_noite' in self.refeicoes[dia],
            ]

            dados.append({'dia': dia, 'refeicoes': dados_refeicoes})

        return dados

    def juntar_refeicoes(self):
        dados = []

        for dia in self.refeicoes:
            dados_refeicoes = []

            dados_refeicoes.append('Café da manhã') if 'cafe_manha' in self.refeicoes[dia] else ...
            dados_refeicoes.append('Coffee manhã') if 'coffee_manha' in self.refeicoes[dia] else ...
            dados_refeicoes.append('Almoço') if 'Almoço' in self.refeicoes[dia] else ...
            dados_refeicoes.append('Lanche da tarde') if 'lanche_tarde' in self.refeicoes[dia] else ...
            dados_refeicoes.append('Coffee tarde') if 'coffee_tarde' in self.refeicoes[dia] else ...
            dados_refeicoes.append('Jantar') if 'jantar' in self.refeicoes[dia] else ...
            dados_refeicoes.append('Lanche da noite') if 'lanche_noite' in self.refeicoes[dia] else ...

            dados.append({'dia': dia, 'refeicoes': ', '.join(dados_refeicoes)})

        return dados

    @property
    def refeicoes_realizadas(self):
        refeicoes = set()

        for refeicao in self.refeicoes.values():
            for ref in refeicao:
                print(ref)
                refeicoes.add(ref)

        return list(refeicoes)

    def separar_informacoes_locacoes(self):
        dados = []

        for espaco in self.informacoes_locacoes.values():
            dados.append(espaco)

        return dados

    @staticmethod
    def juntar_dados_locacoes(dados_requisicao):
        dados_locacoes = {}

        for posicao, espaco in enumerate(dados_requisicao.getlist('espaco'), start=1):
            dados_locacoes[f'espaco_{posicao}'] = {
                'id_espaco': dados_requisicao.getlist('id_espaco')[posicao - 1],
                'espaco': espaco,
                'intervalo': dados_requisicao.getlist('intervalo')[posicao - 1],
                'formato_sala': dados_requisicao.getlist('formato_sala')[posicao - 1]
            }

        return dados_locacoes


class Eventos(models.Model):
    estagios_evento = (
        ('pre_reserva', 'Pré reserva'),
        ('confirmado', 'Evento confirmado'),
        ('ficha_evento', 'Ficha de evento'),
        ('ordem_servico', 'Ordem de serviço'),
    )

    sim_e_nao = (
        (True, 'Sim'),
        (False, 'Não')
    )

    ordem_de_servico = models.ForeignKey(
        'ordemDeServico.OrdemDeServico',
        on_delete=models.DO_NOTHING,
        null=True,
        blank=True
    )
    ficha_de_evento = models.ForeignKey(
        FichaDeEvento,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name='Ficha de evento'
    )
    colaborador = models.ForeignKey(Vendedor, on_delete=models.SET_DEFAULT, verbose_name='Colaborador', default=atribuir_diretoria_vendedor)
    cliente = models.ForeignKey(ClienteColegio, on_delete=models.CASCADE, verbose_name='Cliente')
    cnpj = models.CharField(max_length=18, verbose_name='CNPJ')
    responsavel = models.ForeignKey(Responsavel, on_delete=models.PROTECT, verbose_name='Responsavel')
    cargo_responsavel = models.CharField(max_length=255, verbose_name='Cargo responsável', blank=True, null=True)
    telefone_responsavel = models.CharField(max_length=255, verbose_name='telefone responsável')
    email_responsavel = models.CharField(max_length=255, verbose_name='email responsável')
    data_check_in = models.DateField(verbose_name='Data de check in')
    hora_check_in = models.TimeField(verbose_name='Hora de check in')
    data_check_out = models.DateField(verbose_name='Data de check out')
    hora_check_out = models.TimeField(verbose_name='Hora de check out')
    qtd_previa = models.IntegerField(verbose_name='QTD reservado')
    qtd_confirmado = models.IntegerField(verbose_name='QTD confirmado')
    data_preenchimento = models.DateField(verbose_name='Data de preenchimento')
    estagio_evento = models.CharField(choices=estagios_evento, max_length=25, verbose_name='Estágio do evento')
    codigo_pagamento = models.CharField(max_length=255, blank=True, verbose_name='Código de pagamento')
    tipo_evento = models.CharField(max_length=25, verbose_name='Tipo de evento')
    dias_evento = models.IntegerField(verbose_name='Dias de evento')
    produto_peraltas = models.ForeignKey(ProdutosPeraltas, on_delete=models.DO_NOTHING, verbose_name='Produto Peraltas')
    produto_corporativo = models.ForeignKey(
        ProdutoCorporativo,
        on_delete=models.DO_NOTHING,
        blank=True,
        null=True,
        verbose_name='Produto Corporativo'
    )
    adesao = models.FloatField(default=0.0, verbose_name='Adesão')
    veio_ano_anterior = models.BooleanField(choices=sim_e_nao, verbose_name='Veio no ano anterior')

    class Meta:
        verbose_name_plural = 'Eventos'

        permissions = [
            ('ver_relatorios_eventos', 'Relatório de eventos'),
        ]

    def adesao_formatado(self):
        return f'{self.adesao:.2f}%'.replace('.', ',')

    adesao_formatado.short_description = 'Adesão'

    @classmethod
    def campos_cadastro_eventos(cls):
        return {campo.name: campo.verbose_name for campo in cls._meta.get_fields()}

    @staticmethod
    def nome_mes(n_mes):
        meses = [
            'Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
            'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro'
        ]

        return meses[n_mes - 1]

    @staticmethod
    def numero_mes(nome_mes):
        meses = [
            'Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
            'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro'
        ]

        return meses.index(nome_mes) + 1

    @classmethod
    def pegar_escolha_estagios_evento(cls, estagio):
        for choice in cls.estagios_evento:
            if choice[0] == estagio:

                return choice[1]

        return None

    @classmethod
    def preparar_relatorio_mes_mes(cls):
        relatorios = {}
        relatorio_mes_mes = []
        comparados = []
        eventos = cls.objects.filter(
            data_check_in__month__gte=datetime.today().month,
            data_check_in__year__gte=datetime.today().year,
            data_check_in__lte=datetime.today().date() + timedelta(days=180),
        ).order_by('data_check_in')

        for evento in eventos:
            mes_ano = f'{cls.nome_mes(evento.data_check_in.month)}/{evento.data_check_in.year}'

            if mes_ano in comparados:
                relatorios[mes_ano]['n_pre_reserva'] += 1 if evento.estagio_evento == 'pre_reserva' else 0
                relatorios[mes_ano][
                    'n_previa_pre_reserva'] += evento.qtd_previa if evento.estagio_evento == 'pre_reserva' else 0
                relatorios[mes_ano][
                    'n_confirmados_pre_reserva'] += evento.qtd_confirmado if evento.estagio_evento == 'pre_reserva' else 0
                relatorios[mes_ano]['n_confirmado'] += 1 if evento.estagio_evento == 'confirmado' else 0
                relatorios[mes_ano][
                    'n_previa_confirmado'] += evento.qtd_previa if evento.estagio_evento == 'confirmado' else 0
                relatorios[mes_ano][
                    'n_confirmados_confirmado'] += evento.qtd_confirmado if evento.estagio_evento == 'confirmado' else 0
                relatorios[mes_ano]['n_ficha_de_evento'] += 1 if evento.estagio_evento == 'ficha_evento' else 0
                relatorios[mes_ano][
                    'n_previa_ficha_de_evento'] += evento.qtd_previa if evento.estagio_evento == 'ficha_evento' else 0
                relatorios[mes_ano][
                    'n_confirmados_ficha_de_evento'] += evento.qtd_confirmado if evento.estagio_evento == 'ficha_evento' else 0
                relatorios[mes_ano]['n_ordem_de_servico'] += 1 if evento.estagio_evento == 'ordem_servico' else 0
                relatorios[mes_ano][
                    'n_previa_ordem_de_servico'] += evento.qtd_previa if evento.estagio_evento == 'ordem_servico' else 0
                relatorios[mes_ano][
                    'n_confirmados_ordem_de_servico'] += evento.qtd_confirmado if evento.estagio_evento == 'ordem_servico' else 0
            else:
                comparados.append(mes_ano)
                relatorios[mes_ano] = {
                    'n_pre_reserva': 1 if evento.estagio_evento == 'pre_reserva' else 0,
                    'n_previa_pre_reserva': evento.qtd_previa if evento.estagio_evento == 'pre_reserva' else 0,
                    'n_confirmados_pre_reserva': evento.qtd_confirmado if evento.estagio_evento == 'pre_reserva' else 0,
                    'n_confirmado': 1 if evento.estagio_evento == 'confirmado' else 0,
                    'n_previa_confirmado': evento.qtd_previa if evento.estagio_evento == 'confirmado' else 0,
                    'n_confirmados_confirmado': evento.qtd_confirmado if evento.estagio_evento == 'confirmado' else 0,
                    'n_ficha_de_evento': 1 if evento.estagio_evento == 'ficha_evento' else 0,
                    'n_previa_ficha_de_evento': evento.qtd_previa if evento.estagio_evento == 'ficha_evento' else 0,
                    'n_confirmados_ficha_de_evento': evento.qtd_confirmado if evento.estagio_evento == 'ficha_evento' else 0,
                    'n_ordem_de_servico': 1 if evento.estagio_evento == 'ordem_servico' else 0,
                    'n_previa_ordem_de_servico': evento.qtd_previa if evento.estagio_evento == 'ordem_servico' else 0,
                    'n_confirmados_ordem_de_servico': evento.qtd_confirmado if evento.estagio_evento == 'ordem_servico' else 0,
                }

        for mes_ano, valores in relatorios.items():
            temp = {'mes_ano': mes_ano}

            for chave, valor in valores.items():
                temp[chave] = valor

            relatorio_mes_mes.append(temp)

        return relatorio_mes_mes

    @classmethod
    def preparar_relatorio_produtos(
            cls,
            pesquisar_seis_meses=True,
            mes_check_in=None,
            ano_check_in=None,
    ):
        relatorios = {}
        produtos_presentes = set()

        if pesquisar_seis_meses:
            eventos = cls.objects.filter(
                data_check_in__month__gte=datetime.today().month,
                data_check_in__year__gte=datetime.today().year,
                data_check_in__lte=datetime.today().date() + timedelta(days=180),
            ).order_by('data_check_in')
        else:
            if not mes_check_in and not ano_check_in:
                raise f'Informar mes e ano de check in para a montagem do relatório'

            eventos = cls.objects.filter(
                data_check_in__month=mes_check_in,
                data_check_in__year=ano_check_in,
            ).order_by('data_check_in')

        for evento in eventos:
            mes_ano = f'{cls.nome_mes(evento.data_check_in.month)}/{evento.data_check_in.year}'
            produto = evento.produto_peraltas.produto
            produtos_presentes.add(produto)

            if mes_ano not in relatorios:
                relatorios[mes_ano] = {
                    'pre_reserva': {},
                    'confirmado': {},
                    'ficha_evento': {},
                    'ordem_servico': {}
                }

            if produto not in relatorios[mes_ano][evento.estagio_evento]:
                relatorios[mes_ano][evento.estagio_evento][produto] = 1
            else:
                relatorios[mes_ano][evento.estagio_evento][produto] += 1

        relatorio_produtos = {
            'relatorio_mes_mes': [],
            'produtos': list(produtos_presentes)
        }

        for mes_ano, estagios in relatorios.items():
            relatorio_item = {'mes_ano': mes_ano, 'estagios': {}}

            for estagio, produtos in estagios.items():
                relatorio_item['estagios'][estagio] = []

                for produto in relatorio_produtos['produtos']:
                    relatorio_item['estagios'][estagio].append(produtos.get(produto, 0))

            relatorio_produtos['relatorio_mes_mes'].append(relatorio_item)

        return relatorio_produtos

    @classmethod
    def preparar_relatorio_clientes_mes_estagios(cls, estagio, mes, ano, campos):
        relatorio = []
        verbose_campos = []
        numero_mes = cls.numero_mes(mes)
        eventos_estagio_mes_ano = cls.objects.filter(
            estagio_evento=estagio,
            data_check_in__month=numero_mes,
            data_check_in__year=ano,
        )

        for evento in eventos_estagio_mes_ano:
            campos_evento = {}

            for campo in campos:
                valor_campo = getattr(evento, campo)
                campo_modelo = cls._meta.get_field(campo)
                verbose_name = campo_modelo.verbose_name if hasattr(campo_modelo, 'verbose_name') else campo

                if verbose_name not in verbose_campos:
                    verbose_campos.append(verbose_name)

                match campo_modelo:
                    case models.ForeignKey():
                        if campo == 'ficha_de_evento':
                            if evento.estagio_evento in ['ordem_servico', 'ficha_evento']:
                                valor_campo = {
                                    'cliente': str(evento.cliente),
                                    'url': reverse('ver_ficha_de_evento', kwargs={
                                        'id_ficha_de_evento': evento.ficha_de_evento.pk
                                    }),
                                }
                            else:
                                valor_campo = ''
                        elif campo == 'ordem_de_servico' and evento.estagio_evento in ['ordem_servico']:
                            valor_campo = {
                                'cliente': str(evento.cliente),
                                'url': reverse('ver_ordem_de_servico', kwargs={
                                    'id_ordem_de_servico': evento.ficha_de_evento.pk
                                }),
                            }
                        else:
                            valor_campo = str(valor_campo) if valor_campo else ''
                    case models.DateField():
                        valor_campo = valor_campo.strftime('%d/%m/%Y') if valor_campo else None
                    case models.TimeField():
                        valor_campo = valor_campo.strftime('%H:%M') if valor_campo else None
                    case models.IntegerField():
                        valor_campo = str(valor_campo)
                    case models.CharField():
                        valor_campo = str(valor_campo)
                    case models.FloatField():
                        if campo == 'adesao':
                            valor_campo = f'{valor_campo:.2f}%'.replace('.', ',')
                        else:
                            valor_campo = f'{valor_campo:.2f}'.replace('.', ',')
                    case models.BooleanField():
                        valor_campo = 'Sim' if valor_campo else 'Não'

                campos_evento[campo] = valor_campo

            relatorio.append(campos_evento)

        return {
            'relatorio': relatorio,
            'estagio': cls.pegar_escolha_estagios_evento(estagio),
            'campos': verbose_campos
        }

    @classmethod
    def peparar_relatorio_estagio(cls, mes, ano):
        dados = []
        pre_reserva = confirmado = ficha_evento = ordem_servico = 0
        eventos = cls.objects.filter(
            data_check_in__month=mes,
            data_check_in__year=ano,
        )

        for evento in eventos:
            if evento.estagio_evento == 'pre_reserva':
                pre_reserva += 1
            elif evento.estagio_evento == 'confirmado':
                confirmado += 1
            elif evento.estagio_evento == 'ficha_evento':
                ficha_evento += 1
            elif evento.estagio_evento == 'ordem_servico':
                ordem_servico += 1

        dados.append({
            'pre_reserva': pre_reserva,
            'confirmado': confirmado,
            'ficha_evento': ficha_evento,
            'ordem_servico': ordem_servico,
        })

        return dados


class DisponibilidadePeraltas(models.Model):
    meses = (
        (1, 'Janeiro'),
        (2, 'Fevereiro'),
        (3, 'Março'),
        (4, 'Abril'),
        (5, 'Maio'),
        (6, 'Junho'),
        (7, 'Julho'),
        (8, 'Agosto'),
        (9, 'Setembro'),
        (10, 'Outubro'),
        (11, 'Novembro'),
        (12, 'Dezembro'),
    )

    monitor = models.ForeignKey(Monitor, on_delete=models.CASCADE, null=True, blank=True)
    enfermeira = models.ForeignKey(Enfermeira, on_delete=models.CASCADE, null=True, blank=True)
    dias_disponiveis = models.TextField(max_length=500)
    mes = models.IntegerField(choices=meses)
    ano = models.CharField(max_length=20)
    n_dias = models.IntegerField()

    def monitor_enfermeira(self):
        return self.monitor if self.monitor else self.enfermeira


class DiaLimitePeraltas(models.Model):
    dia_limite_peraltas = models.PositiveIntegerField()


class EscalaAcampamento(models.Model):
    cliente = models.ForeignKey(ClienteColegio, on_delete=models.CASCADE)
    ficha_de_evento = models.ForeignKey(FichaDeEvento, on_delete=models.CASCADE, null=True)
    monitores_acampamento = models.ManyToManyField(Monitor, related_name='monitores_acampamento')
    monitores_embarque = models.ManyToManyField(Monitor, blank=True, related_name='monitores_embarque')
    tecnicos = models.ManyToManyField(Monitor, blank=True, related_name='tecnicos')
    biologos = models.ManyToManyField(Monitor, blank=True, related_name='biologos')
    enfermeiras = models.ManyToManyField(Enfermeira, blank=True, related_name='enfermeiras')
    ultima_pre_escala = models.JSONField(blank=True, null=True)
    check_in_cliente = models.DateTimeField()
    check_out_cliente = models.DateTimeField()
    observacoes = models.TextField(null=True)
    pre_escala = models.BooleanField(default=False)
    racional_monitores = models.PositiveIntegerField(default=10)
    avaliou_coordenadores = models.ManyToManyField(Monitor, blank=True, related_name='avaliou_coordenadores')

    def tipo_escala(self):
        if self.ficha_de_evento.produto.colegio:
            return "Colégio"
        else:
            return 'Corporativo'

    class Meta:
        permissions = (('confirmar_escala', 'Confirmar Escala'),)

    @property
    def coordenadores(self):
        if self.ficha_de_evento.os:
            ordem = Eventos.objects.get(ficha_de_evento=self.ficha_de_evento).ordem_de_servico

            return ', '.join([coordenador.usuario.get_full_name() for coordenador in ordem.monitor_responsavel.all()])

        return 'Sem monitor definido.'

    @property
    def id_ordem_de_servico(self):
        if self.ficha_de_evento.os:
            return Eventos.objects.get(ficha_de_evento=self.ficha_de_evento).ordem_de_servico.id

    @property
    def valores_escala(self):
        valores_monitoria = valores_coordenadores = valores_biologo = valores_enfermeiras = valores_tecnicos = 0.00
        monitores = set()
        monitores.update(list(self.monitores_acampamento.all()) + list(self.monitores_embarque.all()))
        dias = (self.check_out_cliente - self.check_in_cliente).days + 1

        for monitor in monitores:
            if isinstance(monitor.nivel, NivelMonitoria):
                if monitor.nivel.coordenacao:
                    valores_coordenadores += float(monitor.valor_diaria_coordenacao)
                else:
                    valores_monitoria += float(monitor.valor_diaria)

        for biologo in self.biologos.all():
            valores_biologo += float(biologo.valor_diaria_biologo)

        for enfermeira in self.enfermeiras.all():
            valores_enfermeiras += float(enfermeira.valor_diaria)

        for tecnico in self.tecnicos.all():
            valores_tecnicos += float(tecnico.valor_diaria)

        return (valores_monitoria + valores_coordenadores + valores_biologo + valores_enfermeiras + valores_tecnicos) * dias

    @property
    def valor_escala_sem_extra(self):
        valores_monitoria = valores_coordenadores = 0.00
        monitores = set()
        monitores.update(list(self.monitores_acampamento.all()))
        dias = (self.check_out_cliente - self.check_in_cliente).days + 1

        for monitor in monitores:
            if monitor.nivel.coordenacao:
                valores_coordenadores += float(monitor.valor_diaria_coordenacao)
            else:
                valores_monitoria += float(monitor.valor_diaria)

        return (valores_monitoria + valores_coordenadores) * dias

    @property
    def contagem_niveis(self):
        contagem_niveis = {}
        niveis = ''
        monitores = list(self.monitores_acampamento.all()) + list(self.monitores_embarque.all())

        for monitor in monitores:
            if monitor.nivel.nivel in contagem_niveis:
                contagem_niveis[monitor.nivel.nivel] += 1
            else:
                contagem_niveis[monitor.nivel.nivel] = 1

        for tecnico in self.tecnicos.all():
            if tecnico.nivel.nivel in contagem_niveis:
                contagem_niveis[tecnico.nivel.nivel] += 1
            else:
                contagem_niveis[tecnico.nivel.nivel] = 1

        for biologo in self.biologos.all():
            if biologo.nivel.nivel in contagem_niveis:
                contagem_niveis[biologo.nivel.nivel] += 1
            else:
                contagem_niveis[biologo.nivel.nivel] = 1

        for enfermeira in self.enfermeiras.all():
            if enfermeira.nivel.nivel in contagem_niveis.keys():
                contagem_niveis[enfermeira.nivel.nivel] += 1
            else:
                contagem_niveis[enfermeira.nivel.nivel] = 1

        return contagem_niveis

    def relacao_monitor_participante(self):
        return round(self.ficha_de_evento.qtd_convidada / len(self.monitores_acampamento.all()), 2)

    def media_diarias(self):
        soma_diarias = 0.00
        monitores = set()
        monitores.update(list(self.monitores_acampamento.all()) + list(self.monitores_embarque.all()))

        for monitor in monitores:
            if monitor.nivel.coordenacao:
                soma_diarias += float(monitor.valor_diaria_coordenacao)
            else:
                soma_diarias += float(monitor.valor_diaria)

        return round(soma_diarias / len(monitores), 2)

    @classmethod
    def soma_valor_diaria_nivel(cls, id_escala, id_nivel):
        valor_diaria = 0.00
        escala = cls.objects.get(pk=id_escala)

        for monitor in escala.monitores_acampamento.all():
            if monitor.nivel.id == id_nivel:
                if monitor.nivel.coordenacao:
                    valor_diaria += float(monitor.valor_diaria_coordenacao)
                else:
                    valor_diaria += float(monitor.valor_diaria)

        return f'{valor_diaria:.2f}'.replace('.', ',') if valor_diaria != 0.00 else ''


class EscalaHotelaria(models.Model):
    coordenadores = models.ManyToManyField(Monitor, blank=True, related_name='coordendadores')
    tecnicos_hotelaria = models.ManyToManyField(Monitor, blank=True, related_name='tecnicos_hotelaria')
    monitores_hotelaria = models.JSONField(null=True)
    monitores_escalados = models.ManyToManyField(Monitor)
    pre_escala = models.BooleanField(default=True)
    ultima_pre_escala = models.JSONField(blank=True, null=True)
    data = models.DateField()

    def separar_monitores(self):
        monitores = []

        for id_monitor in self.monitores_hotelaria.values():
            monitor = Monitor.objects.get(id=id_monitor)

            monitores.append({'nome': monitor.usuario.get_full_name(), 'user': monitor.usuario})

        return monitores

    @property
    def coordenadores_escala(self):
        return [monitor.usuario.get_full_name() for monitor in self.coordenadores.all()]

    def data_escala(self):
        return self.data.strftime('%d/%m/%Y')


# ------------------------------------------------ Formulários ---------------------------------------------------------
class CadastroFichaDeEvento(forms.ModelForm):
    perfil_participantes = forms.ModelMultipleChoiceField(
        queryset=PerfilsParticipantes.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False
    )
    perfil_participantes.widget.attrs['class'] = 'form-check-input'

    produto = forms.ModelChoiceField(
        queryset=ProdutosPeraltas.objects.all(),
        widget=forms.RadioSelect,
        required=True
    )
    produto.widget.attrs['class'] = 'form-check-input'
    produto.widget.attrs['onclick'] = 'verQuantidades(this)'

    class Meta:
        model = FichaDeEvento
        exclude = ['data_preenchimento']

        widgets = {
            'check_in': forms.TextInput(attrs={
                'type': 'datetime-local',
                'onChange': 'pegarDias()',
                'onkeyup': '$("#id_check_in").val("")',
                'onclick': 'this.showPicker()'
            }),
            'check_out': forms.TextInput(attrs={
                'type': 'datetime-local',
                'onChange': 'pegarDias()',
                'onkeyup': '$("#id_check_out").val("")',
                'onclick': 'this.showPicker()'
            }),
            'atividades_ceu_a_definir': forms.NumberInput(attrs={
                'min': '0',
                'max': 10,
                'placeholder': 'n',
            }),
            'qtd_convidada': forms.NumberInput(attrs={'readonly': 'readonly'}),
            'exclusividade': forms.CheckboxInput(attrs={'class': 'form-check-input exclusividade'}),
            'produto_corporativo': forms.Select(attrs={'onChange': 'corporativo(this)'}),
            'data_final_inscricao': forms.TextInput(attrs={'type': 'date', 'readonly': 'readonly'}),
            'data_divulgacao': forms.TextInput(attrs={'type': 'date'}),
            'professores_com_alunos': forms.CheckboxInput(attrs={'type': 'checkbox',
                                                                 'class': 'form-check-input'}),
            'id_negocio': forms.TextInput(attrs={'readonly': 'readonly'})
        }

    def __init__(self, *args, **kwargs):
        super(CadastroFichaDeEvento, self).__init__(*args, **kwargs)
        atividades_obrigatorias = GrupoAtividade.objects.filter(obrigatoria=True)
        atividades = []

        for atividade in atividades_obrigatorias:
            atividades.append((atividade.id, atividade.grupo))

        self.fields['atividades_peraltas'].choices = atividades


class CadastroCliente(forms.ModelForm):
    class Meta:
        model = ClienteColegio
        exclude = ()

        widgets = {
            'codigo_app_pj': forms.TextInput(attrs={
                'pattern': '\d*', 'minlength': '6', 'maxlength': '6',
                'onload': 'if (this.value != "") this.prop("readonly", false)',
            }),
        }

    def __init__(self, *args, **kwargs):
        super(CadastroCliente, self).__init__(*args, **kwargs)
        self.fields['codigo_app_pj'].widget.attrs['readonly'] = True


class CadastroResponsavel(forms.ModelForm):
    class Meta:
        model = Responsavel
        exclude = ()

        widgets = {
            'fone': forms.TextInput(attrs={'onfocus': 'mascara_telefone()'})
        }


class CadastroInfoAdicionais(forms.ModelForm):
    class Meta:
        model = InformacoesAdcionais
        exclude = ()

        widgets = {
            'transporte': forms.CheckboxInput(attrs={'onchange': 'pegarEndereco()'}),
            'etiquetas_embarque': forms.CheckboxInput(attrs={'onchange': 'servicoBordo()'}),
            'biologo': forms.CheckboxInput(attrs={'onchange': 'quaisAtividades()'}),
            'transporte_fechado_internamente': forms.Select(attrs={'style': 'width: 100px'}),
            'lanche_bordo': forms.CheckboxInput(attrs={'onclick': 'liberar_ida_e_volta()'})
        }


class CadastroCodigoApp(forms.ModelForm):
    class Meta:
        model = CodigosApp
        exclude = ()

        widgets = {
            'cliente_pj': forms.TextInput(attrs={'pattern': '\d*', 'minlength': '6', 'maxlength': '6'}),
            'cliente_pf': forms.TextInput(attrs={'pattern': '\d*', 'minlength': '6', 'maxlength': '6'}),
            'eficha': forms.TextInput(attrs={'onkeyup': 'this.value=this.value.toUpperCase()'}),
            'reserva': forms.TextInput(attrs={'pattern': '\d*', 'minlength': '6', 'maxlength': '6'}),
            'tipo_de_pagamento': forms.SelectMultiple(attrs={'style': 'width: 100%', 'onchange': ''}),
            'ficha_financeira': forms.TextInput(attrs={'pattern': '\d*', 'min': '0'}),
            'evento_app': forms.TextInput(attrs={'pattern': '\d*', 'min': '0'}),
        }


class CadastroPreReserva(forms.ModelForm):
    class Meta:
        model = FichaDeEvento
        fields = [
            'cliente', 'responsavel_evento', 'produto', 'produto_corporativo',
            'check_in', 'check_out', 'qtd_convidada', 'observacoes', 'exclusividade',
            'vendedora', 'pre_reserva', 'agendado', 'obs_edicao_horario', 'agencia', 'id_negocio'
        ]

        widgets = {
            'cliente': forms.Select(attrs={'onChange': 'gerar_responsaveis(this)'}),
            'produto': forms.Select(attrs={'onChange': 'dadosProduto()'}),
            'produto_corporativo': forms.Select(attrs={'onChange': 'corporativo(this, true)'}),
            'qtd_convidada': forms.NumberInput(attrs={'onChange': 'atualizar_lotacao(this.value)'}),
            'agencia': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'exclusividade': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
                'onchange': 'verificar_evento_dia_exclusividade()'
            }),
            'check_in': forms.TextInput(attrs={
                'type': 'datetime-local',
                'onChange': 'pegarDias(true)',
                'onkeyup': '$("#ModalCadastroPreReserva #id_check_in").val("")',
                'onclick': 'this.showPicker()'
            }),
            'check_out': forms.TextInput(attrs={
                'type': 'datetime-local',
                'onChange': 'pegarDias(true)',
                'onkeyup': '$("#ModalCadastroPreReserva #id_check_out").val("")',
                'onclick': 'this.showPicker()'
            }),
            # 'id_negocio': forms.TextInput(attrs={'required': 'required', 'onchange': 'verificar_id_negocio(this)'})
        }

    def __init__(self, *args, **kwargs):
        super(CadastroPreReserva, self).__init__(*args, **kwargs)
        clientes = ClienteColegio.objects.all()
        responsaveis = Responsavel.objects.all()
        responsaveis_cargo = [('', '')]
        clientes_cnpj = [('', '')]

        for cliente in clientes:
            clientes_cnpj.append((cliente.id, f'{cliente} ({cliente.cnpj})'))

        for responsavel in responsaveis:
            cargos = []

            for cargo in responsavel.cargo.all():
                if cargo != '':
                    cargos.append(cargo.cargo)

            if len(cargos) > 0:
                responsaveis_cargo.append((responsavel.id, f'{responsavel.nome} ({", ".join(cargos)})'))
            else:
                responsaveis_cargo.append((responsavel.id, responsavel.nome))

        self.fields['cliente'].choices = clientes_cnpj
        self.fields['responsavel_evento'].choices = responsaveis_cargo


class MonitorAdminForm(forms.ModelForm):
    class Meta:
        model = Monitor
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(MonitorAdminForm, self).__init__(*args, **kwargs)
        self.fields['nivel_acampamento'].queryset = NivelMonitoria.objects.filter(setor_monitoria__setor='Acampamento').order_by('id')
        self.fields['nivel_hotelaria'].queryset = NivelMonitoria.objects.filter(setor_monitoria__setor='Hotelaria').order_by('id')
        self.fields['nivel_corporativo'].queryset = NivelMonitoria.objects.filter(setor_monitoria__setor='Hotelaria').order_by('id')
        self.fields['nivel_tecnica'].queryset = NivelMonitoria.objects.filter(setor_monitoria__setor='Técnica').order_by('id')


class EnfermeiraAdminForm(forms.ModelForm):
    class Meta:
        model = Monitor
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(EnfermeiraAdminForm, self).__init__(*args, **kwargs)
        self.fields['nivel'].queryset = NivelMonitoria.objects.filter(setor_monitoria__setor='Enfermagem').order_by('id')
