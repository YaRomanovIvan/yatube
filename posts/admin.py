from django.contrib import admin
from .models import Post, Group, Comment, Follow


class PostAdmin(admin.ModelAdmin):
    list_display = ("text", "pub_date", "author", "group")
    list_filter = ("text", "pub_date", "author", "group")
    search_fields = ("text", "pub_date", "author", "group")
    empty_value_display = "-пусто-"


class GroupAdmin(admin.ModelAdmin):
    list_display = ("title", "slug", "description")
    list_filter = ("title", "slug")
    empty_value_display = "-пусто-"
    prepopulated_fields = {"slug": ("title",)}


class CommentAdmin(admin.ModelAdmin):
    list_display = ("post", "author", "text", "created")
    list_filter = ("post", "author", "text", "created")
    search_fields = ("post", "author", "text", "created")
    empty_value_display = "-пусто-"


class FollowAdmin(admin.ModelAdmin):
    list_display = ("user", "author")
    list_filter = ("user", "author")
    search_fields = ("user", "author")


admin.site.register(Post, PostAdmin)
admin.site.register(Group, GroupAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(Follow, FollowAdmin)