from django.test import TestCase, Client
from posts.models import User
from http import HTTPStatus


class UsersUrlsTests(TestCase):
    '''Создаем клиентов для тестирования urls'''
    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.create_user(username='HasNoName')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_public_urls(self):
        '''Тестируем общедоступные страницы'''
        public_urls = {
            '/auth/signup/',
            '/auth/logout/',
            '/auth/login/',
        }
        for url in public_urls:
            responce = self.guest_client.get(url)
            self.assertEqual(responce.status_code, HTTPStatus.OK)

    def test_authorized_urls(self):
        '''Тестируем страницы для авторизованных'''
        authorized_urls = {
            '/auth/password_change/',
            '/auth/password_change/done/',
            '/auth/password_reset',
            '/auth/password_reset/done/',
            '/auth/reset/<uidb64>/<token>/',
            '/auth/reset/done/',
        }
        for url in authorized_urls:
            responce = self.authorized_client.get(url)
            self.assertEqual(responce.status_code, HTTPStatus.OK)

    def test_correct_template(self):
        '''Тестируем корректность используемых шаблонов'''
        templates_url_names = {
            '/auth/password_change/': 'users/password_change_form.html',
            '/auth/password_change/done/': 'users/password_change_done.html',
            '/auth/signup/': 'users/signup.html',
            '/auth/logout/': 'users/logged_out.html',
            '/auth/login/': 'users/login.html',
            '/auth/password_reset': 'users/password_reset_form.html',
            '/auth/password_reset/done/': 'users/password_reset_done.html',
            '/auth/reset/<uidb64>/<token>/':
            'users/password_reset_confirm.html',
            '/auth/reset/done/': 'users/password_reset_complete.html',
        }
        for url, template, in templates_url_names.items():
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertTemplateUsed(response, template)
