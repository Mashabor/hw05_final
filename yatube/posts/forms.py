from django import forms
from .models import Post, Comment


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('text', 'group', 'image')
        labels = {
            'text': 'Текст поста',
            'group': 'Группа'
        }
        help_texts = {
            'text': 'Введите текст поста',
            'group': 'Выберите группу'
        }

        def clean_text(self):
            data = self.cleaned_data['text']
            if data == '':
                raise forms.ValidationError(
                    'Напишите здесь что-нибудь'
                )
            return data


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('text',)
        labels = {
            'text': 'Текст комментария',
        }
        help_texts = {
            'text': 'Напишите комментарий',
        }

        def clean_text(self):
            data = self.cleaned_data['text']
            if data == '':
                raise forms.ValidationError('Вы не оставили комментарий')
            return data
