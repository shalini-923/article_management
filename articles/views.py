from tokenize import Comment
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth import login
from articles.models import *
from django.urls import reverse
from .forms import ArticlePage1Form, ArticlePage2Form, CustomUserCreationForm
from .forms import ArticleForm
from django.contrib.auth.models import User
from .forms import UserForm 
from django.contrib.auth import update_session_auth_hash
from .forms import EditProfileForm, PasswordChangeForm 
from django.contrib.auth import logout
from .models import Article


def home(request):
    return render(request, 'articles/home.html')


def register_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        role = request.POST.get('role')  # Get the role from the form data
        if form.is_valid():
            user = form.save()
            # Check if Profile already exists for the user
            if not Profile.objects.filter(user=user).exists():
                Profile.objects.create(user=user, role=role)  # Create Profile instance
            login(request, user)  # Log the user in immediately
            messages.success(request, 'Registration successful. You can now log in.')
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'articles/register.html', {'form': form})


def user_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            auth_login(request, user)
            # Ensure Profile exists
            profile, created = Profile.objects.get_or_create(user=user)
            role = profile.role  # Access the role from the profile
            # Redirect based on user role
            if role == 'journalist':
                return redirect('journalist_dashboard')
            elif role == 'editor':
                return redirect('editor_dashboard')
            elif role == 'admin':
                return redirect('admin_dashboard')
            else:
                messages.error(request, 'User role is not defined.')
                return redirect('login')
        else:
            messages.error(request, 'Invalid username or password.')
    else:
        form = AuthenticationForm()
    return render(request, 'articles/login.html', {'form': form})

@login_required
def journalist_dashboard(request):
    # List all articles created by the journalist
    articles = Article.objects.filter(author=request.user)
    return render(request, 'articles/journalist_dashboard.html', {'articles': articles})

@login_required
def add_article(request):
    if request.method == 'POST':
        if 'page1' in request.POST:
            page1_form = ArticlePage1Form(request.POST)
            if page1_form.is_valid():
                request.session['page1_data'] = page1_form.cleaned_data
                return redirect('add_article_page2')
        elif 'page2' in request.POST:
            if 'page1_data' not in request.session:
                return redirect ('add_article')
           
            page2_form = ArticlePage2Form(request.POST, request.FILES)
            if page2_form.is_valid():
                page1_data = request.session.get('page1_data', {})
                article_data = {**page1_data, **page2_form.cleaned_data}
                # Save article data to the database
                article = Article(
                    title=article_data['title'],
                    subtitle=article_data['subtitle'],
                    content=article_data['content'],
                    author=request.user,
                    email=article_data['email'],
                    image=article_data.get('image'),
                    tags=','.join(article_data.get('tags', [])),
                    category=article_data['category'],
                    publish_date=article_data['publish_date'],
                )
                article.save()
                del request.session['page1_data']  # Clean up session data
                return redirect('submit_success')  # Redirect to the submission success page
    else:
        page1_form = ArticlePage1Form()
        page2_form = ArticlePage2Form()

    return render(request, 'articles/add_article.html', {
        'page1_form': page1_form,
        'page2_form': page2_form,
    })

@login_required
def add_article_page2(request):
    if 'page1_data' not in request.session:
        return redirect('add_article')  # Redirect if page1 data is not in the session

    if request.method == 'POST':
        page2_form = ArticlePage2Form(request.POST, request.FILES)
        if page2_form.is_valid():
            page1_data = request.session.get('page1_data', {})
            article_data = {**page1_data, **page2_form.cleaned_data}
        
            # Save article data to the database
            article = Article(
                title=article_data['title'],
                subtitle=article_data['subtitle'],
                content=article_data['content'],
                author=request.user,
                email=article_data['email'],
                image=article_data.get('image'),
                tags=','.join(article_data.get('tags', [])),
                category=article_data['category'],
                publish_date=article_data['publish_date'],
            )
            article.save()
            del request.session['page1_data']  # Clean up session data
            return redirect('submit_success')  # Redirect to the submission success page
        
    else:
        page2_form = ArticlePage2Form()

    return render(request, 'articles/add_article_page2.html', {
        'page2_form': page2_form,
    })

@login_required
def submit_success(request):
    return render(request, 'articles/submit.html')

@login_required
def view_article(request, id):
    # Retrieve the specific article by ID
    article = get_object_or_404(Article, id=id, author=request.user)  # Ensure the article belongs to the logged-in user
    return render(request, 'articles/view_article.html', {'article': article})

# def edit_article(request, id):
#     article = get_object_or_404(Article, id=id)
#     if request.method == 'POST':
#         form = ArticleForm(request.POST, instance=article)
#         if form.is_valid():
#             form.save()
#             return redirect('some_view_name')  # Replace with your redirect target
#     else:
#         form = ArticleForm(instance=article)
#     return render(request, 'edit_article.html', {'form': form})


@login_required
def edit_article(request, id):
     article = get_object_or_404(Article, id=id)
     if request.method == 'POST':
         form = ArticleForm(request.POST, request.FILES, instance=article)
         if form.is_valid():
             form.save()
             messages.success(request, 'Article updated successfully!')
             return redirect('journalist_dashboard', article_id=article.id)
     else:
         form = ArticleForm(instance=article)
     return render(request, 'articles/edit_article.html', {'form': form})

@login_required
def delete_article(request, id):
    article = get_object_or_404(Article, id=id)
    user_profile = request.user.profile

    if request.method == 'POST':
        if 'confirm' in request.POST:
            # Confirm delete action
            article.delete()
            messages.success(request, 'Your article has been deleted successfully.')

            # Redirect based on user role
            if user_profile.role == 'journalist':
                return redirect('journalist_dashboard')
            elif user_profile.role == 'admin':
                return redirect('admin_dashboard')

        elif 'cancel' in request.POST:
            # Cancel delete action
            messages.info(request, 'Article deletion was canceled.')
            
            # Redirect based on user role
            if user_profile.role == 'journalist':
                return redirect('journalist_dashboard')
            elif user_profile.role == 'admin':
                return redirect('admin_dashboard')

    return render(request, 'articles/delete_article.html', {'article': article})

@login_required
def editor_dashboard(request):
    return render(request, 'articles/editor_dashboard.html')

@login_required
def admin_dashboard(request):
    return render(request, 'articles/admin_dashboard.html')

def review_articles(request):
    articles = Article.objects.all()  # Fetch all articles
    return render(request, 'articles/review_articles.html', {'articles': articles})

def publish_article(request, article_id):
    article = get_object_or_404(Article, id=article_id)
    if article.status != 'published' and article.status != 'rejected':  # Only publish if not already processed
        article.status = 'published'
        article.save()
        messages.success(request, f'Article "{article.title}" has been published.')
    return redirect('review_articles')

def reject_article(request, article_id):
    article = get_object_or_404(Article, id=article_id)
    if article.status != 'rejected' and article.status != 'published':  # Only reject if not already processed
        article.status = 'rejected'
        article.save()
        messages.success(request, f'Article "{article.title}" has been rejected.')
    return redirect('review_articles')

def article_detail(request, article_id):
    article = get_object_or_404(Article, id=article_id)
    comments = Comment.objects.filter(article=article).order_by('-created_at')  # Fetch comments for this article

    # Handle comment form submission
    if request.method == 'POST':
        comment_form = comment_form(request.POST)
        if comment_form.is_valid():
            new_comment = comment_form.save(commit=False)
            new_comment.article = article
            new_comment.author = request.user  # assuming you have authentication
            new_comment.save()
            return HttpResponseRedirect(reverse('article_detail', args=[article_id]))
    else:
        comment_form = comment_form()

    context = {
        'article': article,
        'comments': comments,
        'comment_form': comment_form,
    }
    return render(request, 'article_detail.html', context)


def manage_articles(request):
    articles = Article.objects.all()  # Fetch all articles from the database
    return render(request, 'articles/manage_articles.html', {'articles': articles})


def manage_users(request):
    users = User.objects.all()  # Fetch all users from the database
    return render(request, 'articles/manage_users.html', {'users': users})

# Edit a user
def edit_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    if request.method == 'POST':
        form = UserForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return redirect('manage_users')
    else:
        form = UserForm(instance=user)
    return render(request, 'articles/edit_user.html', {'form': form})

# Delete a user
def delete_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    user.delete()
    return redirect('manage_users')

# Edit profile view
@login_required
def edit_profile(request):
    if request.method == 'POST':
        profile_form = EditProfileForm(request.POST, instance=request.user)
        password_form = PasswordChangeForm(request.user, request.POST)

        if profile_form.is_valid():
            profile_form.save()
            return redirect('edit_profile')

        if password_form.is_valid():
            user = password_form.save()
            update_session_auth_hash(request, user)  # Update session to keep the user logged in
            return redirect('edit_profile')
    else:
        profile_form = EditProfileForm(instance=request.user)
        password_form = PasswordChangeForm(request.user)

    return render(request, 'articles/edit_profile.html', {
        'profile_form': profile_form,
        'password_form': password_form
    })

def custom_logout(request):
    logout(request)
    return redirect('login')