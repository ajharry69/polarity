from django.urls import include, path

# from rest_framework.urlpatterns import format_suffix_patterns

# Quickstart & Snippets APIs are wired up using automatic URL routing.
# Additionally, we include login URLs for the browsable API.

# app_name = 'api' # prevents `admin-auth/` from showing login & logout buttons
urlpatterns = [
    # path('', views.api_root, name='index'),
    path('quickstart/', include('quickstart.urls', namespace='quickstart')),
    path('snippets/', include('snippets.urls', namespace='snippets')),
    path('admin-auth/', include('rest_framework.urls', namespace='rest_framework')),  # should be at the end!
]
# urlpatterns = format_suffix_patterns(urlpatterns)
