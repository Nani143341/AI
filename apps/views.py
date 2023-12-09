from django.http import HttpResponse
from django.views.generic import TemplateView, ListView, DetailView
from django.shortcuts import render, redirect  # Import redirect
from .models import BlogPost, Post, Tag
from .forms import BlogPostForm

# Remove the 'your_view' functions, they are not needed in this context.

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

def create_blog_post(request):
    if request.method == 'POST':
        form = BlogPostForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('blog_post_list')
    else:
        form = BlogPostForm()
    return render(request, 'blog_post_form.html', {'form': form})
    
def create_blog(request):
    if request.method == 'POST':
        form = BlogPostForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('blog_post_list')
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
    template_name = "index.html"

