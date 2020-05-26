from django.urls import path, include
from rest_framework import routers

from xauth import views

router = routers.DefaultRouter()
router.register(r'security-question', views.SecurityQuestionView)

app_name = 'xauth'
urlpatterns = [
    path('', include(router.urls)),
    path('sign-in/', view=views.SignInView.as_view(), name='sign-in'),
    path('sign-up/', view=views.SignUpView.as_view(), name='sign-up'),
    path('profile/<int:pk>/', view=views.ProfileView.as_view(), name='profile'),
    path('verify/', view=views.VerificationView.as_view(), name='verify'),
    path('password-reset/', view=views.PasswordResetView.as_view(), name='password-reset'),
]
