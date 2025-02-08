from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth import login
from articles.models import *
from .forms import ArticlePage1Form, ArticlePage2Form, CustomUserCreationForm
from .forms import ArticleForm
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import logout
from .forms import UserForm, ProfileForm
from django.urls import reverse_lazy
from django.core.mail import send_mail
from django.contrib.auth.views import PasswordResetView
from .models import Article, Profile
from django.core.paginator import Paginator



def home(request):
    # Fetch all articles with 'Approved' status
    published_articles = Article.objects.filter(status='Approved')
    context = {
        'published_articles': published_articles
    }
    return render(request, 'articles/home.html', context)

def published_article(request, article_id):
    article = get_object_or_404(Article, id=article_id, status='Approved')
    context = {
        'article': article
    }
    return render(request, 'articles/published_article.html', context)


def register_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        rol = request.POST.get('role')  # Get the role from the form data
        if form.is_valid():
            user = form.save()
            if rol == 'admin':
                user.is_superuser = True
                user.is_staff = True  # This also grants access to the admin panel
                user.save()
            print(request.user)
            if request.user.is_superuser:
                    return redirect('admin_dashboard') 
            # Check if Profile already exists for the user
            
            if not Profile.objects.filter(user=user).exists():
                Profile.objects.create(user=user, role=rol)  # Create Profile instance
            login(request, user)  # Log the user in immediately
            messages.success(request, 'Registration successful. You can now log in.')
            return redirect('login')
    else:
        form = CustomUserCreationForm()
    return render(request, 'articles/register.html', {'form': form})


def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username', '')
        password = request.POST.get('password', '')

        user = authenticate(request, username=username, password=password)

        if user is not None:
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
            # Custom error messages based on username and password
            if not username and not password:
                messages.error(request, 'Invalid username and password.')
            elif not username:
                messages.error(request, 'Invalid username.')
            elif not password:
                messages.error(request, 'Invalid password.')
            else:
                messages.error(request, 'Invalid username and password.')

    return render(request, 'articles/login.html')

def user_logout(request):
    logout(request)
    return render(request, 'articles/logout.html')

@login_required
def journalist_dashboard(request):
    # Fetch articles for the logged-in journalist
    articles = Article.objects.filter(author=request.user)

    # Filter articles based on status
    my_articles = articles.filter(status='Submitted')
    published_articles = articles.filter(status='Approved')
    rejected_articles = articles.filter(status='Rejected')

    # Count the number of articles in each category
    my_articles_count = my_articles.count()
    published_articles_count = published_articles.count()
    rejected_articles_count = rejected_articles.count()

    # Pass the filtered articles and counts to the template
    context = {
        'my_articles_count': my_articles_count,
        'published_articles_count': published_articles_count,
        'rejected_articles_count': rejected_articles_count,
        'my_articles': my_articles,  # For 'My Articles' section
        'published_articles': published_articles,  # For 'Published Articles' section
        'rejected_articles': rejected_articles,  # For 'Rejected Articles' section
    }

    return render(request, 'articles/journalist_dashboard.html', context)

@login_required
def my_articles_view(request):
    # Fetch submitted articles for the logged-in journalist
    my_articles = Article.objects.filter(author=request.user, status='Submitted')
    
    # Implement pagination
    paginator = Paginator(my_articles, 5)  # Show 5 articles per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,  # Update context to pass the paginated object
    }
    
    return render(request, 'articles/my_articles.html', context)

@login_required
def published_articles_view(request):
    # Fetch published articles for the logged-in journalist with status 'Approved'
    published_article = Article.objects.filter(author=request.user, status='Approved')
    
    # Set up pagination
    paginator = Paginator(published_article, 5)  # Show 5 articles per page
    page_number = request.GET.get('page')
    articles_page = paginator.get_page(page_number)

    context = {
        'published_article': articles_page,
    }
    
    return render(request, 'articles/published_article.html', context)

@login_required
def rejected_articles_view(request):
    # Fetch rejected articles for the logged-in journalist
    rejected_articles = Article.objects.filter(author=request.user, status='Rejected')
    
    context = {
        'rejected_articles': rejected_articles,
    }
    
    return render(request, 'articles/rejected_articles.html', context)

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
                return redirect('add_article')  # Redirect if page1 data is not in the session

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
        page2_form = ArticlePage2Form()  # Initialize form if GET request

    return render(request, 'articles/add_article_page2.html', {
        'page2_form': page2_form,
    })
    
@login_required
def submit_success(request):
    return render(request, 'articles/submit.html')

@login_required
def view_article(request, article_id):  # Ensure this matches the URL pattern
    article = get_object_or_404(Article, id=article_id)  # This will raise a 404 if not found
    return render(request, 'articles/view_article.html', {'article': article})

def edit_article(request, id):
    article = get_object_or_404(Article, id=id)
    redirect_url = request.POST.get('from', 'journalist')  # Default to 'journalist' if not specified

    if request.method == 'POST':
        form = ArticleForm(request.POST, request.FILES, instance=article)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your article has been updated successfully.')
            if redirect_url == 'editor':
                return redirect('editor_dashboard')  # Adjust to your actual editor dashboard URL
            else:
                return redirect('journalist_dashboard')  # Default to journalist dashboard
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
            elif user_profile.role == 'editor':
                return redirect('editor_dashboard')  # Redirect to editor's dashboard

        elif 'cancel' in request.POST:
            # Cancel delete action
            messages.info(request, 'Article deletion was canceled.')
            
            # Redirect based on user role
            if user_profile.role == 'journalist':
                return redirect('journalist_dashboard')
            elif user_profile.role == 'admin':
                return redirect('admin_dashboard')
            elif user_profile.role == 'editor':
                return redirect('editor_dashboard')  # Redirect to editor's dashboard

    return render(request, 'articles/delete_article.html', {'article': article})

@login_required
def edit_profile(request):
    user = request.user
    profile = user.profile  # Assuming you have a Profile model linked to User
    
    if request.method == 'POST':
        user.username = request.POST['username']
        user.email = request.POST['email']
        user.first_name = request.POST.get('first_name', '')
        user.last_name = request.POST.get('last_name', '')
        user.save()

        old_password = request.POST.get('old_password')
        new_password1 = request.POST.get('new_password1')
        new_password2 = request.POST.get('new_password2')

        if old_password and new_password1 and new_password2:
            if new_password1 == new_password2:
                if user.check_password(old_password):
                    user.set_password(new_password1)
                    user.save()
                    update_session_auth_hash(request, user)  # Keep the user logged in after password change
                    messages.success(request, 'Your password has been updated successfully.')
                else:
                    messages.error(request, 'Old password is incorrect.')
            else:
                messages.error(request, 'New passwords do not match.')

        messages.success(request, 'Your profile has been updated successfully.')
        
        # Redirect based on the user's role
        if profile.role == 'journalist':
            return redirect('journalist_dashboard')
        elif profile.role == 'editor':
            return redirect('editor_dashboard')
        elif profile.role == 'admin':
            return redirect('admin_dashboard')

    return render(request, 'articles/edit_profile.html')

@login_required
def editor_dashboard(request):
    # Fetch articles that are pending for review
    pending_articles = Article.objects.filter(status='Pending')
    
    # Fetch articles that are either published or rejected
    published_rejected_articles = Article.objects.filter(status__in=['Approved', 'Rejected'])

    context = {
        'pending_articles': pending_articles,
        'published_rejected_articles': published_rejected_articles,
    }

    return render(request, 'articles/editor_dashboard.html', context)


@login_required
def review_article(request):
    # Retrieve all articles and set up pagination
    article_list = Article.objects.all()
    paginator = Paginator(article_list, 5)  # Show 10 articles per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    if request.method == 'POST':
        article_id = request.POST.get('article_id')  # Get the article ID from the POST data
        status = request.POST.get('status')
        
        # Check if the status is valid and update the article's status
        if status in ['Submitted', 'Approved', 'Rejected'] and article_id:
            article = get_object_or_404(Article, id=article_id)
            article.status = status
            article.save()
            return redirect('review_article')  # Redirect back to the review articles page

    return render(request, 'articles/review_article.html', {'page_obj': page_obj})


def update_article_status(request,id):
    article = get_object_or_404(Article, id=id)

    if request.method == 'POST':
        status = request.POST.get('status')
        if status in ['Submitted', 'Approved', 'Rejected']:
            article.status = status
            article.save()
        return redirect('review_article')

    return HttpResponse(status=405)  # Method not allowed


def admin_dashboard(request):
    if not request.user.is_superuser:
        return redirect('home')  # Redirect if not an admin
    
    users = User.objects.all()
    articles = Article.objects.all()
    return render(request, 'articles/admin_dashboard.html', {'users': users, 'articles': articles})

def manage_users(request):
    # Fetch users based on role
    journalists = User.objects.filter(profile__role='journalist')
    editors = User.objects.filter(profile__role='editor')
    admins = User.objects.filter(profile__role='admin')

    context = {
        'journalists': journalists,
        'editors': editors,
        'admins': admins,
    }

    return render(request, 'articles/manage_users.html', context)

@login_required
def create_user(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        
        if form.is_valid():
            print("5024224")
            form.save()
            
            messages.success(request, 'User created successfully.')
            return redirect('manage_users')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = CustomUserCreationForm()

    return render(request, 'articles/create_users.html', {'form': form})

def edit_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    
    if request.method == 'POST':
        user_form = UserForm(request.POST, instance=user)
        profile_form = ProfileForm(request.POST, instance=user.profile)
        password = request.POST.get('password', '')

        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save(commit=False)

            # Update password only if a new one is provided
            if password:
                user.set_password(password)
            
            user.save()
            profile_form.save()
            return redirect('manage_users')
    else:
        user_form = UserForm(instance=user)
        profile_form = ProfileForm(instance=user.profile)
    
    return render(request, 'articles/edit_user.html', {
        'user_form': user_form, 
        'profile_form': profile_form, 
        'user': user
    })

def delete_user(request, user_id):
    user = get_object_or_404(User, id=user_id)

    if request.method == 'POST':
        user.delete()
        return redirect('manage_users')  # Redirect to the manage users page after deletion
    
    return render(request, 'articles/delete_user.html', {'user': user})

def manage_articles(request):
    all_articles = Article.objects.all()
    published_articles = Article.objects.filter(status='Published')
    rejected_articles = Article.objects.filter(status='Rejected')

    context = {
        'all_articles': all_articles,
        'published_articles': published_articles,
        'rejected_articles': rejected_articles,
    }
    return render(request, 'articles/manage_article.html', context)

class CustomPasswordResetView(PasswordResetView):
    template_name = '  password_reset_form.html'
    email_template_name = 'password_reset_email.html'
    success_url = reverse_lazy('password_reset_done')
    subject_template_name = 'password_reset_subject.txt'

    # Customizing the email sending logic
    def form_valid(self, form):
        email = form.cleaned_data['email']
        # Check if the email exists in your system
        send_mail(
            'Password Reset Request',
            'You requested a password reset. Click the link below to reset your password.',
            settings.DEFAULT_FROM_EMAIL,
            [email],
            fail_silently=False,
        )
        return super().form_valid(form)
    
    
from django.http import JsonResponse
from django.contrib.auth import get_user_model

User = get_user_model()

# View to validate if the username is unique
def validate_username(request):
    username = request.GET.get('username', None)
    data = {
        'is_unique': not User.objects.filter(username=username).exists()
    }
    return JsonResponse(data)

# View to validate if the email is unique
def validate_email(request):
    email = request.GET.get('email', None)
    data = {
        'is_unique': not User.objects.filter(email=email).exists()
    }
    return JsonResponse(data)