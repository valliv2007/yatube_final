import shutil
import tempfile

from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from ..models import Follow, Group, Post
from ..views import AMOUNT_POSTS

User = get_user_model()
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_slug',
            description='Тестовое описание')
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B')
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif')
        cls.post = Post.objects.create(
            author=cls.author,
            text=('Тестовый пост для тестирования'),
            group=cls.group,
            image=uploaded)
        cls.index = 'posts:index'
        cls.group_post = 'posts:group_list'
        cls.profile = 'posts:profile'
        cls.post_id = 'posts:post_detail'
        cls.create = 'posts:post_create'
        cls.edit = 'posts:post_edit'
        cls.subscribe = 'posts:profile_follow'
        cls.unsubscribe = 'posts:profile_unfollow'
        cls.follow = 'posts:follow_index'

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        cache.clear()
        self.guest_client = Client()
        self.user = User.objects.create_user(username='test_user')
        self.authorized_client = Client()
        self.author_client = Client()
        self.authorized_client.force_login(self.user)
        self.author_client.force_login(self.author)

    def test_correct_templates(self):
        """URL-адрес использует соответствующий шаблон."""
        templates = {reverse(self.index): 'posts/index.html',
                     reverse(self.create): 'posts/create_post.html',
                     reverse(self.group_post, kwargs={'slug': 'test_slug'}):
                     'posts/group_list.html',
                     reverse(self.profile, kwargs={'username': 'auth'}):
                     'posts/profile.html',
                     reverse(self.post_id,
                             kwargs={'post_id': PostPagesTests.post.pk}):
                     'posts/post_detail.html',
                     reverse(self.edit,
                             kwargs={'post_id': PostPagesTests.post.pk}):
                     'posts/create_post.html'}

        for reverse_name, template in templates.items():
            with self.subTest(template=template):
                response = self.author_client.get(reverse_name)
                self.assertTemplateUsed(response, template,
                                        f'Ошибка при вызове {reverse_name}')

    def test_index_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        response = self.guest_client.get(reverse(self.index))
        first_obj = response.context['page_obj'].object_list[0]
        self.assertEqual(first_obj, self.post,
                         'Ошибка вывода контекста поста в шаблон')
        self.assertEqual(first_obj.image, self.post.image,
                         'Ошибка вывода изображения в шаблон')

    def test_group_posts_context(self):
        """Шаблон group_list сформирован с правильным контекстом."""
        response = self.guest_client.get(reverse(
            self.group_post, kwargs={'slug': 'test_slug'}))
        first_obj = response.context['page_obj'].object_list[0]

        self.assertEqual(first_obj, self.post,
                         'Ошибка вывода контекста поста в шаблон')
        self.assertEqual(first_obj.image, self.post.image,
                         'Ошибка вывода изображения в шаблон')

    def test_profile_context(self):
        """Шаблон profile сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse(
            self.profile, kwargs={'username': 'auth'}))
        first_obj = response.context['page_obj'].object_list[0]

        self.assertEqual(first_obj, self.post,
                         'Ошибка вывода контекста поста в шаблон')
        self.assertEqual(first_obj.image, self.post.image,
                         'Ошибка вывода изображения в шаблон')

    def test_post_detail_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        response = self.guest_client.get(
            reverse(self.post_id, kwargs={'post_id': PostPagesTests.post.pk}))
        first_obj = response.context['post']

        self.assertEqual(first_obj, self.post,
                         'Ошибка вывода контекста поста в шаблон')
        self.assertEqual(first_obj.image, self.post.image,
                         'Ошибка вывода изображения в шаблон')

    def test_create_context(self):
        """Шаблон post_create сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse(self.create))
        form_fields = {'text': forms.fields.CharField,
                       'group': forms.fields.ChoiceField}

        for field, field_type in form_fields.items():
            with self.subTest(field=field):
                form_field = response.context['form'].fields[field]

                self.assertIsInstance(form_field, field_type,
                                      f'Ошибка вывода поля {field} в шаблон')

    def test_post_edit_context(self):
        """Шаблон post_edit сформирован с правильным контекстом."""
        response = self.author_client.get(reverse(
            self.edit, kwargs={'post_id': self.post.pk}))
        form_fields = {'text': forms.fields.CharField,
                       'group': forms.fields.ChoiceField}

        for field, field_type in form_fields.items():
            with self.subTest(field=field):
                form_field = response.context['form'].fields[field]

                self.assertIsInstance(form_field, field_type,
                                      f'Ошибка вывода поля {field} в шаблон')

    def test_new_post_in_pages(self):
        """Пост не попадает в неправильную группу."""
        self.group = Group.objects.create(
            title='Неправильная группа',
            slug='slug_wrong',
            description='Не та группа')

        response = self.authorized_client.get(reverse(
            self.group_post, kwargs={'slug': 'slug_wrong'}))

        self.assertEqual(response.context['page_obj'].paginator.count, 0,
                         'Пост попадает в неверную группу')

        Post.objects.create(
            author=PostPagesTests.author,
            text='Тестовый пост для тестирования неверной группы',
            group=PostPagesTests.group)
        cache.clear()

        response = self.authorized_client.get(reverse(
            self.group_post, kwargs={'slug': 'slug_wrong'}))

        self.assertEqual(response.context['page_obj'].paginator.count, 0,
                         'Пост попадает в неверную группу')

        responses = (self.guest_client.get(reverse(self.index)),
                     self.guest_client.get(reverse(
                         self.group_post, kwargs={'slug': 'test_slug'})),
                     self.authorized_client.get(reverse(
                         self.profile, kwargs={'username': 'auth'})))

        for response in responses:
            with self.subTest(response=response):
                self.assertEqual(response.context['page_obj'].paginator.count,
                                 2, 'Ошибка вывода нового поста')

    def test_paginators(self):
        """Выводится правильное кол-во постов."""
        for i in range(13):
            self.post = Post.objects.create(
                author=self.author,
                text=(f'Тестовый пост {i} для тестирования'),
                group=self.group)

        responses = (self.guest_client.get(reverse(self.index)),
                     self.guest_client.get(reverse(
                         self.group_post,
                         kwargs={'slug': 'test_slug'})),
                     self.guest_client.get(reverse(
                         self.profile,
                         kwargs={'username': 'auth'})))

        for response in responses:
            with self.subTest(response=response):
                self.assertEqual(len(response.context['page_obj'].object_list),
                                 AMOUNT_POSTS,
                                 'Ошибка вывода кол-во постов на странице')

        responses = (self.guest_client.get(reverse(self.index) + '?page=2'),
                     self.guest_client.get(reverse(
                         self.group_post,
                         kwargs={'slug': 'test_slug'}) + '?page=2'),
                     self.guest_client.get(reverse(
                         self.profile,
                         kwargs={'username': 'auth'}) + '?page=2'))

        for response in responses:
            with self.subTest(response=response):
                self.assertEqual(len(response.context['page_obj'].object_list),
                                 4,
                                 'Ошибка вывода кол-во постов на странице')

    def test_cache(self):
        """Проверка кэширования"""
        cache.clear()
        cache_post = Post.objects.create(
            author=PostPagesTests.author,
            text=' Пост для тестирования кэша',
            group=PostPagesTests.group)
        response_1 = self.guest_client.get(reverse(self.index))
        content = response_1.content

        self.assertEqual(content, response_1.content)

        cache_post.delete()
        response_2 = self.guest_client.get(reverse(self.index))

        self.assertEqual(content, response_2.content,
                         'Ошибка кэширования постов')

        cache.clear()
        response_3 = self.guest_client.get(reverse(self.index))

        self.assertNotEqual(content, response_3.content,
                            'Ошибка очистки кэша')

    def test_subscribe(self):
        """можно подписываться на пользователей и удалять подписки."""
        self.authorized_client.get(reverse(
            self.subscribe, kwargs={'username': 'auth'}))

        self.assertTrue(Follow.objects.filter(author=self.author,
                                              user=self.user).exists(),
                        'Ошибка создания новой подписки')

        self.authorized_client.get(reverse(
            self.unsubscribe, kwargs={'username': 'auth'}))

        self.assertFalse(Follow.objects.filter(author=self.author,
                                               user=self.user).exists(),
                         'Ошибка удаления подписки')

    def test_follow(self):
        """новый пост есть в ленте подписчиков и отсутвует в ленте других."""
        Follow.objects.create(
            user=self.user,
            author=self.author)
        Follow.objects.create(
            user=self.author,
            author=self.user)
        test_post = Post.objects.create(
            author=self.user,
            text=('Пост для тестирования подписки'),
            group=self.group)

        response = self.author_client.get(reverse(self.follow))
        first_obj = response.context['page_obj'].object_list[0]

        self.assertEqual(first_obj, test_post,
                         'Ошибка вывода поста в ленте подписчика')

        response = self.authorized_client.get(reverse(self.follow))
        first_obj = response.context['page_obj'].object_list[0]

        self.assertNotEqual(first_obj, test_post,
                            'Ошибка вывода поста в ленте подписчика')
