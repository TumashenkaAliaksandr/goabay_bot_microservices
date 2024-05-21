from django.contrib import admin

from bot_app import models


class WordAdmin(admin.ModelAdmin):
    list_display = ['pk', 'word_gender', 'word']
    list_edit = ['word_gender', 'word']

admin.site.register(models.Words, WordAdmin)