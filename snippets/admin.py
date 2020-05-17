from django.contrib import admin

from .models import *


class SnippetAdmin(admin.ModelAdmin):
    list_display = ['title', 'owner', 'language', 'style', 'created', 'linenos', ]
    list_filter = ['owner', 'linenos', 'language', 'style', ]
    search_fields = ['title']


admin.site.register(Snippet, SnippetAdmin)
