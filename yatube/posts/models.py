from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Group(models.Model):
    """Задает название, описание группы, ссылку в адресной строке"""
    title = models.CharField(max_length=200, verbose_name='Название группы')
    slug = models.SlugField(unique=True, verbose_name='Адрес')
    description = models.TextField(verbose_name='Описание группы')

    class Meta:
        verbose_name_plural = 'Группы'
        verbose_name = 'название группы'

    def __str__(self):
        return f' {self.title}'


class Post(models.Model):
    """Задает текст поста, дату публикации, автора и группу"""
    text = models.TextField(
        verbose_name='Содержание записи',
        help_text='Введите текст поста')
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата публикации')
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name='Автор публикации'
    )
    group = models.ForeignKey(
        Group,
        on_delete=models.SET_NULL,
        related_name='posts',
        blank=True,
        null=True,
        verbose_name='Название группы',
        help_text='Группа, к которой будет относиться пост'
    )
    image = models.ImageField(
        'Картинка',
        upload_to='posts/',
        blank=True
    )

    class Meta:
        verbose_name_plural = 'Посты'
        verbose_name = 'Пост'
        ordering = ['-pub_date']

    def __str__(self):
        return self.text[:15]


class Comment(models.Model):
    """
    Ссылка на пост и автора комментария,
    текст комментария, дата и время комментария.
    """
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Пост',
        help_text='Под каким постом оставлен комментарий'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Автор комментария',
        help_text='Автор отображается на сайте'
    )
    text = models.TextField(
        verbose_name='Текст комментария',
        help_text='Обязательное поле, не должно быть пустым'
    )
    created = models.DateTimeField(
        verbose_name='Дата публикации',
        help_text='Дата публикации',
        auto_now_add=True
    )
    image = models.ImageField(
        'Картинка',
        upload_to='posts/',
        blank=True
    )

    class Meta:
        ordering = ('-created',)
        verbose_name_plural = 'Комментарии к постам'

    def __str__(self):
        return self.text


class Follow(models.Model):
    """Подписка пользователя на автора."""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Пользователь',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='Автор',
    )

    class Meta:
        verbose_name_plural = 'Подписки на авторов'

    def __str__(self):
        return self.text
