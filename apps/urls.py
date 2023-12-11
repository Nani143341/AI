"""
URL configuration for myapp project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path
from . import views
from .views import IndexView  # Import IndexView here

app_name = 'blog'  # Add this line to specify the app namespace


urlpatterns = [
    path('hello/', views.hello, name='hello'),
    path('', views.home, name='home'),
    path('accounts/profile/', views.user_profile, name='user_profile'),
    path('login/', views.loginPage, name='login'),
    path('logout/', views.logoutUser, name='logout'),
    path('register/', views.register, name='register'),
    path('index/', views.IndexView.as_view(), name='index'),
    path('', IndexView.as_view(), name='home'),
    path('blog/', views.BlogPostListView.as_view(), name='blog_post_list.html'),
    path('blog/<int:pk>/', views.BlogPostDetailView.as_view(),
         name='blog_post_detail.htm'),
    path('blog/create/', views.create_blog_post, name='create_blog_post.html'),
    path('create-blog/', views.create_blog, name='create_blog_post.html'),
    path('about/', views.about, name='about.html'),
]
