from django.contrib import admin
from .models import Post, Group


class PostAdmin(admin.ModelAdmin):
    list_display = ('text', 'pub_date', 'author', 'group')
    list_filter = ('text', 'pub_date', 'author', 'group')
    search_fields = ('text', 'pub_date', 'author', 'group')
    empty_value_display = '-пусто-'


class GroupAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug', 'description')
    list_filter = ('title', 'slug')
    empty_value_display = '-пусто-'
    prepopulated_fields = {"slug": ("title",)}

admin.site.register(Post, PostAdmin)
admin.site.register(Group, GroupAdmin)