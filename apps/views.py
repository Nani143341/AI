from django.contrib.auth.forms import UserCreationForm
from django.http import HttpResponse
from django.views.generic import TemplateView, ListView, DetailView
from django.shortcuts import render, redirect  # Import redirect
from .models import BlogPost, Post, Tag
from .forms import BlogPostForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum
from django.utils import timezone
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout

# Redirect to the login page if not authenticated


@login_required
def loginPage(request):
    if request.user.is_authenticated:
        return redirect('/')
    else:
        if request.method == 'POST':
            username = request.POST.get('username')
            password = request.POST.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('blog:home')
            else:
                messages.info(request, 'Incorrect Username or Password')
        context = {}
        return render(request, 'login.html', context)


# Redirect to the login page if not authenticated
@login_required
def logoutUser(request):
    logout(request)
    return redirect('login')


def register(request):
    if request.user.is_authenticated:
        return redirect('blog:home')
    else:
        form = UserCreationForm()
        if request.method == 'POST':
            form = UserCreationForm(request.POST)
            if form.is_valid():
                form.save()
                user = form.cleaned_data.get('username')
                messages.success(request, 'Account created for ' + user)
                return redirect('login')
        context = {'form': form}
        return render(request, 'register.html', context)


class BlogPostListView(ListView):
    model = BlogPost
    template_name = 'blog_post_list.html'
    context_object_name = 'posts'

    # Override the get_context_data method to add extra context data
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        latest_posts = Post.objects.all().order_by('-pub_date')[:5]
        popular_tags = Tag.objects.filter(popular=True)
        context['latest_posts'] = latest_posts
        context['popular_tags'] = popular_tags
        return context


class BlogPostDetailView(DetailView):
    model = BlogPost
    template_name = 'blog_post_detail.html'
    context_object_name = 'post'

    # Override the get_context_data method to add extra context data
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        latest_posts = Post.objects.all().order_by('-pub_date')[:5]
        popular_tags = Tag.objects.filter(popular=True)
        context['latest_posts'] = latest_posts
        context['popular_tags'] = popular_tags
        return context


@login_required
def create_blog_post(request):
    if request.method == 'POST':
        form = BlogPostForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('blog:blog_post_list')
    else:
        form = BlogPostForm()
    return render(request, 'blog_post_form.html', {'form': form})


@login_required
def create_blog(request):
    if request.method == 'POST':
        form = BlogPostForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('blog:blog_post_list')
    else:
        form = BlogPostForm()

    return render(request, 'create_blog_post.html', {'form': form})


def blog_post_list(request):
    posts = BlogPost.objects.all()
    return render(request, 'blog_post_list.html', {'posts': posts})


def about(request):
    if request.method == 'POST':
        form = BlogPostForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('blog_post_list')
    else:
        form = BlogPostForm()

    context = {
        'form': form,
        'arbitrary_date': 'September 37, 2023',
        'creator_name': 'The Hot News LLC',
        'current_year': 2023,
    }
    return render(request, 'about.html', context)


def hello(request):
    return HttpResponse("Hello, Django!")


class IndexView(TemplateView):
    template_name = "login.html"

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)

    def post(self, request, *args, **kwargs):

        # Retrieve username and password from the POST request
        username = request.POST.get('username')
        password = request.POST.get('password')

        # Log the user in
        user = authenticate(request, username=username, password=password)

        if user is not None:
            # Only log in if the user is found and authentication is successful
            login(request, user)
            return redirect('blog:index')
        else:
            # User not authenticated, render the login page with an error message
            error_message = "Authentication failed. Please check your username/password. New user register account"
            return render(request, self.template_name, {'error_message': error_message})


@login_required
def home(request):
    return render(request, 'index.html')


@login_required
def user_profile(request):
    return render(request, 'index.html')
