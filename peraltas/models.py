import datetime
from collections import defaultdict
from heapq import nlargest

import reversion
from django import forms
from django.contrib.contenttypes.models import ContentType
from django.contrib.postgres.fields import JSONField
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.db.models import ManyToManyField
from django.utils import timezone
from reversion.models import Version

from ceu.models import Atividades, Locaveis


class NivelMonitoria(models.Model):
    nivel = models.CharField(max_length=100)

    def __str__(self):
        return self.nivel


class Monitor(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE)
    telefone = models.CharField(max_length=11)
    cidade_horigem = models.CharField(max_length=255, verbose_name='Moradia', blank=True)
    valor_diaria = models.DecimalField(null=True, decimal_places=2, max_digits=5)
    valor_diaria_coordenacao = models.DecimalField(null=True, decimal_places=2, max_digits=5)
    valor_diaria_biologo = models.DecimalField(null=True, decimal_places=2, max_digits=5)
    nivel = models.ForeignKey(NivelMonitoria, on_delete=models.DO_NOTHING, default=1)
    aceite_do_termo = models.BooleanField(default=False)
    biologo = models.BooleanField(default=False)
    tecnica = models.BooleanField(default=False)
    som = models.BooleanField(default=False)
    video = models.BooleanField(default=False)
    fotos_e_filmagens = models.BooleanField(default=False)
    fixo = models.BooleanField(default=False)
    nota = models.FloatField(default=0.00)
    n_avaliacoes = models.IntegerField(default=0)

    def __str__(self):
        return self.usuario.get_full_name()

    def nome_completo(self):
        return self.usuario.get_full_name()


class Enfermeira(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE)
    telefone = models.CharField(max_length=11)
    valor_diaria = models.DecimalField(null=True, decimal_places=2, max_digits=5)
    valor_pernoite = models.DecimalField(null=True, decimal_places=2, max_digits=5)
    pode_pernoitar = models.BooleanField(default=False)

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
    nivel_atividade = models.ForeignKey(NivelMonitoria, on_delete=models.DO_NOTHING, verbose_name='Nível da atividade')
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


@reversion.register
class CodigosApp(models.Model):
    cliente_pj = models.IntegerField()
    cliente_pf = models.IntegerField()
    evento = models.CharField(max_length=255)
    reserva = models.CharField(max_length=255)
    pagamento = models.IntegerField(null=True, blank=True)

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
        on_delete=models.DO_NOTHING,
        blank=True, null=True,
        related_name='responsavel_alteracao'
    )
    responsavel_cadastro = models.ForeignKey(
        User,
        on_delete=models.DO_NOTHING,
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
    responsavel_cadastro = models.ForeignKey(User,
                                             on_delete=models.DO_NOTHING,
                                             blank=True, null=True,
                                             related_name='responsavel_cadastro')
    responsavel_atualizacao = models.ForeignKey(User,
                                                on_delete=models.DO_NOTHING,
                                                blank=True, null=True,
                                                related_name='responsavel_atualizacao')

    def __str__(self):
        return self.nome

    def responsavel_por(self):
        relacao = RelacaoClienteResponsavel.objects.get(responsavel=self)

        return relacao.cliente

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
    motivo_cancelamento = models.TextField()

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


@reversion.register
class InformacoesAdcionais(models.Model):
    tipos_monitoria = (
        (1, '1/2 monitoria (fora de quarto - 1/20)'),
        (2, '1/2 monitoria (dentro de quarto - 1/20'),
        (3, 'Monitoria completa (em quarto - 1/12)')
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


class RelacaoClienteResponsavel(models.Model):
    cliente = models.ForeignKey(ClienteColegio, on_delete=models.CASCADE)
    responsavel = models.ManyToManyField(Responsavel)


@reversion.register
class FichaDeEvento(models.Model):
    empresa_choices = (
        ('Peraltas', 'Peraltas'),
        ('CEU', 'Fundação CEU'),
        ('Peraltas CEU', 'Peraltas + Fundação CEU')
    )

    cliente = models.ForeignKey(ClienteColegio, on_delete=models.CASCADE, verbose_name='Cliente')
    responsavel_evento = models.ForeignKey(Responsavel, on_delete=models.CASCADE, verbose_name='Responsável pelo evento')
    produto = models.ForeignKey(ProdutosPeraltas, on_delete=models.DO_NOTHING, verbose_name='Produto')
    produto_corporativo = models.ForeignKey(ProdutoCorporativo, on_delete=models.CASCADE, blank=True, null=True,
                                            verbose_name='Produto corporativo')
    check_in = models.DateTimeField(verbose_name='Check in')
    check_out = models.DateTimeField(verbose_name='Check out')
    obs_edicao_horario = models.CharField(max_length=255, blank=True, null=True, verbose_name='Observação da edição do horário')
    professores_com_alunos = models.BooleanField(default=False, verbose_name='Professores dormirão com alunos?')
    qtd_professores = models.PositiveIntegerField(blank=True, null=True, verbose_name='Quantidade de professores')
    qtd_profs_homens = models.PositiveIntegerField(blank=True, null=True, verbose_name='Quantidade de professores homens')
    qtd_profs_mulheres = models.PositiveIntegerField(blank=True, null=True, verbose_name='Quantidade de professores mulheres')
    qtd_convidada = models.PositiveIntegerField(blank=True, null=True, verbose_name='Quantidade reservada')
    qtd_confirmada = models.PositiveIntegerField(blank=True, null=True, verbose_name='Quantidade confirmada')
    qtd_meninos = models.PositiveIntegerField(blank=True, null=True, verbose_name='Quantidade de menino')
    qtd_meninas = models.PositiveIntegerField(blank=True, null=True, verbose_name='Quantidade de meninas')
    qtd_homens = models.PositiveIntegerField(blank=True, null=True, verbose_name='Quantidade de homens')
    qtd_mulheres = models.PositiveIntegerField(blank=True, null=True, verbose_name='Quantidade de mulheres')
    perfil_participantes = models.ManyToManyField(PerfilsParticipantes, blank=True, verbose_name='Perfíl dos participantes')
    refeicoes = models.JSONField(blank=True, null=True, verbose_name='Refeições')
    observacoes_refeicoes = models.TextField(blank=True, null=True, verbose_name='Observações das refeições')
    informacoes_adcionais = models.ForeignKey(InformacoesAdcionais, on_delete=models.CASCADE, blank=True, null=True, verbose_name='Informações adicionais')
    observacoes = models.TextField(blank=True, verbose_name='Observações')
    atividades_ceu = models.ManyToManyField(Atividades, blank=True, verbose_name='Atividades CEU')
    atividades_ceu_a_definir = models.IntegerField(blank=True, null=True, verbose_name='Atividades CEU a definir')
    locacoes_ceu = models.ManyToManyField(Locaveis, blank=True, verbose_name='Locações no CEU')
    informacoes_locacoes = models.JSONField(blank=True, null=True, verbose_name='Informações de locações')
    atividades_eco = models.ManyToManyField(AtividadesEco, blank=True, verbose_name='Atividades extra')
    atividades_peraltas = models.ManyToManyField(GrupoAtividade, blank=True, verbose_name='Atividades Peraltas')
    vendedora = models.ForeignKey(Vendedor, on_delete=models.CASCADE, verbose_name='Vendedora')  # TODO: Verificar caso de exclusão de colaborador
    data_final_inscricao = models.DateField(blank=True, null=True, verbose_name='Data final da inscrição')
    data_divulgacao = models.DateField(blank=True, null=True, verbose_name='Data prevista para divulgação')
    empresa = models.CharField(choices=empresa_choices, max_length=100, blank=True, null=True, verbose_name='Empresa')
    material_apoio = models.FileField(blank=True, null=True, upload_to='materiais_apoio/%Y/%m/%d', verbose_name='Material de apoio')
    data_preenchimento = models.DateField(blank=True, null=True, editable=False, verbose_name='Data de preenchimento')
    codigos_app = models.ForeignKey(CodigosApp, on_delete=models.DO_NOTHING, blank=True, null=True, verbose_name='Códigos APP')
    exclusividade = models.BooleanField(default=False, verbose_name='Exclusividade')
    pre_reserva = models.BooleanField(default=False, verbose_name='Pré reserva')
    agendado = models.BooleanField(default=False, verbose_name='Agendado')
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

    # -------------------------------- Funçõs do para o LOG das fichas de evento ---------------------------------------
    @classmethod
    def logs_de_alteracao(cls):
        dados_alterados = []

        pre_alteracoes = (
            Version.objects
            .get_for_model(cls)
            .select_related('revision')
            .order_by('-revision__date_created')[:100]
        )

        versoes_agrupadas = cls.__agrupar_versoes(pre_alteracoes)
        # cls.teste()

        for obj, versoes in versoes_agrupadas.items():
            campos_alterados = []

            if obj == 'excluidas':
                for versao in versoes:
                    motivo_cancelamento = cls.__pegar_motivo_cancelamento(versao.field_dict['cliente_id'])
                    dados_alterados.append({
                        'ficha': {
                            'ficha': versao,
                            'id_ficha': '',
                        },
                        'campos_alterados': 'excluido',
                        'motivo': motivo_cancelamento,
                        'colaborador': versao.revision.user.get_full_name() if versao.revision.user else '',
                        'data_e_hora': timezone.localtime(versao.revision.date_created).strftime('%d/%m/%Y às %H:%M')
                    })

                continue

            if len(versoes) == 1 or (versoes[1].field_dict['pre_reserva'] and not versoes[0].field_dict['pre_reserva']):
                versao = versoes[0]

                dados_alterados.append({
                    'ficha': {
                        'ficha': versao,
                        'id_ficha': versao.object.id,
                    },
                    'campos_alterados': '',
                    'colaborador': versao.revision.user.get_full_name() if versao.revision.user else '',
                    'data_e_hora': timezone.localtime(versao.revision.date_created).strftime('%d/%m/%Y às %H:%M')
                })
            else:
                versao_atual = versoes[0]
                versao_anterior = versoes[1]

                campos_alterados.extend(cls.__comparar_campos_simples(versao_atual, versao_anterior))
                campos_alterados.extend(cls.__comparar_many_to_many(versao_atual, versao_anterior))

                dados_alterados.append({
                    'ficha': {
                        'ficha': versao_atual.object,
                        'id_ficha': versao_atual.object.id,
                    },
                    'campos_alterados': campos_alterados,
                    'colaborador': versao_atual.revision.user.get_full_name(),
                    'data_e_hora': timezone.localtime(versao_atual.revision.date_created).strftime(
                        '%d/%m/%Y às %H:%M')
                })

        return dados_alterados

    @staticmethod
    def __pegar_motivo_cancelamento(id_cliente):
        cliente = ClienteColegio.objects.get(pk=id_cliente)
        evento_cancelado = EventosCancelados.objects.filter(cnpj_cliente=cliente.cnpj).last()

        return evento_cancelado.motivo_cancelamento

    @staticmethod
    def teste():
        pre_alteracoes = (
            Version.objects
            .get_for_model(FichaDeEvento)
            .select_related('revision')
            .order_by('-revision__date_created')[1]
        )

        previous_version = pre_alteracoes.revision.get_previous()
        diff = pre_alteracoes.difference()

        print(diff)

    @staticmethod
    def __agrupar_versoes(pre_alteracoes):
        versoes_agrupadas = defaultdict(list)
        excluidas = []

        for versao in pre_alteracoes:
            try:
                ficha = versao.content_type.get_object_for_this_type(pk=versao.object_id)
            except ObjectDoesNotExist:
                ...
            else:
                if versao not in versoes_agrupadas['excluidas']:
                    if not ficha.pre_reserva and versao.revision.user and len(versoes_agrupadas) < 10:
                        versoes_agrupadas[ficha].append(versao)

        versoes_agrupadas['excluidas'] = excluidas

        for obj, versoes in versoes_agrupadas.items():
            versoes_agrupadas[obj] = nlargest(2, versoes, key=lambda x: x.revision.date_created)

        return versoes_agrupadas

    @staticmethod
    def __comparar_campos_simples(versao_atual, versao_anterior):
        campos_alterados = []

        for campo in versao_atual.object.get_all_fields():
            if versao_atual.object.get_field_type(campo) == 'ForeignKey':
                valor_anterior = versao_anterior.field_dict[f'{campo}_id']
                valor_atual = versao_atual.field_dict[f'{campo}_id']

                if campo == 'vendedora':
                    valor_anterior = Vendedor.objects.get(pk=valor_anterior).usuario.get_full_name()
                    valor_atual = Vendedor.objects.get(pk=valor_atual).usuario.get_full_name()
            else:
                valor_anterior = versao_anterior.field_dict[campo]
                valor_atual = versao_atual.field_dict[campo]

            if valor_anterior != valor_atual:
                campo_alterado = {
                    'campo': {
                        'nome_campo': versao_atual.object.get_field_verbose_name(campo),
                        'valor_anterior': valor_anterior,
                        'novo_valor': valor_atual,
                        'tipo_campo': versao_atual.object.get_field_type(campo)
                    }
                }

                campos_alterados.append(campo_alterado)

        return campos_alterados

    @staticmethod
    def __comparar_many_to_many(versao_atual, versao_anterior):
        campos_alterados = []
        campos_m2m = versao_atual.object._meta.many_to_many

        for campo in campos_m2m:
            campo_nome = campo.name
            campo_verbose_name = campo.verbose_name
            campo_tipo = campo.remote_field.model.__name__

            if campo_nome not in versao_atual.field_dict or campo_nome not in versao_anterior.field_dict:
                continue

            ids_anterior = versao_anterior.field_dict[campo_nome]
            ids_atual = versao_atual.field_dict[campo_nome]

            valores_anterior = []
            valores_atual = []

            if ids_anterior != ids_atual:
                model_class = campo.remote_field.model

                if len(ids_atual) > 0:
                    objetos_atual = model_class.objects.filter(pk__in=ids_atual)
                    valores_atual = [str(objeto) for objeto in objetos_atual]

                if len(ids_anterior) > 0:
                    objetos_anterior = model_class.objects.filter(pk__in=ids_anterior)
                    valores_anterior = [str(objeto) for objeto in objetos_anterior]

                campo_alterado = {
                    'campo': {
                        'nome_campo': campo_verbose_name,
                        'valor_anterior': ', '.join(valores_anterior) if valores_anterior else '"Vazio"',
                        'novo_valor': ', '.join(valores_atual) if valores_atual else '"Vazio"',
                        'tipo_campo': campo_tipo
                    }
                }

                campos_alterados.append(campo_alterado)

        return campos_alterados

    @staticmethod
    def __comparar_json_field(versao_atual, versao_anterior):
        campos_alterados = []

        for campo in versao_atual.object.get_all_fields():
            if versao_atual.object.get_field_type(campo) == 'JSONField':
                valor_anterior = versao_anterior.field_dict[campo]
                valor_atual = versao_atual.field_dict[campo]

                if valor_atual != valor_anterior:
                    campo_alterado = {
                        'campo': {
                            'nome_campo': campo,
                            'valor_anterior': '',
                            'novo_valor': '',
                            'tipo_campo': 'JSONField'
                        }
                    }

                    campos_alterados.append(campo_alterado)

            return campos_alterados
    # ------------------------------------------------------------------------------------------------------------------

    def tabelar_refeicoes(self):
        dados = []

        for dia in self.refeicoes:
            dados_refeicoes = []

            dados_refeicoes = [
                'Café' in self.refeicoes[dia],
                'Coffee manhã' in self.refeicoes[dia],
                'Almoço' in self.refeicoes[dia],
                'Lanche tarde' in self.refeicoes[dia],
                'Coffee tarde' in self.refeicoes[dia],
                'Jantar' in self.refeicoes[dia],
                'Lanche noite' in self.refeicoes[dia],
            ]

            dados.append({'dia': dia, 'refeicoes': dados_refeicoes})

        return dados

    def juntar_refeicoes(self):
        dados = []

        for dia in self.refeicoes:
            dados_refeicoes = []

            dados_refeicoes.append('Café da manhã') if 'Café' in self.refeicoes[dia] else ...
            dados_refeicoes.append('Coffee manhã') if 'Coffee manhã' in self.refeicoes[dia] else ...
            dados_refeicoes.append('Almoço') if 'Almoço' in self.refeicoes[dia] else ...
            dados_refeicoes.append('Lanche da tarde') if 'Lanche tarde' in self.refeicoes[dia] else ...
            dados_refeicoes.append('Coffee tarde') if 'Coffee tarde' in self.refeicoes[dia] else ...
            dados_refeicoes.append('Jantar') if 'Jantar' in self.refeicoes[dia] else ...
            dados_refeicoes.append('Lanche da noite') if 'Lanche noite' in self.refeicoes[dia] else ...

            dados.append({'dia': dia, 'refeicoes': ', '.join(dados_refeicoes)})

        return dados

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
    ordem_de_servico = models.ForeignKey('ordemDeServico.OrdemDeServico', on_delete=models.CASCADE, null=True,
                                         blank=True)
    ficha_de_evento = models.ForeignKey(FichaDeEvento, on_delete=models.CASCADE, null=True, blank=True)

    class Meta:
        verbose_name_plural = 'Eventos'

    def vendedor(self):
        return self.ficha_de_evento.vendedora.usuario.get_full_name()

    def cliente(self):
        return self.ficha_de_evento.cliente

    def check_in(self):
        return self.ordem_de_servico.check_in if self.ordem_de_servico else self.ficha_de_evento.check_in

    def check_out(self):
        return self.ordem_de_servico.check_out if self.ordem_de_servico else self.ficha_de_evento.check_out

    def qtd_confirmada(self):
        return self.ordem_de_servico.n_participantes if self.ordem_de_servico else self.ficha_de_evento.qtd_confirmada

    def qtd_previa(self):
        return self.ficha_de_evento.qtd_convidada

    def data_preenchimento(self):
        return self.ordem_de_servico.data_preenchimento if self.ordem_de_servico else self.ficha_de_evento.data_preenchimento

    def estagio_evento(self):
        if self.ordem_de_servico:
            return 'Ordem de Servico'
        else:
            if self.ficha_de_evento.pre_reserva and not self.ficha_de_evento.agendado:
                return 'Pré reserva'
            elif self.ficha_de_evento.pre_reserva and self.ficha_de_evento.agendado:
                return 'Evento confirmado'
            else:
                return 'Ficha de evento'

    def codigo_pagamento(self):
        if not self.ficha_de_evento.pre_reserva:
            return self.ficha_de_evento.codigos_app.evento
        else:
            return ''


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

    def tipo_escala(self):
        if self.ficha_de_evento.produto.colegio:
            return "Colégio"
        else:
            return 'Corporativo'


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
            'evento': forms.TextInput(attrs={'onkeyup': 'this.value=this.value.toUpperCase()'}),
            'reserva': forms.TextInput(attrs={'pattern': '\d*', 'minlength': '6', 'maxlength': '6'}),
        }


class CadastroPreReserva(forms.ModelForm):
    class Meta:
        model = FichaDeEvento
        fields = [
            'cliente', 'responsavel_evento', 'produto', 'produto_corporativo',
            'check_in', 'check_out', 'qtd_convidada', 'observacoes', 'exclusividade',
            'vendedora', 'pre_reserva', 'agendado', 'obs_edicao_horario'
        ]

        widgets = {
            'cliente': forms.Select(attrs={'onChange': 'gerar_responsaveis(this)'}),
            'produto': forms.Select(attrs={'onChange': 'dadosProduto()'}),
            'produto_corporativo': forms.Select(attrs={'onChange': 'corporativo(this, true)'}),
            'qtd_convidada': forms.NumberInput(attrs={'onChange': 'atualizar_lotacao(this.value)'}),
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
