from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register_view, name='register'),
    path('login/', views.user_login, name='login'),
    path('journalist/dashboard/', views.journalist_dashboard, name='journalist_dashboard'),
    path('editor/dashboard/', views.editor_dashboard, name='editor_dashboard'),
    path('editor/review/', views.review_article, name='review_article'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('add_article/', views.add_article, name='add_article'),
    path('add_article_page2/', views.add_article_page2, name='add_article_page2'),
     path('my-articles/', views.my_articles_view, name='my_articles'),
    path('published-article/', views.published_articles_view, name='published_article'),  # Add this line
    path('rejected-articles/', views.rejected_articles_view, name='rejected_articles'),
    path('submit_success/', views.submit_success, name='submit_success'),
    path('article/<int:article_id>/', views.view_article, name='view_article'),
    path('article/edit/<int:id>/', views.edit_article, name='edit_article'),
    path('article/delete/<int:id>/', views.delete_article, name='delete_article'),
    path('edit-profile/', views.edit_profile, name='edit_profile'),
    path('logout/', views.user_logout, name='logout'),
    path('update-article-status/<int:id>/', views.update_article_status, name='update_article_status'),
    path('manage-users/', views.manage_users, name='manage_users'),
    path('edit-user/<int:user_id>/', views.edit_user, name='edit_user'),
    path('delete-user/<int:user_id>/', views.delete_user, name='delete_user'),  # Add delete user URL
    path('manage-articles/', views.manage_articles, name='manage_articles'),
    path('create-user/', views.create_user, name='create_user'),
    
    path('password_reset/', auth_views.PasswordResetView.as_view(template_name='password_reset_form.html'), name='password_reset'),     
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='password_reset_done.html'), name='password_reset_done'),     
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='password_reset_confirm.html'), name='password_reset_confirm'),     
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='password_reset_complete.html'), name='password_reset_complete'),
    path('validate-username/', views.validate_username, name='validate-username'),
    path('validate-email/', views.validate_email, name='validate-email'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)