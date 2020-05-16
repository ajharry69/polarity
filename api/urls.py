from django.urls import include, path

# Quickstart & Snippets APIs are wired up using automatic URL routing.
# Additionally, we include login URLs for the browsable API.

# app_name = 'api' # prevents `admin-auth/` from showing login & logout buttons
urlpatterns = [
    path('quickstart/', include('quickstart.urls')),
    path('snippets/', include('snippets.urls')),
    # path('', views.api_root, name='index'),
    path('admin-auth/', include('rest_framework.urls', namespace='rest_framework')),  # should be at the end!
]
