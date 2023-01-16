from django.test import Client, TestCase
from django.urls import reverse
from posts.models import User
from http import HTTPStatus
from django import forms

UID = 64
TOKEN = 86


class UserPagesTests(TestCase):

    def setUp(self):
        '''Создаем клиентов для тестирования'''
        self.guest_client = Client()
        self.user = User.objects.create_user(username='SeriousName')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_public_pages_namespases_correct(self):
        '''Тестируем namespases страниц для неавторизованного пользователя'''
        public_adress = {
            'users:signup',
            'users:login',
            'users:logout',
        }
        for name in public_adress:
            response = self.guest_client.get(reverse(name))
            self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_authorized_pages_namespases_correct(self):
        '''Тестируем namespases страниц для авторизованного пользователя'''
        authorized_adress = {
            reverse('users:password_change'),
            reverse('users:password_change_done'),
            reverse('users:password_reset'),
            reverse('users:password_reset_done'),
            reverse(
                'users:password_reset_confirm',
                kwargs={'uidb64': UID, 'token': TOKEN}
            ),
            reverse('users:password_reset_complete'),
        }
        for name in authorized_adress:
            response = self.authorized_client.get(name)
            self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_create_user_correct_context(self):
        '''При регистрации пользователя передается правильный контекст'''
        response = self.guest_client.get(reverse('users:signup'))
        form_fields = {
            'first_name': forms.fields.CharField,
            'last_name': forms.fields.CharField,
            'username': forms.fields.CharField,
            'email': forms.fields.EmailField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                self.assertIsInstance(form_field, expected)
