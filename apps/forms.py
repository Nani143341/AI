# myapp/forms.py

from django import forms
from django.contrib.auth.models import User

from .models import (Article, BlogPost, Course, ForumComment, ForumThread,
                     Interest, Quiz, UserProfile)


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


# forms.py


class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)
    interests = forms.ModelMultipleChoiceField(
        queryset=Interest.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False
    )

    class Meta:
        model = User
        fields = ['username', 'password',
                  'confirm_password', 'email', 'interests']

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if not username[0].isalpha():
            raise forms.ValidationError("Username must start with a letter.")
        return username

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password and confirm_password and password != confirm_password:
            self.add_error('confirm_password', "Passwords do not match.")

        return cleaned_data


# Article Form
class ArticleForm(forms.ModelForm):
    class Meta:
        model = Article
        fields = ['title', 'content', 'category', 'is_premium']

# Course Form


class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ['title', 'description', 'video_url',
                  'difficulty', 'category', 'is_premium']

# Quiz Form


class QuizForm(forms.ModelForm):
    class Meta:
        model = Quiz
        fields = ['title', 'course', 'is_premium']

# Forum Thread Form


class ForumThreadForm(forms.ModelForm):
    class Meta:
        model = ForumThread
        fields = ['title', 'content']

# Forum Comment Form


class ForumCommentForm(forms.ModelForm):
    class Meta:
        model = ForumComment
        fields = ['content']
