from datetime import datetime

from django.contrib.auth.models import User, Permission
from django.test import TestCase
from django.urls import reverse

from peraltas.tests.factories import EventosFactory


class SecurityTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='user', password='password')
        self.permission = Permission.objects.get(codename='view_eventos')
        self.user.user_permissions.add(self.permission)
        self.evento = EventosFactory.create(data_check_in=datetime(2024, 7, 8))

    def test_index_painel_diretoria(self):
        self.client.login(username='user', password='password')
        response = self.client.get(reverse('painel_diretoria'))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'painelDiretoria/index.html')

    def test_get_usuario_logado_ajax_infos_clientes_mes_estagios(self):
        self.client.login(username='user', password='password')

        response = self.client.get(
            reverse('infos_clientes_mes_estagios'),
            HTTP_X_REQUESTED_WITH='XMLHttpRequest',
            data={
                'mes_ano': 'Julho/2024',
                'estagio': 'confirmado',
                'campos': ['cliente', 'qtd_previa', 'qtd_confirmado']
            }
        )

        self.assertEqual(response.status_code, 200)
        self.assertTrue('relatorio' in response.json())
        self.assertTrue('estagio' in response.json())

    def test_get_usuario_nao_logado_ajax_infos_clientes_mes_estagios(self):
        response = self.client.get(
            reverse('infos_clientes_mes_estagios'),
            HTTP_X_REQUESTED_WITH='XMLHttpRequest',
        )

        self.assertEqual(response.status_code, 302)

    def test_post_usuario_logado_ajax_infos_clientes_mes_estagios(self):
        self.client.login(username='user', password='password')

        response = self.client.post(
            reverse('infos_clientes_mes_estagios'),
            HTTP_X_REQUESTED_WITH='XMLHttpRequest',
        )

        self.assertEqual(response.status_code, 405)

    def test_get_usuario_logado_ajax_infos_produtos_estagios(self):
        self.client.login(username='user', password='password')

        response = self.client.get(
            reverse('infos_produtos_estagios'),
            HTTP_X_REQUESTED_WITH='XMLHttpRequest',
            data={
                'mes_ano': 'Julho/2024',
            }
        )

        self.assertEqual(response.status_code, 200)
        self.assertTrue('dados_estagio' in response.json())
        self.assertTrue('dados_produto' in response.json())

    def test_post_usuario_logado_ajax_infos_produtos_estagios(self):
        self.client.login(username='user', password='password')

        response = self.client.post(
            reverse('infos_produtos_estagios'),
            HTTP_X_REQUESTED_WITH='XMLHttpRequest',
        )

        self.assertEqual(response.status_code, 405)

    def test_get_usuario_nao_logado_ajax_infos_produtos_estagios(self):
        response = self.client.post(
            reverse('infos_produtos_estagios'),
            HTTP_X_REQUESTED_WITH='XMLHttpRequest',
        )

        self.assertEqual(response.status_code, 302)
