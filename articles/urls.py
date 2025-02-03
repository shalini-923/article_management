from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register_view, name='register'),
    path('login/', views.user_login, name='login'),
    path('journalist/dashboard/', views.journalist_dashboard, name='journalist_dashboard'),
    path('editor/dashboard/', views.editor_dashboard, name='editor_dashboard'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('article/add/', views.add_article, name='add_article'),
    path('article/add/page2/', views.add_article_page2, name='add_article_page2'),
    path('submit_success/', views.submit_success, name='submit_success'),
    path('article/<int:id>/', views.view_article, name='view_article'),
    path('articles/<int:id>/edit/', views.edit_article, name='edit_article'),
    path('articles/<int:id>/delete/', views.delete_article, name='delete_article'),
    path('articles/manage/', views.manage_articles, name='manage_articles'),
    path('users/manage/', views.manage_users, name='manage_users'),
    path('edit/profile/', views.edit_profile, name='edit_profile'),
    path('logout/', views.custom_logout, name='logout'),
    path('review_articles/', views.review_articles, name='review_articles'),
    path('article/<int:article_id>/publish/', views.publish_article, name='publish_article'),
    path('article/<int:article_id>/reject/', views.reject_article, name='reject_article'),

        path('article/<int:article_id>/', views.article_detail, name='article_detail'),  
    path('users/edit/<int:user_id>/', views.edit_user, name='edit_user'),
    path('users/delete/<int:user_id>/', views.delete_user, name='delete_user'),
 ]