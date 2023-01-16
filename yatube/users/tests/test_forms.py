from django.test import TestCase, Client
from django.urls import reverse
from ..forms import User
from http import HTTPStatus


class PostModelTest(TestCase):
    '''Создаем тестового пользователя'''
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='TestName')
        cls.guest_client = Client()
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)

    def test_create_user_save_if_valid(self):
        '''При отправке валидных данных создается новый пользователь'''
        users_count = User.objects.count()
        form_data = {
            'first_name': 'Dmitry',
            'last_name': 'Puchkov',
            'username': 'Goblin',
            'email': 'tupichok@mail.ru',
            'password1': 'Tipsi1517',
            'password2': 'Tipsi1517',
        }
        response = self.guest_client.post(
            reverse('users:signup'),
            data=form_data,
            follow=True
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(User.objects.count(), users_count + 1)
        self.assertTrue(User.objects.filter(last_name='Puchkov').exists())
