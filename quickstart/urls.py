from rest_framework import routers

from quickstart import views

quickstart_router = routers.DefaultRouter()
quickstart_router.register(r'users', views.UserViewSet)
quickstart_router.register(r'groups', views.GroupViewSet)
