from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import Client, TestCase
from django.urls import reverse
from posts.models import Post

User = get_user_model()


class CacheTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(
            username='Voland',
        )
        cls.post = Post.objects.create(
            text='Мистер тестовый постик',
            author=cls.user,
        )

    def setUp(self):
        cache.clear()
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_cache_index(self):
        """Проверка кеширования главной страницы."""
        response = self.authorized_client.get(reverse('posts:index'))
        Post.objects.get(
            text='Мистер тестовый постик',
            author=self.user,
        ).delete()
        response_2 = self.authorized_client.get(reverse('posts:index'))
        self.assertEqual(response.content, response_2.content)
        cache.clear()
        response_3 = self.authorized_client.get(reverse('posts:index'))
        self.assertNotEqual(response.content, response_3.content)
