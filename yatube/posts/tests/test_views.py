from django import forms
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.urls import reverse

from yatube.settings import POSTS_PER_PAGE

from ..models import Follow, Group, Post, User

NUMBER_OF_POSTS_FOR_THE_SECOND_PAGE = 3


class PostPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(
            username='Voland',
        )
        cls.user2 = User.objects.create_user(
            username='Tamtamtam',
        )
        cls.group = Group.objects.create(
            title='Тестовый заголовок',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        cls.post = Post.objects.create(
            text='Тестовый текст',
            author=cls.user,
            group=cls.group,
            image=SimpleUploadedFile(
                name='small.gif',
                content=PostPagesTests.small_gif,
                content_type='image/gif'
            ),
        )

    def setUp(self):
        cache.clear()
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_pages_uses_correct_template(self):
        cache.clear()
        """URL-адрес использует соответствующий шаблон."""
        templates_page_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:follow_index'): 'posts/follow.html',
            reverse('posts:groups'): 'posts/groups.html',
            reverse(
                'posts:group_list', kwargs={
                    'slug': PostPagesTests.group.slug
                }
            ): 'posts/group_list.html',
            reverse(
                'posts:profile', kwargs={
                    'username': PostPagesTests.user.username
                }
            ): 'posts/profile.html',
            reverse('posts:post_create'): 'posts/create_post.html',
            reverse(
                'posts:post_edit', kwargs={
                    'post_id': PostPagesTests.post.id
                }
            ): 'posts/create_post.html',
            reverse(
                'posts:post_detail', kwargs={
                    'post_id': PostPagesTests.post.id
                }
            ): 'posts/post_detail.html',
        }
        for reverse_name, template in templates_page_names.items():
            with self.subTest(template=template):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def context_for_all_with_page_obj(self, response):
        cache.clear()
        """Функция для проверки контекста страниц с page_obj в контексте."""
        self.assertTrue(
            response.context.get(
                'page_obj'
            ).paginator.count >= 1, 'На странице нет постов'
        )
        first_object = response.context['page_obj'][0]
        objects = {
            self.post.text: first_object.text,
            self.post.image: first_object.image,
            self.post.id: first_object.id,
            self.user: first_object.author,
            self.group.slug: first_object.group.slug,
            self.group.title: first_object.group.title,
            self.group.description: first_object.group.description,
        }
        for reverse_name, response_name in objects.items():
            with self.subTest(reverse_name=reverse_name):
                self.assertEqual(response_name, reverse_name)

    def context_for_all_without_page_obj(self, response):
        cache.clear()
        """Функция для проверки контекста страниц без page_obj в контексте."""
        self.assertTrue(response.context['post'], 'На странице нет постов')
        objects = {
            self.post.text: response.context.get('post').text,
            self.post.image: response.context.get('post').image,
            self.post.id: response.context.get('post').id,
            self.user: response.context.get('post').author,
            self.group: response.context.get('post').group,
            self.post: response.context['post'],
        }
        for reverse_name, response_name in objects.items():
            with self.subTest(reverse_name=reverse_name):
                self.assertEqual(response_name, reverse_name)

    def test_index_page_show_correct_context(self):
        cache.clear()
        """Шаблон index сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:index'))
        PostPagesTests.context_for_all_with_page_obj(self, response)

    def test_group_list_page_show_correct_context(self):
        cache.clear()
        """Шаблон group_list сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse(
                'posts:group_list', kwargs={
                    'slug': PostPagesTests.group.slug
                }
            )
        )
        PostPagesTests.context_for_all_with_page_obj(self, response)

    def test_profile_page_show_correct_context(self):
        cache.clear()
        """Шаблон profile сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse(
                'posts:profile', kwargs={
                    'username': PostPagesTests.user.username
                }
            )
        )
        PostPagesTests.context_for_all_with_page_obj(self, response)

    def test_post_detail_page_show_correct_context(self):
        cache.clear()
        """Шаблон post_detail сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse(
                'posts:post_detail', kwargs={
                    'post_id': PostPagesTests.post.id
                }
            )
        )
        PostPagesTests.context_for_all_without_page_obj(self, response)

    def test_post_edit_page_show_correct_context(self):
        cache.clear()
        """Шаблон post_edit сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse(
                'posts:post_edit', kwargs={
                    'post_id': self.post.id
                }
            )
        )
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
            'image': forms.fields.ImageField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                self.assertIsInstance(form_field, expected)
        PostPagesTests.context_for_all_without_page_obj(self, response)
        self.assertEqual(response.context['is_edit'], True)

    def test_post_create_correct_context(self):
        cache.clear()
        """Шаблон post_create сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:post_create'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.models.ModelChoiceField,
            'image': forms.fields.ImageField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_author_cannot_follow_himself(self):
        cache.clear()
        """"Автор не может подписаться сам на себя."""
        follow_user = Follow.objects.filter(author=self.user, user=self.user)
        self.assertIsNotNone(
            follow_user, 'Автор не может подписаться сам на себя '
        )

    def user_can_follow_author(self):
        cache.clear()
        """"Пользователь может подписаться на автора."""
        Follow.objects.get_or_create(
            user=self.user,
            author=self.user2
        )
        follow_url = reverse(
            'posts:profile_follow',
            kwargs={'username': self.user2}
        )
        self.authorized_client.get(follow_url)
        self.assertFalse(
            Follow.objects.filter(
                user=self.user,
                author=self.user2,
            ).exists()
        )

    def user_can_unfollow_author(self):
        cache.clear()
        """"Пользователь может отписаться от автора."""
        Follow.objects.get_or_create(
            user=self.user,
            author=self.user2
        )
        unfollow_url = reverse(
            'posts:profile_unfollow',
            kwargs={'username': self.user2}
        )
        self.authorized_client.get(unfollow_url)
        self.assertFalse(
            Follow.objects.filter(
                user=self.user,
                author=self.user2,
            ).exists()
        )

    def post_create_in_follow(self):
        cache.clear()
        """"
        Проверяем, что новый пост появился в ленте тех,
        кто на него подписан.
        """
        Follow.objects.get_or_create(
            user=self.user,
            author=self.user2
        )
        response = reverse('posts:follow_index')
        self.assertEqual(
            len(Follow.objects.count()), response.context.count() + 1
        )

    def post_not_create_in_follow(self):
        cache.clear()
        """"
        Проверяем, что новый пост не появился в ленте тех,
        кто на него не подписан.
        """
        Follow.objects.get_or_create(
            user=self.user,
            author=self.user2,
        )
        response = self.follower_client.get('posts:follow_index')
        count_post_follower = len(response.context['page_obj'])
        self.assertEqual(len(
            response.context['page_obj']), count_post_follower
        )


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(
            username='Fagot',
        )
        cls.group = Group.objects.create(
            title='Тестовый заголовок2',
            slug='test-slug2',
            description='Тестовое описание2',
        )
        cls.post = [Post(
            text=f'Тестовый текст {post}',
            group=cls.group,
            author=cls.user,)
            for post in range(
                POSTS_PER_PAGE + NUMBER_OF_POSTS_FOR_THE_SECOND_PAGE
        )
        ]
        Post.objects.bulk_create(cls.post)

    def setUp(self):
        cache.clear()
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_index_first_page_contains_ten_records(self):
        cache.clear()
        """
        В шаблонах index, group_list и profile на первой странице
        отображается 10 постов, на второй странице - 3 поста.
        """
        field_paginator = {
            self.authorized_client.get(reverse('posts:index')): POSTS_PER_PAGE,
            self.authorized_client.get(
                reverse(
                    'posts:group_list', kwargs={
                        'slug': self.group.slug
                    }
                )
            ): POSTS_PER_PAGE,
            self.authorized_client.get(
                reverse(
                    'posts:profile', kwargs={
                        'username': self.user.username
                    }
                )
            ): POSTS_PER_PAGE,
            self.client.get(
                reverse('posts:index') + '?page=2'
            ): NUMBER_OF_POSTS_FOR_THE_SECOND_PAGE,
            self.authorized_client.get(
                reverse(
                    'posts:group_list', kwargs={
                        'slug': self.group.slug
                    }
                ) + '?page=2'
            ): NUMBER_OF_POSTS_FOR_THE_SECOND_PAGE,
            self.authorized_client.get(
                reverse(
                    'posts:profile', kwargs={
                        'username': self.user.username
                    }
                ) + '?page=2'
            ): NUMBER_OF_POSTS_FOR_THE_SECOND_PAGE,
        }
        for response, expected_value in field_paginator.items():
            with self.subTest(response=response):
                self.assertEqual(
                    len(response.context['page_obj']), expected_value
                )


class CreatingPostTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(
            username='Gella',
        )
        cls.group = Group.objects.create(
            title='Группа с постом',
            slug='with',
            description='Группа, в которой появился пост',
        )
        cls.group_1 = Group.objects.create(
            title='Группа без поста',
            slug='without',
            description='Группа, в которой никакого поста не появилось',
        )
        cls.small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        cls.post = Post.objects.create(
            text='Мистер тестовый постик',
            author=cls.user,
            group=cls.group,
            image=SimpleUploadedFile(
                name='small.gif',
                content=CreatingPostTests.small_gif,
                content_type='image/gif'
            ),
        )

    def setUp(self):
        cache.clear()
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_post_create(self):
        cache.clear()
        """"
        Проверяем, что пост с изображением появился на страницах
        index, group_list, post_detail и profile.
        """
        page_names = {
            reverse('posts:index'),
            reverse(
                'posts:group_list', kwargs={
                    'slug': CreatingPostTests.group.slug
                }
            ),
            reverse(
                'posts:profile', kwargs={
                    'username': CreatingPostTests.user.username
                }
            ),
            reverse(
                'posts:post_detail', kwargs={
                    'post_id': CreatingPostTests.post.id
                }
            ),
            reverse('posts:follow_index'),
        }
        for page in page_names:
            with self.subTest():
                response = self.authorized_client.get(page)
                post_1 = response.context['page_obj'][0]
                self.assertEqual(response.context['page_obj'][0], 1)
                self.assertEqual(post_1.group.title, self.group.title)

    def test_post_create(self):
        cache.clear()
        """"Проверяем, что новый пост не попал в другую группу."""
        response = self.authorized_client.get(
            reverse(
                'posts:group_list', kwargs={
                    'slug': CreatingPostTests.group_1.slug
                }
            ),
        )
        self.assertEqual(response.context.get('page_obj').paginator.count, 0)
