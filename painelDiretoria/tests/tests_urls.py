from django.contrib.auth.models import User, Permission
from django.test import TestCase
from django.urls import reverse


class SecurityTest(TestCase):
    def setUp(self):
        self.user_with_permission = User.objects.create_user(username='user_with_permission', password='password')
        self.permission = Permission.objects.get(codename='view_eventos')
        self.user_with_permission.user_permissions.add(self.permission)
        self.user_without_permission = User.objects.create_user(username='user_without_permission', password='password')

    def test_usuario_logado_com_permissao(self):
        self.client.login(username='user_with_permission', password='password')
        response = self.client.get(reverse('painel_diretoria'))
        self.assertEqual(response.status_code, 200)

    def test_usuario_nao_logado(self):
        response = self.client.get(reverse('painel_diretoria'))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/?next=/painel-diretoria/')

    def test_usuario_logado_sem_permissao(self):
        self.client.login(username='user_without_permission', password='password')
        response = self.client.get(reverse('painel_diretoria'))
        self.assertEqual(response.status_code, 403)

    def test_requisicao_post_negada_infos_clientes_mes_estagios(self):
        self.client.login(username='user_with_permission', password='password')
        response = self.client.post(reverse('infos_clientes_mes_estagios'), data={})
        self.assertEqual(response.status_code, 405)

    def test_requisicao_post_negada_infos_produtos_estagios(self):
        self.client.login(username='user_with_permission', password='password')
        response = self.client.post(reverse('infos_produtos_estagios'), data={})
        self.assertEqual(response.status_code, 405)
