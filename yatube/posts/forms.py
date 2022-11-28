from django import forms

from .models import Comment, Post


class PostForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['text'].widget.attrs['placeholder'] = (
            'Введите какой-нибудь текст, ну пожалуйста 😥')
        self.fields['group'].empty_label = (
            'Нажмите сюда, чтобы выбрать группу')

    class Meta:
        model = Post
        fields = ('text', 'group', 'image',)
        labels = {
            'text': 'Пост:',
            'group': 'Группа',
            'image': 'Изабражение',
        }
        help_texts = {
            'text': 'Напишите пост и нажмите "Добавить"',
            'group': 'Выбирать группу не обязательно',
            'image': 'Вы можете добавить изображение. '
                     'Оно будет обрезано до формата 960x339 px.',
        }


class CommentForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['text'].widget.attrs['placeholder'] = (
            'Ваш комментарий')

    class Meta:
        model = Comment
        fields = ('text',)
        labels = {
            'text': 'Комментарий:',
        }
        help_texts = {
            'text': 'Напишите комментарий и нажмите "Добавить"',
        }
