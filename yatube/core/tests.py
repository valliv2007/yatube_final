from http import HTTPStatus

from django.test import TestCase


class CoreTests(TestCase):
    def test_unexisting_page(self):
        """Cтраница 404 отдает кастомный шаблон."""
        response = self.client.get('/anything/')

        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND,
                         'Ошибка доступа к несуществующей странице')
        self.assertTemplateUsed(
            response, 'core/404.html',
            'Ошибка шаблона при вызове несуществующей страницы')
