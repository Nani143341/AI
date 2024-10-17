import pdb
import re
from datetime import timedelta

import requests
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.db import models
from django.db.models import Avg, Count, Q, Sum
from django.http import HttpResponse
from django.shortcuts import (get_object_or_404, redirect,  # Import redirect
                              render)
from django.urls import reverse
from django.utils import timezone
from django.utils.text import slugify
from django.views.generic import DetailView, ListView, TemplateView
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from .forms import (ArticleForm, BlogPostForm, CourseForm, ForumCommentForm,
                    ForumThreadForm, QuizForm, UserRegistrationForm)
from .models import (Article, BlogPost, Course,  # Import your models
                     ForumComment, ForumThread, Post, Question, Quiz, Tag,
                     UserBadge, UserCourseEnrollment, UserCourseProgress,
                     UserProfile, UserQuizResult)


@login_required
def edit_blog_post(request, pk):
    post = get_object_or_404(BlogPost, pk=pk)

    if request.method == 'POST':
        form = BlogPostForm(request.POST, instance=post)
        if form.is_valid():
            form.save()
            # Redirect to the blog post list
            return redirect('blog:blog_post_list')
    else:
        form = BlogPostForm(instance=post)

    return render(request, 'edit_blog_post.html', {'form': form, 'post': post})


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
                if user.profile.is_premium:  # Assuming profile stores user role
                    return redirect('blog:premium_dashboard')
                else:
                    redirect('blog:home')
            else:
                messages.info(request, 'Incorrect Username or Password')
        context = {}
        return render(request, 'login.html', context)


@login_required
def premium_dashboard(request):
    # Load premium courses and user progress
    courses = Course.objects.filter(is_premium=True)
    user_progress = request.user.get_course_progress()
    return render(request, 'premium_dashboard.html', {'courses': courses, 'progress': user_progress})


# youtube_service.py

YOUTUBE_API_SERVICE_NAME = 'youtube'
YOUTUBE_API_VERSION = 'v3'


def search_educational_videos(query):
    try:
        youtube = build(
            YOUTUBE_API_SERVICE_NAME,
            YOUTUBE_API_VERSION,
            developerKey=settings.YOUTUBE_API_KEY
        )
        request = youtube.search().list(
            q=query + ' tutorial',  # Add additional keywords to narrow down the search
            part='snippet',
            type='video',
            maxResults=5,
            videoCategoryId='27',
            safeSearch='strict'
        )
        response = request.execute()
        return [item['id']['videoId'] for item in response.get('items', [])]

    except HttpError as e:
        error_reason = e.content.decode("utf-8")
        print(f"YouTube API Error: {error_reason}")
        # Handle the error as needed, e.g., log it or return an empty list
        return []


# Redirect to the login page if not authenticated
@login_required
def logoutUser(request):
    logout(request)
    return redirect(reverse('blog:login'))


def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(
                request, 'Registration successful! Welcome to the platform.')
            # Redirect to a home page or dashboard after registration
            return redirect('blog:home')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = UserRegistrationForm()
    return render(request, 'register.html', {'form': form})


class BlogPostListView(ListView):
    model = BlogPost
    template_name = 'blog_post_list.html'
    context_object_name = 'posts'

    def get_queryset(self):
        query = self.request.GET.get('q')

        if query:
            return BlogPost.objects.filter(Q(title__icontains=query))
        else:
            return BlogPost.objects.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        latest_posts = Post.objects.all().order_by('-pub_date')[:5]
        popular_tags = Tag.objects.filter(popular=True)
        context['latest_posts'] = latest_posts
        context['popular_tags'] = popular_tags
        context['query'] = self.request.GET.get('q', '')
        context['message'] = f'Search results for "{context["query"]}"' if context['query'] else 'All Blog Posts'
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
            form.instance.user = request.user
            form.instance.pub_date = timezone.now()
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
            form.instance.user = request.user
            form.instance.pub_date = timezone.now()
            form.save()
            return redirect('blog:blog_post_list')
    else:
        form = BlogPostForm()

    return render(request, 'create_blog_post.html', {'form': form})


@login_required
def blog_post_list(request):
    posts = BlogPost.objects.all()
    return render(request, 'blog_post_list.html', {'posts': posts})


@login_required
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
    # Replace with the logic to get featured courses
    courses = Course.objects.all()
    # Replace with your logic for articles
    articles = Article.objects.all()[:5]
    # Filter out premium courses
    premium_courses = courses.filter(is_premium=True)
    # Filter out non-premium courses
    regular_courses = courses.filter(is_premium=False)

    # Sample AI news data
    news_feed = [
        {
            "title": "OpenAI Introduces New ChatGPT Model",
            # Replace with actual announcement
            "url": "https://openai.com/blog/introducing-chatgpt-4/",
            "source": "OpenAI Blog"
        },
        {
            "title": "AI Breakthrough in Healthcare: Diagnosing Diseases Faster",
            "url": "https://www.weforum.org/agenda/2024/09/how-ai-is-improving-diagnostics-and-health-outcomes-transforming-healthcare",
            "source": "World Economic Forum"  # Updated source based on real article
        },
        {
            "title": "Google's AI Strategy in 2024",
            # Example article
            "url": "https://www.theverge.com/2024/8/12/22073124/google-ai-strategy-deepmind-lamda",
            "source": "The Verge"
        },
        {
            "title": "How AI is Transforming the Finance Industry",
            "url": "https://www.bloomberg.com/news/articles/2024-09-26/how-ai-is-reshaping-finance",
            "source": "Bloomberg"
        },
        {
            "title": "Top AI Trends to Watch in 2024",
            "url": "https://www.forbes.com/sites/bernardmarr/2024/01/10/top-10-artificial-intelligence-trends-to-watch-in-2024/",
            "source": "Forbes"
        },
        {
            "title": "AI Regulation on the Horizon",
            "url": "https://www.reuters.com/technology/governments-race-regulate-ai-tools-2023-10-13/",
            "source": "Reuters"
        },
        {
            "title": "Bias in AI: Mitigating Algorithmic Inequality",
            "url": "https://www.wired.com/story/recruiters-ai-application-overload/",
            "source": "Wired"
        },
        {
            "title": "AI-Powered Customer Service Revolutionizes Interactions",
            "url": "https://www.forbes.com/sites/sunilrajaraman/2024/06/18/ai-driven-customer-service-is-gaining-steam/",
            "source": "Forbes"
        },
        {
            "title": "AI Optimizes Supply Chains for Efficiency and Cost Savings",
            "url": "https://www.mckinsey.com/industries/metals-and-mining/our-insights/succeeding-in-the-ai-supply-chain-revolution",
            "source": "McKinsey & Company"
        },
        {
            "title": "AI Fights Climate Change: Predicting Disasters and Saving Energy",
            "url": "https://www.technologyreview.com/topic/climate-change/",
            "source": "MIT Technology Review"
        },
        {
            "title": "AI Protects Endangered Species and Combats Poaching",
            "url": "https://www.nationalgeographic.com/animals/article/artificial-intelligence-counts-wild-animals",
            "source": "National Geographic"
        }
    ]

    context = {
        'courses': courses,
        'premium_courses': premium_courses,
        'regular_courses': regular_courses,
        'articles': articles,
        'news_feed': news_feed
    }

    return render(request, 'index.html', context)


# views.py


@login_required
def upgrade_to_premium(request):
    """View for upgrading a user to a premium subscription."""
    user_profile = UserProfile.objects.get(user=request.user)

    if request.method == 'POST':
        # Assume there's a valid payment or other verification process
        # Here, we directly update the subscription status
        user_profile.subscription_status = True
        user_profile.subscription_start_date = timezone.now().date()
        user_profile.subscription_end_date = timezone.now(
        ).date() + timedelta(days=365)  # 1-year subscription
        user_profile.save()
        # Retrieve the course title from session and redirect back to the course
        course_title = request.session.get('course_title', None)
        if course_title:
            # Convert the course title back to slug format and redirect
            course_slug = course_title.replace(' ', '-')
            return redirect('blog:course_detail', slug=course_slug)

        # If no course was found in the session, redirect to the home page or course list
        return redirect('blog:home')

    return render(request, 'upgrade_to_premium.html')


@login_required
def process_payment(request):
    """Handles payment processing for upgrading to premium."""
    if request.method == 'POST':
        payment_plan = request.POST.get('payment_plan')
        # In a real app, payment gateway integration would be here

        # Assuming payment is successful
        request.user.is_premium = True  # Set the user as premium
        request.user.save()

        messages.success(
            request, "Payment successful! You've been upgraded to Premium.")
        return redirect('blog:home')
    else:
        messages.error(request, "Invalid payment request.")
        return redirect('upgrade_to_premium')


@login_required
def user_profile(request):
    # Replace with the logic to get featured courses
    courses = Course.objects.all()
    # Replace with your logic for articles
    articles = Article.objects.all()[:5]
    # Filter out premium courses
    premium_courses = courses.filter(is_premium=True)
    # Filter out non-premium courses
    regular_courses = courses.filter(is_premium=False)

    # Sample AI news data
    news_feed = [
        {
            "title": "OpenAI Introduces New ChatGPT Model",
            # Replace with actual announcement
            "url": "https://openai.com/blog/introducing-chatgpt-4/",
            "source": "OpenAI Blog"
        },
        {
            "title": "AI Breakthrough in Healthcare: Diagnosing Diseases Faster",
            "url": "https://www.weforum.org/agenda/2024/09/how-ai-is-improving-diagnostics-and-health-outcomes-transforming-healthcare",
            "source": "World Economic Forum"  # Updated source based on real article
        },
        {
            "title": "Google's AI Strategy in 2024",
            # Example article
            "url": "https://www.theverge.com/2024/8/12/22073124/google-ai-strategy-deepmind-lamda",
            "source": "The Verge"
        },
        {
            "title": "How AI is Transforming the Finance Industry",
            "url": "https://www.bloomberg.com/news/articles/2024-09-26/how-ai-is-reshaping-finance",
            "source": "Bloomberg"
        },
        {
            "title": "Top AI Trends to Watch in 2024",
            "url": "https://www.forbes.com/sites/bernardmarr/2024/01/10/top-10-artificial-intelligence-trends-to-watch-in-2024/",
            "source": "Forbes"
        },
        {
            "title": "AI Regulation on the Horizon",
            "url": "https://www.reuters.com/technology/governments-race-regulate-ai-tools-2023-10-13/",
            "source": "Reuters"
        },
        {
            "title": "Bias in AI: Mitigating Algorithmic Inequality",
            "url": "https://www.wired.com/story/recruiters-ai-application-overload/",
            "source": "Wired"
        },
        {
            "title": "AI-Powered Customer Service Revolutionizes Interactions",
            "url": "https://www.forbes.com/sites/sunilrajaraman/2024/06/18/ai-driven-customer-service-is-gaining-steam/",
            "source": "Forbes"
        },
        {
            "title": "AI Optimizes Supply Chains for Efficiency and Cost Savings",
            "url": "https://www.mckinsey.com/industries/metals-and-mining/our-insights/succeeding-in-the-ai-supply-chain-revolution",
            "source": "McKinsey & Company"
        },
        {
            "title": "AI Fights Climate Change: Predicting Disasters and Saving Energy",
            "url": "https://www.technologyreview.com/topic/climate-change/",
            "source": "MIT Technology Review"
        },
        {
            "title": "AI Protects Endangered Species and Combats Poaching",
            "url": "https://www.nationalgeographic.com/animals/article/artificial-intelligence-counts-wild-animals",
            "source": "National Geographic"
        }
    ]

    context = {
        'courses': courses,
        'premium_courses': premium_courses,
        'regular_courses': regular_courses,
        'articles': articles,
        'news_feed': news_feed
    }

    return render(request, 'index.html', context)


def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Use get_or_create to avoid duplicates
            UserProfile.objects.get_or_create(user=user)
            login(request, user)
            return redirect('blog:home')
    else:
        form = UserRegistrationForm()
    return render(request, 'register.html', {'form': form})


def quiz_view(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)

    if request.method == 'POST':
        # Handle quiz submission
        score = 0
        for question in quiz.questions.all():  # Using the related_name
            user_answer = request.POST.get(str(question.id))
            if user_answer == question.correct_answer:  # Assuming a correct_answer field exists
                score += 1

        # Save the score or handle it as needed
        return render(request, 'quiz_result.html', {'quiz': quiz, 'score': score})

    questions = quiz.questions.all()  # Access the questions through related_name
    return render(request, 'quiz.html', {'quiz': quiz, 'questions': questions})


@login_required
def profile(request):
    user_profile = request.user.userprofile
    courses_progress = user_profile.user.usercourseprogress_set.all()
    quiz_results = UserQuizResult.objects.filter(user=request.user)
    badges = UserBadge.objects.filter(user=request.user)
    return render(request, 'profile.html', {
        'user_profile': user_profile,
        'courses_progress': courses_progress,
        'quiz_results': quiz_results,
        'badges': badges
    })


def article_list(request):
    articles = Article.objects.all()
    if not request.user.is_authenticated or not request.user.userprofile.is_premium:
        articles = articles.filter(is_premium=False)
    return render(request, 'article_list.html', {'articles': articles})


@login_required
def article_detail(request, article_id):
    article = get_object_or_404(Article, id=article_id)
    if article.is_premium and not request.user.userprofile.is_premium:
        return redirect('subscription_required')
    return render(request, 'article_detail.html', {'article': article})


def course_list(request):
    courses = Course.objects.all()
    # Check if user is authenticated and has a UserProfile
    if not request.user.is_authenticated or not hasattr(request.user, 'userprofile'):
        courses = courses.filter(is_premium=False)
    else:
        # Check if user is premium
        if not request.user.userprofile.is_premium:
            courses = courses.filter(is_premium=False)
    return render(request, 'course_list.html', {'courses': courses})


def subscription_required(request):
    # Get the course title from the session
    course_title = request.session.get('course_title', None)

    if not course_title:
        # Handle case where course_title is missing
        return redirect('blog:course_list')  # or some error page

    # Retrieve the course using the title
    course = get_object_or_404(Course, title__iexact=course_title)

    # Render the explanation page with the course details
    return render(request, 'subscription_required.html', {'course': course, 'course_title': course_title})


# youtube_service.py

YOUTUBE_API_SERVICE_NAME = 'youtube'
YOUTUBE_API_VERSION = 'v3'


def search_educational_videos(query):
    try:
        youtube = build(
            YOUTUBE_API_SERVICE_NAME,
            YOUTUBE_API_VERSION,
            developerKey=settings.YOUTUBE_API_KEY
        )
        request = youtube.search().list(
            q=query + ' tutorial',  # Add additional keywords to narrow down the search
            part='snippet',
            type='video',
            maxResults=5,
            videoCategoryId='27',
            safeSearch='strict'
        )
        response = request.execute()
        return [item['id']['videoId'] for item in response.get('items', [])]

    except HttpError as e:
        error_reason = e.content.decode("utf-8")
        print(f"YouTube API Error: {error_reason}")
        # Handle the error as needed, e.g., log it or return an empty list
        return []


@login_required
@login_required
def course_detail(request, slug):
    # Replace hyphens with spaces to get the title from the slug
    course_title = slug.replace('-', ' ')

    # Retrieve the course using the title instead of the slug
    course = get_object_or_404(Course, title__iexact=course_title)

    try:
        user_profile = request.user.userprofile
    except UserProfile.DoesNotExist:
        return redirect('create_profile')

    # Check if the user needs a premium subscription to access the course
    if course.is_premium and not user_profile.subscription_status:
        request.session['course_title'] = course_title
        return redirect('blog:subscription_required')

    # Get or create the user's progress for this course
    progress, progress_created = UserCourseProgress.objects.get_or_create(
        user=request.user, course=course
    )

    # Initialize a flag to indicate enrollment
    is_enrolled = False

    # Fetch the first YouTube video based on the course title
    video_ids = search_educational_videos(course.title)

    # Check if a video was found
    first_video_id = video_ids[0] if video_ids else None

    if request.method == 'POST':
        if 'enroll' in request.POST:
            enrollment, created = UserCourseEnrollment.objects.get_or_create(
                user=request.user,
                course=course
            )
            if created:
                progress.progress = 0  # Set initial progress
                progress.save()
                is_enrolled = True  # Set the flag to True
        elif 'start_quiz' in request.POST:
            quiz_id = request.POST.get('quiz_id')
            if quiz_id:
                return redirect('blog:quiz', quiz_id=quiz_id)

    # Check if the user is already enrolled
    is_enrolled = UserCourseEnrollment.objects.filter(
        user=request.user, course=course).exists()

    # Retrieve the first quiz for the course (if available)
    quiz = Quiz.objects.filter(course=course).first()

    # Render the course detail template with enrollment status, progress, and video
    return render(request, 'course_detail.html', {
        'course': course,
        'progress': progress,
        'is_enrolled': is_enrolled,
        'quiz': quiz,
        'first_video_id': first_video_id,  # Pass the first video ID to the template
    })


def fetch_video_details(video_id):
    """Fetch video details from YouTube API."""
    api_key = settings.YOUTUBE_API_KEY
    url = f"https://www.googleapis.com/youtube/v3/videos?id={video_id}&key={api_key}&part=snippet,contentDetails"

    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        return None  # Handle error or return a default value


@login_required
def take_quiz(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    if quiz.is_premium and not request.user.userprofile.is_premium:
        return redirect('subscription_required')
    # Implement quiz-taking logic here
    return render(request, 'take_quiz.html', {'quiz': quiz})


@login_required
def forum_list(request):
    threads = ForumThread.objects.annotate(comment_count=Count('forumcomment'))
    return render(request, 'forum_list.html', {'threads': threads})


@login_required
def forum_thread(request, thread_id):
    thread = get_object_or_404(ForumThread, id=thread_id)
    comments = thread.forumcomment_set.all()
    if request.method == 'POST':
        form = ForumCommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.thread = thread
            comment.author = request.user
            comment.save()
            return redirect('forum_thread', thread_id=thread.id)
    else:
        form = ForumCommentForm()
    return render(request, 'forum_thread.html', {'thread': thread, 'comments': comments, 'form': form})


@login_required
def create_thread(request):
    if request.method == 'POST':
        form = ForumThreadForm(request.POST)
        if form.is_valid():
            thread = form.save(commit=False)
            thread.author = request.user
            thread.save()
            return redirect('forum_thread', thread_id=thread.id)
    else:
        form = ForumThreadForm()
    return render(request, 'create_thread.html', {'form': form})


def leaderboard(request):
    top_users = UserProfile.objects.annotate(
        avg_score=Avg('user__userquizresult__score'),
        course_count=Count('user__usercourseprogress', filter=models.Q(
            user__usercourseprogress__progress=100))
    ).order_by('-avg_score', '-course_count')[:10]
    return render(request, 'leaderboard.html', {'top_users': top_users})


@login_required
def subscription_management(request):
    # Implement subscription management logic here (e.g., using Stripe)
    return render(request, 'subscription_management.html')
