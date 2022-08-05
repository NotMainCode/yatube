from django import forms

from .models import Comment, Post


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ("text", "group", "image")
        labels = {
            "text": "Текст поста",
            "group": "Группа",
            "image": "Картинка",
        }
        help_texts = {
            "text": "Текст нового поста",
            "group": "Группа, к которой будет относиться пост",
        }

    def clean_text(self):
        data = self.cleaned_data["text"]
        if not data:
            raise forms.ValidationError("Заполните поле для текста записи")
        return data


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ("text",)

    def clean_text(self):
        data = self.cleaned_data["text"]
        if not data:
            raise forms.ValidationError(
                "Заполните поле для текста комментария"
            )
        return data
