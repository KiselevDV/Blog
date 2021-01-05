from django import forms

from .models import Comment


class EmailPostForm(forms.Form):
    """Форма отправки статьи на e-mail"""
    name = forms.CharField(max_length=25)
    email = forms.EmailField()
    to = forms.EmailField()
    # required=False - поле стало необязательным
    comments = forms.CharField(required=False, widget=forms.Textarea)


class CommentForm(forms.ModelForm):
    """Форма для комментария"""

    class Meta:
        model = Comment
        fields = ('name', 'email', 'body')


class SearchForm(forms.Form):
    """Полнотекстовый поиск"""
    query = forms.CharField()
