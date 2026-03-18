from django import forms
from .models import Post, Comment, Tag


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['description', 'status', ]
        labels = {'description': 'Description',
                  'status': 'Status', }
        widgets = {
            'description': forms.Textarea(attrs={
                'class': 'form-control form-control-lg',
                'rows': 4,
                'placeholder': 'Write something interesting...'
            }),
            'status': forms.Select(attrs={
                'class': 'form-select'
            }),
        }


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text']
        widgets = {
            'text': forms.Textarea(attrs={
                'class': 'form-control me-2',
                'rows': 2,
                'placeholder': 'Add a comment...'
            }),
        }


class TagForm(forms.ModelForm):
    class Meta:
        model = Tag
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Add a tag...'}),
        }
