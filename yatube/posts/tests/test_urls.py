from django.test import TestCase, Client
from posts.models import Post, Group, User
from http import HTTPStatus


class PostUrlsTests(TestCase):
    '''Создаем тестовые записи в бд для тестирования urls'''
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='NoName')
        cls.group = Group.objects.create(
            title='Тестовый заголовок',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            text='Текст',
            pub_date='01.01.2012',
            author=cls.author,
            group=cls.group,
        )
        cls.guest_client = Client()
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.author)
        cls.post_detail = f'/posts/{cls.post.id}/'
        cls.post_edit = f'/posts/{cls.post.id}/edit/'

    def test_public_urls(self):
        '''Тестируем общедоступные страницы'''
        public_urls = {
            '/',
            '/group/test-slug/',
            '/profile/NoName/',
            f'{self.post_detail}',
        }
        for url in public_urls:
            responce = self.guest_client.get(url)
            self.assertEqual(responce.status_code, HTTPStatus.OK)

    def test_authorized_urls(self):
        '''Тестируем страницы для авторизованных'''
        authorized_urls = {
            f'{self.post_edit}',
            '/create/'
        }
        for url in authorized_urls:
            responce = self.authorized_client.get(url)
            self.assertEqual(responce.status_code, HTTPStatus.OK)

    def test_redirect_create(self):
        '''Проверяем редирект со страницы создания поста
        для неавторизованного пользователя'''
        responce = self.guest_client.get('/create/')
        self.assertRedirects(responce, '/auth/login/?next=/create/')

    def test_redirect_edit(self):
        '''Проверяем редирект со страницы редактирования поста
        для неавторизованного пользователя'''
        responce = self.guest_client.get(self.post_edit)
        self.assertRedirects(responce, '/auth/login/?next=/posts/1/edit/')

    def test_post_unexisting_page(self):
        '''Тестируем недоступность несуществующей страницы'''
        responce = self.guest_client.get('unexisting_page')
        self.assertEqual(responce.status_code, HTTPStatus.NOT_FOUND)

    def test_correct_template(self):
        '''Тестируем корректность используемых шаблонов'''
        templates_url_names = {
            '/': 'posts/index.html',
            '/group/test-slug/': 'posts/group_list.html',
            '/profile/NoName/': 'posts/profile.html',
            '/posts/1/': 'posts/post_detail.html',
            '/posts/1/edit/': 'posts/create_post.html',
            '/create/': 'posts/create_post.html',
        }
        for url, template, in templates_url_names.items():
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertTemplateUsed(response, template)
