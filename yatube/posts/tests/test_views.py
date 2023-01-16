import shutil
import tempfile

from django import forms
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from django.conf import settings
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from http import HTTPStatus
from posts.models import Post, Group, Follow, User

POST_FIRST_PAGE = 10
POST_SECOND_PAGE = 3
NUMBER_OF_POSTS = POST_FIRST_PAGE + POST_SECOND_PAGE
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostsPagesTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='FunnyName')
        cls.author = User.objects.create_user(username='Author')
        small_gif = (
             b'\x47\x49\x46\x38\x39\x61\x02\x00'
             b'\x01\x00\x80\x00\x00\x00\x00\x00'
             b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
             b'\x00\x00\x00\x2C\x00\x00\x00\x00'
             b'\x02\x00\x01\x00\x00\x02\x02\x0C'
             b'\x0A\x00\x3B'
        )
        cls.group = Group.objects.create(
            title='Тестовая группа0',
            slug='test-slug0',
            description='Тестовое описание',
        )
        for i in reversed(range(NUMBER_OF_POSTS)):
            uploaded = SimpleUploadedFile(
                name=f'small{i}.gif',
                content=small_gif,
                content_type='image/gif'
            )
            cls.post = Post.objects.create(
                text=f'Тестовый пост{i}',
                author=cls.author,
                group=Group.objects.get(slug='test-slug0'),
                image=uploaded
            )
        cls.index_url = ('posts:index', 'posts/index.html')
        cls.group_url = (
            'posts:group_list',
            'posts/group_list.html',
            cls.group.slug
        )
        cls.profile_url = ('posts:profile', 'posts/profile.html', cls.author)
        cls.post_detail_url = (
            'posts:post_detail',
            'posts/post_detail.html',
            cls.post.id,
        )
        cls.post_edit_url = (
            'posts:post_edit',
            'posts/create_post.html',
            cls.post.id,
        )
        cls.post_create_url = ('posts:post_create', 'posts/create_post.html')

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.author_client = Client()
        self.author_client.force_login(self.author)
        cache.clear()

    def test_page_show_correct_context(self):
        '''Следующие шаблоны сформированы с правильным контекстом'''
        pages_names = {
            reverse(self.index_url[0]),
            reverse(self.group_url[0],
                    kwargs={'slug': self.group_url[2]}
                    ),
            reverse(self.profile_url[0],
                    kwargs={'username': self.profile_url[2]}
                    ),
        }

        for template in pages_names:
            with self.subTest(template=template):
                response = self.guest_client.get(template)
                first_object = response.context['page_obj'][0]
                author_0 = first_object.author.username
                post_text_0 = first_object.text
                group_0 = first_object.group.title
                image_0 = first_object.image.name
                self.assertEqual(author_0, self.author.username)
                self.assertEqual(post_text_0, 'Тестовый пост0')
                self.assertEqual(group_0, 'Тестовая группа0')
                self.assertEqual(image_0, 'posts/small0.gif')

    def test_post_detail_show_correct_context(self):
        '''Шаблон post_detail сформирован с правильным контекстом'''
        response = self.authorized_client.get(
            reverse(self.post_detail_url[0],
                    args=[self.post_detail_url[2]])
        )
        post = response.context['post']
        self.assertEqual(post.pk, self.post_edit_url[2])
        self.assertEqual(post.image, 'posts/small0.gif')

    def test_create_post_edit_show_correct_context(self):
        """Шаблон create_post(edit) сформирован с правильным контекстом."""
        response = self.author_client.get(
            reverse(
                self.post_edit_url[0],
                args=[self.post_edit_url[2]]
            )
        )
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.models.ModelChoiceField,
            'image': forms.fields.ImageField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                self.assertIsInstance(form_field, expected)

    def test_create_post_show_correct_context(self):
        """Шаблон create_post сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse(self.post_create_url[0]))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.models.ModelChoiceField,
            'image': forms.fields.ImageField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                self.assertIsInstance(form_field, expected)

    def test_urls_page_contains_10_records(self):
        '''Паджинатор выводит 10 постов на следующие страницы'''
        pages_names = [
            reverse(self.index_url[0]),
            reverse(self.group_url[0],
                    kwargs={'slug': self.group_url[2]}
                    ),
            reverse(self.profile_url[0],
                    kwargs={'username': self.profile_url[2]}
                    ),
        ]
        for template in pages_names:
            with self.subTest(template=template):
                response = self.guest_client.get(template)
                self.assertEqual(
                    len(response.context['page_obj']),
                    POST_FIRST_PAGE
                )

    def test_urls_page_contins_3_recors(self):
        '''Паджинатор выводит 3 поста на следующие страницы'''
        pages_names = [
            reverse(self.index_url[0]),
            reverse(self.group_url[0],
                    kwargs={'slug': self.group_url[2]}
                    ),
            reverse(self.profile_url[0],
                    kwargs={'username': self.profile_url[2]}
                    ),
        ]
        for template in pages_names:
            with self.subTest(template=template):
                response = self.guest_client.get(template + '?page=2')
                self.assertEqual(
                    len(response.context['page_obj']),
                    POST_SECOND_PAGE
                )

    def test_post_in_index_group_profile_after_create(self):
        """созданный пост появился на следующих страницах"""
        reverse_page_names_post = {
            reverse(
                self.index_url[0]):
                    self.group_url[2],
            reverse(
                self.group_url[0],
                kwargs={'slug': self.group_url[2]}):
                    self.group_url[2],
            reverse(
                self.profile_url[0],
                kwargs={'username': self.profile_url[2]}):
                    self.group_url[2]
        }
        for value, expected in reverse_page_names_post.items():
            response = self.authorized_client.get(value)
            for object in response.context['page_obj']:
                post_group = object.group.slug
                with self.subTest(value=value):
                    self.assertEqual(post_group, expected)

    def test_post_not_in_another_group(self):
        """пост не попал в группу, для которой не был предназначен."""
        Group.objects.create(
            title='Тестовая группа100',
            slug='test-slug100',
            description='Тестовое описание',
        )
        Post.objects.create(
            text='Тестовый пост100',
            author=self.user,
            group=Group.objects.get(slug='test-slug100')
        )
        response = self.authorized_client.get(
            reverse(self.group_url[0], kwargs={'slug': 'test-slug100'})
        )
        for object in response.context['page_obj']:
            post_slug = object.group.slug
            self.assertNotEqual(post_slug, self.group.slug)

    def test_cache_index_url(self):
        '''Проверка хранения кэша для index'''
        response = self.authorized_client.get(
            reverse(self.index_url[0])
        )
        posts = response.content
        Post.objects.create(
            text='Новый текст поста',
            author=self.user,
            group=Group.objects.get(slug='test-slug0')
        )
        response_old = self.authorized_client.get(
            reverse(self.index_url[0])
        )
        posts_old = response_old.content
        self.assertEqual(posts, posts_old)

    def test_follow_for_author(self):
        '''Проверка подписки на автора'''
        count_follow = Follow.objects.count()
        Follow.objects.create(
            user=self.user,
            author=self.author
        )
        self.authorized_client.post(
            reverse(
                'posts:profile_follow',
                kwargs={'username': self.author}
            )
        )
        self.assertEqual(Follow.objects.count(), count_follow + 1)

    def test_unfollow_author(self):
        '''Проверка отписки от автора'''
        Follow.objects.create(
            user=self.user,
            author=self.author
        )
        count_follow = Follow.objects.count()
        self.authorized_client.post(
            reverse(
                'posts:profile_unfollow',
                kwargs={'username': self.author}
            )
        )
        self.assertEqual(Follow.objects.count(), count_follow - 1)

    def test_new_post_for_follower_in_feed(self):
        '''Новый пост в ленте подписок'''
        Follow.objects.create(
            user=self.user,
            author=self.author
        )
        post = Post.objects.create(
            text='Новый текст дня',
            author=self.author,
        )
        response = self.authorized_client.get(
            reverse('posts:follow_index')
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertIn(post, response.context['page_obj'])

    def test_new_post_for_unfollower_not_in_follow_list(self):
        '''Нового поста нет в ленте для неподписанных'''
        post = Post.objects.create(
            text='Новый интересный текст дня',
            author=self.author,
        )
        response = self.authorized_client.get(
            reverse('posts:follow_index')
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertNotIn(post, response.context['page_obj'])
