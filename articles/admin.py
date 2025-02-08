from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Profile, Article

# Profile Admin Configuration
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role')
    search_fields = ('user__username', 'role')

admin.site.register(Profile, ProfileAdmin)

# Article Admin Configuration
class ArticleAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'category', 'publish_date', 'is_published')
    search_fields = ('title', 'author__username', 'category')
    list_filter = ('category', 'is_published', 'tags')
    ordering = ('-created_at',)

admin.site.register(Article, ArticleAdmin)
