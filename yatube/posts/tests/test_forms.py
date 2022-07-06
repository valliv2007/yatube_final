import shutil
import tempfile

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from ..models import Comment, Group, Post

User = get_user_model()
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostFormTest(TestCase):
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
            text='Тестовый пост для тестирования',
            group=cls.group)

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.user = User.objects.create_user(username='test_user')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.author_client = Client()
        self.author_client.force_login(self.author)

    def test_create_post(self):
        """Валидная форма создает запись в Post."""
        posts_count = Post.objects.count()
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
        form_data = {'text': 'Создан пост',
                     'group': self.group.id,
                     'image': uploaded}

        response = self.authorized_client.post(reverse('posts:post_create'),
                                               data=form_data, follow=True)

        self.assertRedirects(response, reverse(
            'posts:profile',
            kwargs={'username': 'test_user'}),
            msg_prefix='Ошибка редиректа при создании поста')

        self.assertEqual(Post.objects.count(), posts_count + 1,
                         'Ошибка создания поста')
        self.assertTrue(Post.objects.filter(text='Создан пост',
                                            author=self.user,
                                            group=self.group,
                                            image='posts/small.gif').exists(),
                        'Ошибка содержания нового поста')

    def test_edit_post(self):
        """Валидная форма изменяет запись в Post."""
        posts_count = Post.objects.count()
        self.group = Group.objects.create(
            title='Новая тестовая группа',
            slug='new_slug',
            description='описание новой группы',)
        form_data = {'text': 'Редактирован пост', 'group': self.group.id}

        response = self.author_client.post(reverse(
            'posts:post_edit',
            kwargs={'post_id': self.post.pk}),
            data=form_data,
            follow=True)

        self.assertRedirects(
            response, reverse('posts:post_detail',
                              kwargs={'post_id': PostFormTest.post.pk}),
            msg_prefix='Ошибка редиректа при редактировании')

        self.assertEqual(Post.objects.count(), posts_count,
                         'Вместо редактирования, создан новый пост')
        self.assertTrue(Post.objects.filter(
            text='Редактирован пост',
            author=self.author,
            group=self.group).exists(),
            'Ошибка содержания редактированного поста')

    def test_create_comment(self):
        """После создания комментария, он появляется на странице поста"""
        comments_counter = Comment.objects.count()
        form_data = {'text': 'лучший пост'}

        response = self.authorized_client.post(
            reverse('posts:add_comment', kwargs={'post_id': self.post.pk}),
            data=form_data, follow=True)

        self.assertRedirects(
            response, reverse('posts:post_detail',
                              kwargs={'post_id': self.post.pk}),
            msg_prefix='Ошибка редиректа при создании комментария')
        self.assertEqual(Comment.objects.count(), comments_counter + 1,
                         'Ошибка создания комментария')

        response = self.authorized_client.get(
            reverse('posts:post_detail', kwargs={'post_id': self.post.pk}))
        comment_obj = response.context['comments'].get()

        self.assertEqual(comment_obj, self.post.comments.get(),
                         'Ошибка вывода комментария к посту в шаблон')
