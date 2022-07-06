from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Group, Post

User = get_user_model()


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_slug',
            description='Тестовое описание')
        cls.post = Post.objects.create(
            author=cls.author,
            text='Тестовый пост для тестирования')
        cls.index = '/'
        cls.group = '/group/test_slug/'
        cls.profile = '/profile/test_user/'
        cls.post_id = f'/posts/{cls.post.pk}/'
        cls.create = '/create/'
        cls.edit = f'/posts/{cls.post.pk}/edit/'
        cls.public_urls = (cls.index, cls.group, cls.profile, cls.post_id)

    def setUp(self):
        cache.clear()
        self.guest_client = Client()
        self.user = User.objects.create_user(username='test_user')
        self.authorized_client = Client()
        self.author_client = Client()
        self.authorized_client.force_login(self.user)
        self.author_client.force_login(self.author)

    def test_pages_for_all_users(self):
        """Проверка страниц, доступных любому пользователю."""
        for page in self.public_urls:
            with self.subTest(page=page):
                response = self.guest_client.get(page)
                self.assertEqual(response.status_code, HTTPStatus.OK,
                                 f'Ошибка доступа к странице {page}')

    def test_create_for_authorized_users(self):
        """Тест страницы /create/ для авторизованного пользователя."""
        response = self.authorized_client.get(self.create)

        self.assertEqual(response.status_code, HTTPStatus.OK,
                         'Ошибка доступа авторизованного пользователя'
                         ' к странице create')

    def test_create_and_edit_for_nonauthorized_users(self):
        """Тест страниц создания и редактирования поста
        для неавторизованного пользователя."""
        resp = {self.create: self.guest_client.get(self.create, follow=True),
                self.edit: self.guest_client.get(self.edit, follow=True)}

        for url, response in resp.items():
            with self.subTest(url=url):
                self.assertRedirects(response, (f'/auth/login/?next={url}'),
                                     msg_prefix=('Ошибка переадресации '
                                                 'незарегистрованного'
                                                 'пользователя при попытке'
                                                 f'доступа к странице {url}'))

    def test_edit_for_author(self):
        """Тест страницы редактирования поста для автора поста."""
        response = self.author_client.get(self.edit)

        self.assertEqual(response.status_code, HTTPStatus.OK,
                         'Ошибка доступа авторa поста'
                         ' к странице редактирования поста')

    def test_edit_for_nonauthor_and_authorized_user(self):
        """Тест edit для авторизованного пользователя, но не автора поста."""
        response = self.authorized_client.get(self.edit, follow=True)

        self.assertRedirects(response, ('/profile/auth/'),
                             msg_prefix=('Ошибка переадресации '
                                         'зарегистрованного пользователя, но '
                                         'не автора поста к странице'
                                         ' редактирования'))

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_url_names = {
            self.index: 'posts/index.html',
            self.group: 'posts/group_list.html',
            self.profile: 'posts/profile.html',
            self.post_id: 'posts/post_detail.html',
            self.create: 'posts/create_post.html',
            self.edit: 'posts/create_post.html'}

        for url, template in templates_url_names.items():
            with self.subTest(url=url):
                response = self.author_client.get(url)
                self.assertTemplateUsed(response, template,
                                        f'Ошибка шаблона при вызове {url}')

    def test_comment_for_nonauthorized_users(self):
        """Комментирование не доступно неавторизованному пользлвателю."""
        response = self.guest_client.get(reverse(
            'posts:add_comment', kwargs={'post_id': self.post.pk}))

        self.assertEqual(
            response.status_code, 302,
            'неавторизованный пользователь имеет доступ к комментированию')
        self.assertRedirects(
            response,
            (f'/auth/login/?next=/posts/{self.post.pk}/comment/'),
            msg_prefix=('Ошибка редиректа незарегистрованного пользователя'))
