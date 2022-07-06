from http import HTTPStatus

from django.test import Client, TestCase
from django.urls import reverse


class AboutTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.about_author = '/about/author/'
        cls.about_tech = '/about/tech/'

    def setUp(self):
        self.guest_client = Client()

    def test_pages_for_all_users(self):
        """Проверка доступа к страницам  приложения about."""
        pages = (self.about_author, self.about_tech)

        for page in pages:
            with self.subTest(page=page):
                response = self.guest_client.get(page)

                self.assertEqual(response.status_code, HTTPStatus.OK,
                                 f'Ошибка доступа к странице {page}')

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_url_names = {
            self.about_author: 'about/author.html',
            self.about_tech: 'about/tech.html'}

        for url, template in templates_url_names.items():
            with self.subTest(url=url):
                response = self.guest_client.get(url)

                self.assertTemplateUsed(response, template,
                                        f'Ошибка шаблона при вызове {url}')

    def test_about_pages_accessible_by_name(self):
        """URL, генерируемый страницами about доступен."""
        responses = [self.guest_client.get(reverse('about:author')),
                     self.guest_client.get(reverse('about:tech'))]

        for response in responses:
            with self.subTest(response=response):

                self.assertEqual(response.status_code, HTTPStatus.OK,
                                 'Ошибка доступа к страницам about')

    def test_about_pages_temlates(self):
        """проверка правильности шаблонов в about"""
        responses = {self.guest_client.get(reverse('about:author')):
                     'about/author.html',
                     self.guest_client.get(reverse('about:tech')):
                     'about/tech.html'}

        for response, template in responses.items():
            with self.subTest(response=response):

                self.assertTemplateUsed(response, template,
                                        f'Ошибка шаблона {template}')
