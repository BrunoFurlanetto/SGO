from datetime import datetime, timedelta
from random import randint
from django.test import TestCase
from peraltas.models import Eventos
from peraltas.tests.factories import ClienteColegioFactory, EventosFactory


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

    def test_tipo_retorno_campos_cadastro_eventos(self):
        campos = Eventos.preparar_relatorio_clientes_mes_estagios(
            'confirmado',
            'Julho',
            2024,
            ['cliente', 'qtd_previa', 'qtd_confirmado']
        )
        self.assertEqual(type(campos), dict)
        self.assertTrue('relatorio' in campos)
        self.assertTrue('estagio' in campos)
        self.assertTrue('campos' in campos)

# ----------------------------------------------------------------------------------------------------------------------
# ---------------------------- Testes para o preparar_relatorio_clientes_mes_estagios ----------------------------------
# ----------------------------------------------------------------------------------------------------------------------
    def test_preparar_relatorio_clientes_mes_estagios_pre_reserva(self):
        mes = 'Julho'
        ano = 2024

        # Chamando o método que queremos testar
        relatorio = Eventos.preparar_relatorio_clientes_mes_estagios(
            'pre_reserva',
            mes,
            ano,
            ['cliente', 'qtd_previa', 'qtd_confirmado']
        )

        # Verificando se o relatório foi gerado corretamente
        self.assertEqual(len(relatorio['relatorio']), 1)  # Verifica se há apenas um evento no relatório
        self.assertEqual(relatorio['estagio'], 'Pré reserva')  # Verifica se o estágio está correto

        # Verificando detalhes do evento no relatório
        evento_relatorio = relatorio['relatorio'][0]
        self.assertEqual(evento_relatorio['cliente'], self.cliente1.__str__())  # Verifica o cliente
        self.assertEqual(evento_relatorio['qtd_previa'], '10')  # Verifica a quantidade previamente reservada
        self.assertEqual(evento_relatorio['qtd_confirmado'], '8')  # Verifica a quantidade confirmada

    def test_preparar_relatorio_clientes_mes_estagios_confirmado(self):
        mes = 'Julho'
        ano = 2024
        # Testando para outro estágio
        relatorio_confirmado = Eventos.preparar_relatorio_clientes_mes_estagios(
            'confirmado',
            mes,
            ano,
            ['cliente', 'qtd_previa', 'qtd_confirmado']
        )
        self.assertEqual(len(relatorio_confirmado['relatorio']), 1)  # Verifica se há apenas um evento no relatório
        self.assertEqual(relatorio_confirmado['estagio'], 'Evento confirmado')  # Verifica se o estágio está correto
        evento_relatorio_confirmado = relatorio_confirmado['relatorio'][0]
        self.assertEqual(evento_relatorio_confirmado['cliente'], self.cliente2.__str__())  # Verifica o cliente
        self.assertEqual(evento_relatorio_confirmado['qtd_previa'], '15')  # Verifica a quantidade previamente reservada
        self.assertEqual(evento_relatorio_confirmado['qtd_confirmado'], '12')  # Verifica a quantidade confirmada

    def test_preparar_relatorio_clientes_mes_sem_resultado_para_o_ano(self):
        mes = 'Julho'
        ano = 2025

        relatorio = Eventos.preparar_relatorio_clientes_mes_estagios(
            'confirmado',
            mes,
            ano,
            ['cliente', 'qtd_previa', 'qtd_confirmado']
        )
        self.assertEqual(len(relatorio['relatorio']), 0)

    def test_preparar_relatorio_clientes_mes_sem_resultado_para_o_mes(self):
        mes = 'Agosto'
        ano = 2024

        relatorio = Eventos.preparar_relatorio_clientes_mes_estagios(
            'confirmado',
            mes,
            ano,
            ['cliente', 'qtd_previa', 'qtd_confirmado']
        )
        self.assertEqual(len(relatorio['relatorio']), 0)

    def tester_preparar_relatorio_clientes_mes_sem_resultado_para_o_estagio(self):
        mes = 'Julho'
        ano = 2024

        relatorio = Eventos.preparar_relatorio_clientes_mes_estagios(
            'ficha_evento',
            mes,
            ano,
            ['cliente', 'qtd_previa', 'qtd_confirmado']
        )
        self.assertEqual(len(relatorio['relatorio']), 0)

# ----------------------------------------------------------------------------------------------------------------------
# --------------------------------------- Testes para o relatorio_mes_mes ----------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------
    def test_preparar_relatorio_mes_mes_com_eventos(self):
        data_atual = datetime.today().date()
        mes_atual = Eventos.nome_mes(data_atual.month)
        relatorio = Eventos.preparar_relatorio_mes_mes()
        self.assertEqual(len(relatorio), 1)

        primeiro_relatorio = relatorio[0]
        self.assertEqual(primeiro_relatorio['mes_ano'], f'{mes_atual}/{data_atual.year}')
        self.assertEqual(primeiro_relatorio['n_pre_reserva'], 1)
        self.assertEqual(primeiro_relatorio['n_previa_pre_reserva'], 10)
        self.assertEqual(primeiro_relatorio['n_confirmados_pre_reserva'], 8)
        self.assertEqual(primeiro_relatorio['n_confirmado'], 1)
        self.assertEqual(primeiro_relatorio['n_previa_confirmado'], 15)
        self.assertEqual(primeiro_relatorio['n_confirmados_confirmado'], 12)


class EventosPerformanceTest(TestCase):
    def setUp(self):
        for _ in range(100):  # Criar 100 eventos para simular carga
            random_day = randint(1, 31)
            random_date = datetime(2024, 7, random_day)
            evento = EventosFactory(data_check_in=random_date)

    def test_performance_preparar_relatorio_clientes_mes_sem_resultado(self):
        start_time = datetime.now()
        relatorio = Eventos.preparar_relatorio_clientes_mes_estagios(
            'confirmado',
            'Janeiro',
            2024,
            ['cliente', 'qtd_previa', 'qtd_confirmado']
        )
        end_time = datetime.now()
        execution_time = (end_time - start_time).total_seconds()

        self.assertLess(execution_time, 0.1)
        self.assertEqual(len(relatorio['relatorio']), 0)
        self.assertTrue('relatorio' in relatorio)
        self.assertTrue('estagio' in relatorio)

    def test_performance_preparar_relatorio_clientes_mes_com_resultado(self):
        start_time = datetime.now()
        relatorio = Eventos.preparar_relatorio_clientes_mes_estagios(
            'confirmado',
            'Julho',
            2024,
            ['cliente', 'qtd_previa', 'qtd_confirmado']
        )
        end_time = datetime.now()
        execution_time = (end_time - start_time).total_seconds()

        self.assertLess(execution_time, 0.1)
        self.assertGreaterEqual(len(relatorio['relatorio']), 1)
        self.assertTrue('relatorio' in relatorio)
        self.assertTrue('estagio' in relatorio)

# preparar_relatorio_produtos
# preparar_relatorio_clientes_mes_estagios
# peparar_relatorio_estagio
