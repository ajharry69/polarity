from django.urls import path, include
from rest_framework import routers

from quickstart import views

router = routers.DefaultRouter()
router.register(r'users', views.UserViewSet)
router.register(r'groups', views.GroupViewSet)

app_name = 'quickstart'
urlpatterns = [
    path('', include(router.urls))
]
