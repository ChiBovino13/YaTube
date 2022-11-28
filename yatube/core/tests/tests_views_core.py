from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import Client, TestCase

User = get_user_model()


class ViewTestClass(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(
            username='Voland',
        )

    def setUp(self):
        cache.clear()
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_error_page(self):
        """
        Статус ответа сервера - 404.
        URL-адрес использует шаблон core/404.html.
        """
        response = self.client.get('/nonexist-page/')
        self.assertEqual(response.status_code, 404)
        self.assertTemplateUsed(response, 'core/404.html')
