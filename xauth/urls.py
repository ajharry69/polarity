from django.urls import path

from xauth import views

app_name = 'xauth'
urlpatterns = [
    path('sign-in/', view=views.SignInView.as_view(), name='sign-in'),
    path('sign-up/', view=views.SignUpView.as_view(), name='sign-up'),
    path('profile/<int:pk>/', view=views.ProfileView.as_view(), name='profile'),
    path('verify/', view=views.VerificationView.as_view(), name='verify'),
    path('password-reset/', view=views.PasswordResetView.as_view(), name='password-reset'),
]
