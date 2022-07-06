from django.contrib.auth import get_user_model
from django.test import TestCase

from ..models import Group, Post

User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание')
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост для тестирования')

    def test_models_have_correct_object_names(self):
        """Проверяем, что у моделей корректно работает __str__."""
        models_str = {PostModelTest.post: PostModelTest.post.text[:15],
                      PostModelTest.group: PostModelTest.group.title}

        for model, expected_value in models_str.items():
            with self.subTest(model=model):
                self.assertEqual(model.__str__(), expected_value,
                                 f'Ошибка метода _str__ в'
                                 f' модели {type(model).__name__}')

    def test_verbose_name(self):
        """verbose_name в полях совпадает с ожидаемым."""
        verbose_names = {'text': 'Текст поста', 'pub_date': 'Дата публикации',
                         'author': 'Автор поста', 'group': 'Группа',
                         'image': 'Изображение'}

        for field, expected_value in verbose_names.items():
            with self.subTest(field=field):
                self.assertEqual(self.post._meta.get_field(field).verbose_name,
                                 expected_value,
                                 f'Ошибка verbose name поля {field}')

    def test_help_text(self):
        """help_text в полях совпадает с ожидаемым."""
        help_texts = {'text': 'Текст нового поста',
                      'group': 'Группа, к которой будет относиться пост'}

        for field, expected_value in help_texts.items():
            with self.subTest(field=field):
                self.assertEqual(self.post._meta.get_field(field).help_text,
                                 expected_value,
                                 f'Ошибка help text поля {field}')
