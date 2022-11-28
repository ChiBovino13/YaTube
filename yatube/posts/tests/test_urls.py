from http import HTTPStatus

from django.core.cache import cache
from django.test import Client, TestCase

from ..models import Group, Post, User


class PostsURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        cache.clear()
        super().setUpClass()
        cls.user = User.objects.create_user(
            username='test_name',
        )
        cls.user_2 = User.objects.create_user(
            username='test_name_2',
        )
        cls.group = Group.objects.create(
            title='Тестовый заголовок',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            text='Тестовый текст',
            author=cls.user,
        )
        cls.post_2 = Post.objects.create(
            text='Тестовый текст 2',
            author=cls.user_2,
        )
        cls.guest_client = Client()
        cls.authorized_client = Client()
        cls.authorized_client.force_login(PostsURLTests.user)
        cls.urls_quest = {
            'index_quest': PostsURLTests.guest_client.get('/'),
            'group_list_quest': PostsURLTests.guest_client.get(
                '/group/test-slug/'
            ),
            'profile_quest': PostsURLTests.guest_client.get(
                '/profile/test_name/'
            ),
            'posts_detail_quest': PostsURLTests.guest_client.get(
                f'/posts/{PostsURLTests.post.id}/'
            ),
            'post_edit_quest': PostsURLTests.guest_client.get(
                f'/posts/{PostsURLTests.post.id}/edit/'
            ),
            'posts_create_quest': PostsURLTests.guest_client.get('/create/'),
        }
        cls.urls_authorized = {
            'index_authorized': PostsURLTests.authorized_client.get('/'),
            'group_list_authorized': PostsURLTests.authorized_client.get(
                '/group/{PostsURLTests.group.slug}/'
            ),
            'profile_authorized': PostsURLTests.authorized_client.get(
                '/profile/{PostsURLTests.user.username}/'
            ),
            'posts_detail_authorized': PostsURLTests.authorized_client.get(
                f'/posts/{PostsURLTests.post.id}/'
            ),
            'post_edit_authorized': PostsURLTests.authorized_client.get(
                f'/posts/{PostsURLTests.post.id}/edit/'
            ),
            'posts_create_authorized': PostsURLTests.authorized_client.get(
                '/create/'
            ),
        }

    def test_guest_client(self):
        """
        Страницы index, group_list, profile, posts_detail
        доступны любому пользователю.
        """
        urls_guest_list = [
            self.urls_quest['index_quest'],
            self.urls_quest['group_list_quest'],
            self.urls_quest['profile_quest'],
            self.urls_quest['posts_detail_quest'],
        ]
        for value in urls_guest_list:
            with self.subTest(value=value):
                self.assertEqual(
                    value.status_code, HTTPStatus.OK)

    def test_authorized_client(self):
        """
        Страницы post_edit, posts_create
        доступны авторизованному пользователю.
        """
        urls_authorized_list = [
            self.urls_authorized['post_edit_authorized'],
            self.urls_authorized['posts_create_authorized'],
        ]
        for value in urls_authorized_list:
            with self.subTest(value=value):
                self.assertEqual(
                    value.status_code, HTTPStatus.OK)

    def test_posts_edit_posts_create_redirect_anonymous_on_admin_login(self):
        """
        Страницы post_edit, posts_create
        перенаправят анонимного пользователя.
        """
        urls_quest_list = [
            self.urls_quest['post_edit_quest'],
            self.urls_quest['posts_create_quest'],
        ]
        for value in urls_quest_list:
            with self.subTest(value=value):
                self.assertEqual(
                    value.status_code, HTTPStatus.FOUND)

    def test_posts_edit_url_redirect_not_author(self):
        """
        Страница post_edit перенаправит авторизированного
        пользователя, но не автора поста.
        """
        response = self.authorized_client.get(
            f'/posts/{self.post_2.id}/edit/'
        )
        self.assertEqual(response.status_code, HTTPStatus.FOUND)

    def test_unexisting_page_url_redirect_anonymous_on_admin_login(self):
        """
        Страница unexisting_page и add_comment вернет
        неавторизированному пользователю ошибку 404.
        """
        response = [
            self.guest_client.get('/unexisting_page/'),
            self.guest_client.get('/posts/1/comment//'),
        ]
        for value in response:
            with self.subTest(value=value):
                self.assertEqual(
                    value.status_code, HTTPStatus.NOT_FOUND)

    def test_urls_uses_correct_template(self):
        cache.clear()
        """URL-адрес использует соответствующий шаблон."""
        templates_url_names = {
            '/': 'posts/index.html',
            '/group/test-slug/': 'posts/group_list.html',
            '/profile/test_name/': 'posts/profile.html',
            '/posts/1/': 'posts/post_detail.html',
            '/create/': 'posts/create_post.html',
            '/posts/1/edit/': 'posts/create_post.html',
        }
        for url, template in templates_url_names.items():
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertTemplateUsed(response, template)
