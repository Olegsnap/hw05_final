from django.test import TestCase, Client
from django.urls import reverse
from http import HTTPStatus


class StaticURLTests(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_about_author(self):
        '''Проверка ссылки'''
        response = self.guest_client.get('/about/author/')
        self.assertEqual(response.status_code, 200)

    def test_about_tech(self):
        '''Проверка ссылки'''
        response = self.guest_client.get('/about/tech/')
        self.assertEqual(response.status_code, 200)

    def test_about_author_url_uses_correct_template(self):
        """Проверка шаблона"""
        response = self.guest_client.get('/about/author/')
        self.assertTemplateUsed(response, 'about/author.html')

    def test_about_tech_url_uses_correct_template(self):
        """Проверка шаблона"""
        response = self.guest_client.get('/about/tech/')
        self.assertTemplateUsed(response, 'about/tech.html')


class StaticPagesTests(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_about_author_page_namespase(self):
        '''Проверка namespases страницы автора'''
        response = self.guest_client.get(reverse('about:author'))
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_about_tech_page_namespase(self):
        '''Проверка namespases страницы технологий'''
        response = self.guest_client.get(reverse('about:tech'))
        self.assertEqual(response.status_code, HTTPStatus.OK)
