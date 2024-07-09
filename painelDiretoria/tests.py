# test_eventos.py
from datetime import datetime
from random import choice, randint

import factory
from django.contrib.auth.models import User, Permission
from django.test import TestCase
from django.core.management import call_command
from django.urls import reverse
from django.utils import timezone

from ordemDeServico.models import OrdemDeServico
from peraltas.models import Eventos, FichaDeEvento, ClienteColegio, Responsavel, ProdutosPeraltas, Vendedor


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    username = factory.Sequence(lambda n: f'testuser{n}')
    email = 'testuser@example.com'
    password = factory.PostGenerationMethodCall('set_password', 'testpassword')


class ClienteColegioFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ClienteColegio

    razao_social = factory.Faker('company')
    cnpj = factory.Sequence(lambda n: f'123456780001{n:02d}')
    nome_fantasia = factory.Faker('company_suffix')
    endereco = factory.Faker('street_address')
    bairro = factory.Faker('city')
    cidade = factory.Faker('city')
    estado = factory.Faker('state_abbr')
    cep = factory.Faker('postcode')
    responsavel_alteracao = factory.SubFactory(UserFactory)
    responsavel_cadastro = factory.SubFactory(UserFactory)


class ResponsavelFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Responsavel

    nome = factory.Faker('name')
    fone = factory.Faker('phone_number')
    email_responsavel_evento = factory.Faker('email')

    # Relacionamento many-to-many com ListaDeCargos
    @factory.post_generation
    def cargo(self, create, extracted, **kwargs):
        if not create:
            # Apenas para evitar a criação automática de cargos
            return

        if extracted:
            for cargo in extracted:
                self.cargo.add(cargo)

    # Relacionamento com User (responsavel_cadastro e responsavel_atualizacao)
    responsavel_cadastro = factory.SubFactory(UserFactory)
    responsavel_atualizacao = factory.SubFactory(UserFactory)


class ProdutosPeraltasFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ProdutosPeraltas

    produto = factory.Faker('word')
    pernoite = factory.Faker('boolean')
    colegio = factory.Faker('boolean')
    brotas_eco = factory.Faker('boolean')
    meninos_e_meninas = factory.Faker('boolean')

    # Campos adicionais
    n_dias = factory.Faker('random_int', min=1, max=10)  # Exemplo de geração aleatória
    hora_padrao_check_in = factory.Faker('time')
    hora_padrao_check_out = factory.Faker('time')


class VendedorFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Vendedor

    usuario = factory.SubFactory(UserFactory)
    telefone = factory.Faker('phone_number')
    supervisor = factory.Faker('boolean')
    nota = factory.Faker('pyfloat', left_digits=2, right_digits=2, positive=True)
    n_avaliacoes = factory.Faker('random_int', min=0, max=100)


class FichaDeEventoFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = FichaDeEvento

    cliente = factory.SubFactory(ClienteColegioFactory)
    responsavel_evento = factory.SubFactory(ResponsavelFactory)
    produto = factory.SubFactory(ProdutosPeraltasFactory)
    check_in = factory.Faker('date_time_this_year')
    check_out = factory.Faker('date_time_this_year')
    vendedora = factory.SubFactory(VendedorFactory)
    empresa = factory.Iterator(['Peraltas', 'CEU', 'Peraltas CEU'])
    data_preenchimento = timezone.now()


class OrdemDeServicoFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = OrdemDeServico

    tipo = factory.Iterator(['Colégio', 'Empresa'])
    ficha_de_evento = factory.SubFactory(FichaDeEventoFactory)
    instituicao = factory.Faker('company')
    cidade = factory.Faker('city')
    check_in = factory.Faker('date_time_this_year')
    check_out = factory.Faker('date_time_this_year')
    n_participantes = factory.Faker('random_int', min=1, max=100)
    responsavel_grupo = factory.Faker('name')
    empresa = factory.Iterator(['Peraltas', 'CEU', 'Peraltas CEU'])


class EventosFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Eventos

    colaborador = factory.SubFactory(VendedorFactory)
    cliente = factory.SubFactory(ClienteColegioFactory)
    data_check_in = factory.Faker('date_this_decade', before_today=True)
    hora_check_in = factory.Faker('time')
    data_check_out = factory.LazyAttribute(lambda o: o.data_check_in + timezone.timedelta(days=o.dias_evento))
    hora_check_out = factory.Faker('time')
    qtd_previa = factory.Faker('random_int', min=10, max=100)
    qtd_confirmado = factory.Faker('random_int', min=10, max=100)
    data_preenchimento = factory.Faker('date_this_decade')
    estagio_evento = factory.Faker('random_element',
                                   elements=['pre_reserva', 'confirmado', 'ficha_evento', 'ordem_servico'])
    codigo_pagamento = factory.Faker('bothify', text='#######')
    tipo_evento = factory.Faker('random_element', elements=['Colégio', 'Empresa'])
    dias_evento = factory.Faker('random_int', min=1, max=5)
    produto_peraltas = factory.SubFactory(ProdutosPeraltasFactory)
    adesao = factory.Faker('pyfloat', left_digits=2, right_digits=2, positive=True)
    veio_ano_anterior = factory.Faker('boolean')


class EventosTestCase(TestCase):
    def setUp(self):
        self.cliente1 = ClienteColegioFactory()
        self.cliente2 = ClienteColegioFactory()

        # Criando eventos fictícios para testar o método
        self.evento1 = EventosFactory(
            estagio_evento='pre_reserva',
            data_check_in=datetime(2024, 7, 1),
            qtd_previa=10,
            qtd_confirmado=8,
            cliente=self.cliente1,
        )
        self.evento2 = EventosFactory(
            estagio_evento='confirmado',
            data_check_in=datetime(2024, 7, 15),
            qtd_previa=15,
            qtd_confirmado=12,
            cliente=self.cliente2,
        )

    def test_preparar_relatorio_clientes_mes_estagios_pre_reserva(self):
        mes = 'Julho'
        ano = 2024

        # Chamando o método que queremos testar
        relatorio = Eventos.preparar_relatorio_clientes_mes_estagios('pre_reserva', mes, ano)

        # Verificando se o relatório foi gerado corretamente
        self.assertEqual(len(relatorio['relatorio']), 1)  # Verifica se há apenas um evento no relatório
        self.assertEqual(relatorio['estagio'], 'Pré reserva')  # Verifica se o estágio está correto

        # Verificando detalhes do evento no relatório
        evento_relatorio = relatorio['relatorio'][0]
        self.assertEqual(evento_relatorio['cliente'], self.cliente1.__str__())  # Verifica o cliente
        self.assertEqual(evento_relatorio['reservado'], 10)  # Verifica a quantidade previamente reservada
        self.assertEqual(evento_relatorio['confirmado'], 8)  # Verifica a quantidade confirmada

    def test_preparar_relatorio_clientes_mes_estagios_confirmado(self):
        mes = 'Julho'
        ano = 2024
        # Testando para outro estágio
        relatorio_confirmado = Eventos.preparar_relatorio_clientes_mes_estagios('confirmado', mes, ano)
        self.assertEqual(len(relatorio_confirmado['relatorio']), 1)  # Verifica se há apenas um evento no relatório
        self.assertEqual(relatorio_confirmado['estagio'], 'Evento confirmado')  # Verifica se o estágio está correto

        evento_relatorio_confirmado = relatorio_confirmado['relatorio'][0]
        self.assertEqual(evento_relatorio_confirmado['cliente'], self.cliente2.__str__())  # Verifica o cliente
        self.assertEqual(evento_relatorio_confirmado['reservado'], 15)  # Verifica a quantidade previamente reservada
        self.assertEqual(evento_relatorio_confirmado['confirmado'], 12)  # Verifica a quantidade confirmada

    def tester_preparar_relatorio_clientes_mes_sem_resultado_para_o_ano(self):
        mes = 'Julho'
        ano = 2025

        relatorio = Eventos.preparar_relatorio_clientes_mes_estagios('confirmado', mes, ano)
        self.assertEqual(len(relatorio['relatorio']), 0)

    def tester_preparar_relatorio_clientes_mes_sem_resultado_para_o_mes(self):
        mes = 'Agosto'
        ano = 2024

        relatorio = Eventos.preparar_relatorio_clientes_mes_estagios('confirmado', mes, ano)
        self.assertEqual(len(relatorio['relatorio']), 0)

    def tester_preparar_relatorio_clientes_mes_sem_resultado_para_o_estagio(self):
        mes = 'Julho'
        ano = 2024

        relatorio = Eventos.preparar_relatorio_clientes_mes_estagios('ficha_evento', mes, ano)
        self.assertEqual(len(relatorio['relatorio']), 0)


class PerformanceTest(TestCase):
    def setUp(self):
        self.cliente = ClienteColegioFactory()

        for _ in range(100):  # Criar 100 eventos para simular carga
            random_day = randint(1, 31)
            random_date = datetime(2024, 7, random_day)

            evento = EventosFactory(
                estagio_evento=choice(['pre_reserva', 'confirmado', 'ficha_evento', 'ordem_servico']),
                data_check_in=random_date,
                qtd_previa=10,
                qtd_confirmado=8,
                cliente=self.cliente,
            )

    def test_performance_preparar_relatorio_clientes_mes_sem_resultado(self):
        """
        Testar o desempenho do método preparar_relatorio_clientes_mes_estagios
        para eventos confirmados no mês de janeiro de 2023.
        """
        start_time = datetime.now()
        relatorio = Eventos.preparar_relatorio_clientes_mes_estagios('confirmado', 'Janeiro', 2024)
        end_time = datetime.now()
        execution_time = (end_time - start_time).total_seconds()

        print(f"Tempo de execução em caso de nenhum resultado: {execution_time} segundos")

        # Verificar se o relatório está no formato esperado
        self.assertEqual(len(relatorio['relatorio']), 0)
        self.assertTrue('relatorio' in relatorio)
        self.assertTrue('estagio' in relatorio)

        # Verificar se o relatório possui 100 entradas (um para cada evento criado)
        self.assertLess(len(relatorio['relatorio']), 100)

    def test_performance_preparar_relatorio_clientes_mes_com_resultado(self):
        """
        Testar o desempenho do método preparar_relatorio_clientes_mes_estagios
        para eventos confirmados no mês de janeiro de 2023.
        """
        start_time = datetime.now()
        relatorio = Eventos.preparar_relatorio_clientes_mes_estagios('confirmado', 'Julho', 2024)
        end_time = datetime.now()
        execution_time = (end_time - start_time).total_seconds()

        print(f"Tempo de execução em caso de resultados encontrados: {execution_time} segundos")

        # Verificar se o relatório está no formato esperado
        self.assertGreaterEqual(len(relatorio['relatorio']), 1)
        self.assertTrue('relatorio' in relatorio)
        self.assertTrue('estagio' in relatorio)

        # Verificar se o relatório possui 100 entradas (um para cada evento criado)
        self.assertLess(len(relatorio['relatorio']), 100)


class SecurityTest(TestCase):
    def setUp(self):
        self.user_with_permission = User.objects.create_user(username='user_with_permission', password='password')
        self.permission = Permission.objects.get(codename='view_eventos')  # Substitua com a sua permissão
        self.user_with_permission.user_permissions.add(self.permission)

        # Criando um usuário sem permissão
        self.user_without_permission = User.objects.create_user(username='user_without_permission', password='password')

    def test_usuario_logado_com_permissao(self):
        # Loga o usuário com permissão
        self.client.login(username='user_with_permission', password='password')

        # Acessa a view protegida por permissão
        response = self.client.get(reverse('painel_diretoria'))  # Substitua 'minha_view' pela sua URL de nome

        # Verifica se o acesso foi bem-sucedido (status 200 OK)
        self.assertEqual(response.status_code, 200)

    def test_usuario_nao_logado(self):
        # Não há login do usuário

        # Tenta acessar a view protegida por permissão
        response = self.client.get(reverse('painel_diretoria'))  # Substitua 'minha_view' pela sua URL de nome

        # Verifica se é redirecionado para a página de login (status 302 Found)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/?next=/painel-diretoria/')  # Verifica se é redirecionado para a página de login com a próxima URL correta

    def test_usuario_logado_sem_permissao(self):
        # Loga o usuário sem permissão
        self.client.login(username='user_without_permission', password='password')

        # Tenta acessar a view protegida por permissão
        response = self.client.get(reverse('painel_diretoria'))

        self.assertEqual(response.status_code, 403)

# preparar_relatorio_mes_mes
# preparar_relatorio_produtos
# preparar_relatorio_clientes_mes_estagios
# peparar_relatorio_estagio
