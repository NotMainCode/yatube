"""Admin zone settings of the 'Posts' application."""

from django.contrib import admin

from .models import Comment, Follow, Group, Post


class PostAdmin(admin.ModelAdmin):
    """Table settings for posts of users in the admin-zone."""

    list_display = (
        "pk",
        "text",
        "pub_date",
        "author",
        "group",
    )
    list_editable = ("group",)
    search_fields = ("text",)
    list_filter = ("pub_date",)
    empty_value_display = "-пусто-"


class FollowAdmin(admin.ModelAdmin):
    """Table settings for user subscriptions in the admin area."""

    list_display = (
        "pk",
        "user",
        "author",
    )
    search_fields = ("user", "author")
    list_filter = ("user", "author")


admin.site.register(Post, PostAdmin)
admin.site.register(Group)
admin.site.register(Follow, FollowAdmin)
admin.site.register(Comment)
