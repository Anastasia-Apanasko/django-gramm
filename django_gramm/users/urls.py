from django.urls import path, reverse_lazy
from django.contrib.auth.views import LogoutView, LoginView
from django.contrib.auth import views as auth_views
from . import views

app_name = 'users'

urlpatterns = [
    path("login/", LoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path('signup/', views.signup, name='signup'),
    path('activate/<uidb64>/<token>/', views.activate, name='activate'),
    path('edit/', views.edit, name='edit'),

    path('<str:username>/follow/', views.follow, name='follow'),
    path('<str:username>/unfollow/', views.unfollow, name='unfollow'),
    path('<str:username>/followers/', views.followers_list, name='followers_list'),
    path('<str:username>/following/', views.following_list, name='following_list'),
    path('<str:username>/follow-ajax/', views.follow_ajax, name='follow_ajax'),
    path('<str:username>/unfollow-ajax/', views.unfollow_ajax, name='unfollow_ajax'),

    path('password-change/',
         auth_views.PasswordChangeView.as_view(
             template_name='users/password_change_form.html',
             success_url=reverse_lazy('users:password_change_done')
         ),
         name='password_change'),
    path('password-change/done/',
         auth_views.PasswordChangeDoneView.as_view(
             template_name='users/password_change_done.html'),
         name='password_change_done'),

    path('password-reset/',
         auth_views.PasswordResetView.as_view(
             template_name='users/password_reset_form.html',
             email_template_name='users/password_reset_email.html',
             success_url=reverse_lazy('users:password_reset_done')
         ),
         name='password_reset'),

    path('password-reset/done/',
         auth_views.PasswordResetDoneView.as_view(
             template_name='users/password_reset_done.html'),
         name='password_reset_done'),

    path('password-reset/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(
             template_name='users/password_reset_confirm.html',
             success_url=reverse_lazy('users:password_reset_complete')),
         name='password_reset_confirm'),

    path('password-reset/complete/',
         auth_views.PasswordResetCompleteView.as_view(
             template_name='users/password_reset_complete.html'),
         name='password_reset_complete'),

    path('<str:username>/', views.profile_view, name='profile'),
]
