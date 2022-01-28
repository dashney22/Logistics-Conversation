from django.contrib import admin
from .models import Tag, User, Post, Comment

# Register your models here.
class PostAdmin(admin.ModelAdmin):
    list_filter =("author","tags", "date")
    list_display =("title", "date", "author")
    prepopulated_fields = {"slug" : ("title",)}

admin.site.register(Tag)
admin.site.register(Post, PostAdmin)
admin.site.register(User)
admin.site.register(Comment)