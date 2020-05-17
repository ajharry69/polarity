from django.urls import path, include
from rest_framework import routers

from snippets import views

router = routers.DefaultRouter()
router.register(r'users', views.UserViewSet)
router.register(r'snippets', views.SnippetViewSet)

app_name = 'snippets'
urlpatterns = [
    path('', include(router.urls))
]
