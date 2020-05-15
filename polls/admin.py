from django.contrib import admin

from .models import *


class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 3  # provide enough fields for 3 choices


class QuestionAdmin(admin.ModelAdmin):
    # field names to display, as columns, on the change list page for the object
    list_display = ('question_text', 'pub_date', 'was_published_recently',)
    fieldsets = [
        (None, {'fields': ['question_text']}),
        ('Date Information', {
            'fields': ['pub_date'],
            'classes': ['collapse'],
        })
    ]
    list_filter = ['pub_date']
    search_fields = ['question_text']
    inlines = [ChoiceInline]


admin.site.register(Question, QuestionAdmin)
admin.site.register(Choice)
