# Importações necessárias
from django.contrib.auth.models import User
from django.test import TestCase
from peraltas.models import ProdutosPeraltas
from .models import OrcamentosPromocionais, DadosDePacotes, Orcamento, StatusOrcamento, OrcamentoMonitor
import datetime
import factory


# Definindo Factories
class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    username = factory.Sequence(lambda n: f'testuser{n}')
    email = 'testuser@example.com'
    password = factory.PostGenerationMethodCall('set_password', 'testpassword')


class DadosDePacotesFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = DadosDePacotes

    nome_do_pacote = 'Pacote Teste'
    limite_desconto_geral = 0
    minimo_de_diarias = 1
    maximo_de_diarias = 3
    minimo_de_pagantes = 25
    cortesia = False
    periodos_aplicaveis = [
        {"periodo_1": "01/12/2023 - 01/12/2023"},
        {"periodo_2": "04/12/2023 - 08/12/2023"},
        {"periodo_3": "11/12/2023 - 15/12/2023"},
        {"periodo_4": "18/12/2023 - 22/12/2023"},
        {"periodo_5": "25/12/2023 - 29/12/2023"},
        {"periodo_5": "20/06/2024 - 20/07/2024"},
    ]
    descricao = 'teste'


class StatusOrcamentoFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = StatusOrcamento

    status = 'Em Aberto'


class OrcamentoMonitorFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = OrcamentoMonitor

    nome_monitoria = 'Teste'
    descricao_monitoria = 'Teste'
    valor = 200.00
    inicio_vigencia = datetime.datetime(2020, 1, 1)


class OrcamentoFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Orcamento

    transporte = 'sim'
    desconto = 0.0
    promocional = True
    tipo_monitoria = factory.SubFactory(OrcamentoMonitorFactory)
    colaborador = factory.SubFactory(UserFactory)
    valor = 1000.0
    status_orcamento = factory.SubFactory(StatusOrcamentoFactory)
    data_vencimento = datetime.date.today() + datetime.timedelta(days=10)
    check_in = datetime.datetime(
        datetime.datetime.today().year,
        datetime.datetime.today().month,
        datetime.datetime.today().day
    )
    check_out = datetime.datetime(
        datetime.datetime.today().year,
        datetime.datetime.today().month,
        datetime.datetime.today().day + 2
    )
    produto_id = 1


class ProdutosPeraltasFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ProdutosPeraltas

    produto = 'Produto Teste'
    pernoite = colegio = brotas_eco = meninos_e_meninas = True


class OrcamentosPromocionaisFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = OrcamentosPromocionais

    dados_pacote = factory.SubFactory(DadosDePacotesFactory)
    orcamento = factory.SubFactory(OrcamentoFactory)


class OrcamentosPromocionaisTestCase(TestCase):
    def setUp(self):
        # Cria os objetos necessários para os testes usando factories
        self.dados_pacote = DadosDePacotesFactory()
        self.status = StatusOrcamentoFactory()
        self.user = UserFactory()
        self.tipo_monitor = OrcamentoMonitorFactory()
        self.orcamento = OrcamentoFactory()
        self.produto_elegivel = ProdutosPeraltasFactory()
        self.dados_pacote.produtos_elegiveis.add(self.produto_elegivel)
        self.orcamento_promocional = OrcamentosPromocionaisFactory(
            dados_pacote=self.dados_pacote,
            orcamento=self.orcamento
        )

    def test_pegar_pacotes_promocionais(self):
        # Define os parâmetros de teste
        n_dias = 2
        id_produto = self.produto_elegivel.id
        check_in = datetime.datetime(
            datetime.datetime.today().year,
            datetime.datetime.today().month,
            datetime.datetime.today().day
        ).strftime('%Y-%m-%d %H:%M')
        check_out = datetime.datetime(
            datetime.datetime.today().year,
            datetime.datetime.today().month,
            datetime.datetime.today().day + 1
        ).strftime('%Y-%m-%d %H:%M')

        # Chama o método pegar_pacotes_promocionais
        pacotes = OrcamentosPromocionais.pegar_pacotes_promocionais(n_dias, id_produto, check_in, check_out)

        # Verifica se o pacote esperado está na lista de pacotes válidos
        self.assertEqual(len(pacotes), 1)
        self.assertEqual(pacotes[0]['id'], self.orcamento_promocional.id)
        self.assertEqual(pacotes[0]['nome'], 'Pacote Teste')

    def test_pegar_pacotes_promocionais_data_invalida(self):
        # Define os parâmetros de teste com datas inválidas
        n_dias = 2
        id_produto = self.produto_elegivel.id
        check_in = '2024-01-01 14:00'
        check_out = '2024-01-06 12:00'

        # Chama o método pegar_pacotes_promocionais
        pacotes = OrcamentosPromocionais.pegar_pacotes_promocionais(n_dias, id_produto, check_in, check_out)

        # Verifica se a lista de pacotes válidos está vazia
        self.assertEqual(len(pacotes), 0)

    def test_pegar_pacotes_promocionais_produto_invalido(self):
        # Define os parâmetros de teste com produto inválido
        n_dias = 1
        id_produto = 9999  # ID de um produto que não existe
        check_in = '2023-06-15 14:00'
        check_out = '2023-06-20 12:00'

        # Chama o método pegar_pacotes_promocionais
        pacotes = OrcamentosPromocionais.pegar_pacotes_promocionais(n_dias, id_produto, check_in, check_out)

        # Verifica se a lista de pacotes válidos está vazia
        self.assertEqual(len(pacotes), 0)
