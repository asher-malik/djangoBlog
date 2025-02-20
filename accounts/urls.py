from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.login_user, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('activate/<token>/', views.activate, name='activate'),
    path('password_reset_request/', views.password_reset_request, name='password_reset_request'),
    path('reset_password/<token>/', views.reset_password, name='reset_password'),
    path('view_account/', views.view_account, name='view_account'),
    path('validate_username/', views.validate_username, name='validate_username'),
    path('validate_user_password/', views.validate_user_password, name='validate_user_password'),
    path('delete_account/', views.delete_account, name='delete_account'),
]
