# myapp/models.py

from django.db import models
from django.contrib.auth.models import User


class BlogPost(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    content = models.TextField()
    pub_date = models.DateTimeField('date published')

    def __str__(self):
        return self.title


class Post(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    pub_date = models.DateTimeField('date published')

    def __str__(self):
        return self.title


class Tag(models.Model):
    name = models.CharField(max_length=100)
    popular = models.BooleanField(default=False)

    def __str__(self):
        return self.name
