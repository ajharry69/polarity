from django.urls import include, path

from api import views

# Quickstart & Snippets APIs are wired up using automatic URL routing.
# Additionally, we include login URLs for the browsable API.

# app_name = 'api' # prevents `admin-auth/` from showing login & logout buttons
urlpatterns = [
    path('', views.api_root, name='index'),
    path('quickstart/', include('quickstart.urls', namespace='quickstart')),
    path('snippets/', include('snippets.urls', namespace='snippets')),
    path('xauth/', include('xauth.urls', namespace='xauth')),
    path('admin-auth/', include('rest_framework.urls', namespace='rest_framework')),  # should be at the end!
]
