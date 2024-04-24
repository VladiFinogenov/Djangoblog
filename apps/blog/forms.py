from django import forms
from .models import Comment, Post


class SearchForm(forms.Form):
    """ Форма для поиска постов. """

    query = forms.CharField()


class PostCreateForm(forms.ModelForm):
    """
    Форма добавления статей на сайте
    """

    class Meta:
        model = Post
        fields = (
            'title', 'category', 'tags',
            'description', 'text', 'thumbnail', 'status',
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field in self.fields:
            self.fields[field].widget.attrs.update(
                {'class': 'form-control', 'autocomplete': 'off'}
            )

        # self.fields['description'].widget.attrs.update({'rows': 4, 'cols': 84})
        self.fields['text'].widget.attrs.update(
            {'class': 'form-control django_ckeditor_5'},
            config_name="extend"
        )
        self.fields['text'].required = False


class PostUpdateForm(PostCreateForm):
    """
    Форма обновления статьи на сайте
    """

    class Meta:
        model = Post
        fields = PostCreateForm.Meta.fields + ('updater', 'fixed')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['fixed'].widget.attrs.update({'class': 'form-check-input'})
        self.fields['text'].widget.attrs.update(
            {'class': 'form-control django_ckeditor_5'},
            config_name="extend"
        )
        self.fields['text'].required = False


class CommentCreateForm(forms.ModelForm):
    """
    Форма добавления комментариев к статьям
    """
    parent = forms.IntegerField(widget=forms.HiddenInput, required=False)
    content = forms.CharField(label='', widget=forms.Textarea(
        attrs={'cols': 30, 'rows': 5, 'placeholder': 'Комментарий', 'class': 'form-control'}))

    class Meta:
        model = Comment
        fields = ('content',)
