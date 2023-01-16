from http import HTTPStatus
from django.test import TestCase, Client


class Custom404UrlsTests(TestCase):
    '''Создаем клиента для тестирования'''
    def setUp(self):
        self.guest_client = Client()

    def test_unexisting_page_used_custom_template(self):
        response = self.guest_client.get('unexisting_page')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertTemplateUsed(response, 'core/404.html')
