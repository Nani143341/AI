# myapp/forms.py

from django import forms
from .models import BlogPost


class MyForm(forms.ModelForm):
    class Meta:
        model = BlogPost
        fields = ['title', 'content']

    widgets = {
        'title': forms.TextInput(attrs={'class': 'form-control'}),
        'content': forms.Textarea(attrs={'class': 'form-control'}),
    }


class BlogPostForm(forms.ModelForm):
    class Meta:
        model = BlogPost
        fields = ['title', 'content']
