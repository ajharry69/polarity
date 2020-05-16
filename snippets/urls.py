from django.urls import path, include
from rest_framework import routers

from snippets import views

snippet_router = routers.DefaultRouter()
snippet_router.register(r'snippets', views.SnippetViewSet)
snippet_router.register(r'users', views.UserViewSet)

urlpatterns = [
    path('', include(snippet_router.urls))
]
