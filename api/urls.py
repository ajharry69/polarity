from django.urls import include, path

from quickstart.urls import quickstart_router

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    path('quickstart/', include(quickstart_router.urls)),
    path('snippets/', include('snippets.urls')),
    path('admin-auth/', include('rest_framework.urls', namespace='rest_framework')),  # must be at the end!
]
