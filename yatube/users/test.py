from http import HTTPStatus

from django import forms
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

User = get_user_model()


class UsersTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.login = 'users:login'
        cls.login_tmpl = 'users/login.html'
        cls.logout = 'users:logout'
        cls.logout_tmpl = 'users/logged_out.html'
        cls.sign_up = 'users:signup'
        cls.sign_up_tmpl = 'users/signup.html'
        cls.password_change = 'users:password_change'
        cls.password_change_tmpl = 'users/password_change_form.html'
        cls.password_change_done = 'users:password_change_done'
        cls.password_change_done_tmpl = 'users/password_change_done.html'
        cls.password_reset = 'users:password_reset'
        cls.password_reset_tmpl = 'users/password_reset_form.html'
        cls.password_reset_done = 'users:password_reset_done'
        cls.password_reset_done_tmpl = 'users/password_reset_done.html'
        cls.password_reset_confirm = 'users:password_reset_confirm'
        cls.password_reset_confirm_tmpl = 'users/password_reset_confirm.html'
        cls.password_reset_complete = 'users:password_reset_complete'
        cls.password_reset_complete_tpl = 'users/password_reset_complete.html'

    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.create_user(username='test_user')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_pages_for_all_users(self):
        """Проверка  доступа к  страницам входа и регистрации."""
        pages = ('/auth/login/', '/auth/signup/')
        for page in pages:
            with self.subTest(page=page):
                response = self.guest_client.get(page)

                self.assertEqual(response.status_code, HTTPStatus.OK,
                                 f'Ошибка доступа к странице {page}')

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_url_names = {
            '/auth/login/': self.login_tmpl,
            '/auth/signup/': self.sign_up_tmpl,
            '/auth/password_change/done/': self.password_change_done_tmpl,
            '/auth/password_change/': self.password_change_tmpl,
            '/auth/password_reset/done/': self.password_reset_done_tmpl,
            '/auth/password_reset/': self.password_reset_tmpl,
            '/auth/reset/done/': self.password_reset_complete_tpl,
            '/auth/logout/': self.logout_tmpl,
            '/auth/reset/any/any/': self.password_reset_confirm_tmpl}

        for url, template in templates_url_names.items():
            with self.subTest(url=url):
                response = self.authorized_client.get(url, follow=True)

                self.assertTemplateUsed(response, template,
                                        f'Ошибка шаблона при вызове {url}')

    def test_user_pages_accessible_by_name(self):
        """URL, генерируемый страницами tests доступен."""
        responses = (
            self.authorized_client.get(reverse(self.login)),
            self.authorized_client.get(reverse(self.sign_up)),
            self.authorized_client.get(reverse(self.password_change)),
            self.authorized_client.get(reverse(self.password_change_done)),
            self.authorized_client.get(reverse(self.password_reset)),
            self.authorized_client.get(reverse(self.password_reset_done)),
            self.authorized_client.get(reverse(
                self.password_reset_confirm,
                kwargs={'uidb64': 'any', 'token': 'any'})),
            self.authorized_client.get(reverse(self.password_reset_complete)),
            self.authorized_client.get(reverse(self.logout)))

        for response in responses:
            with self.subTest(response=response):
                self.assertEqual(response.status_code, HTTPStatus.OK,
                                 'Ошибка доступа к страницам users')

    def test_about_pages_temlates(self):
        """проверка правильности шаблонов в users"""
        responses = {
            self.authorized_client.get(reverse(self.login)):
            self.login_tmpl,
            self.authorized_client.get(reverse(self.sign_up)):
            self.sign_up_tmpl,
            self.authorized_client.get(reverse(self.password_change)):
            self.password_change_tmpl,
            self.authorized_client.get(reverse(self.password_change_done)):
            self.password_change_done_tmpl,
            self.authorized_client.get(reverse(self.password_reset)):
            self.password_reset_tmpl,
            self.authorized_client.get(reverse(self.password_reset_done)):
            self.password_reset_done_tmpl,
            self.authorized_client.get(reverse(self.password_reset_complete)):
            self.password_reset_complete_tpl,
            self.authorized_client.get(reverse(
                self.password_reset_confirm,
                kwargs={'uidb64': 'any', 'token': 'any'})):
            self.password_reset_confirm_tmpl,
            self.authorized_client.get(reverse(self.logout)):
            self.logout_tmpl}

        for response, template in responses.items():
            with self.subTest(response=response):
                self.assertTemplateUsed(response, template,
                                        f'Ошибка шаблона {template}')

    def test_signup_context(self):
        """Шаблон signup сформирован с правильным контекстом."""
        response = self.guest_client.get(reverse(self.sign_up))
        form_fields = {'first_name': forms.fields.CharField,
                       'last_name': forms.fields.CharField,
                       'username': forms.fields.CharField,
                       'email': forms.fields.EmailField,
                       'password1': forms.fields.CharField,
                       'password2': forms.fields.CharField}

        for field, field_type in form_fields.items():
            with self.subTest(field=field):
                form_field = response.context['form'].fields[field]

                self.assertIsInstance(form_field, field_type,
                                      f'Ошибка вывода поля {field} в шаблон')

    def test_create_user(self):
        """Форма регистрации создает запись в User"""
        users_count = User.objects.count()
        form_data = {'first_name': 'Lando',
                     'last_name': 'Norris',
                     'username': 'McLaren',
                     'email': 'lando@mclaren.uk',
                     'password1': 'champion2023',
                     'password2': 'champion2023'}

        response = self.guest_client.post(reverse(self.sign_up),
                                          data=form_data, follow=True)

        self.assertRedirects(response,
                             reverse('posts:index'),
                             msg_prefix='Ошибка редиректа при создании юзера')
        self.assertEqual(User.objects.count(), users_count + 1,
                         'Ошибка создания юзера')
        self.assertTrue(User.objects.filter(first_name='Lando',
                                            last_name='Norris',
                                            username='McLaren',
                                            email='lando@mclaren.uk').exists(),
                        'Ошибка заполнения полей при создании юзера')
