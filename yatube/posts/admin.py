"""Admin site settings of the 'Posts' application."""

from django.contrib import admin

from .models import Comment, Follow, Group, Post


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    """Table settings for resource 'Post' on the admin site."""

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


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    """Table settings for resource 'Follow' on the admin site."""

    list_display = (
        "pk",
        "user",
        "author",
    )
    search_fields = ("user", "author")
    list_filter = ("user", "author")


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    """Table settings for resource 'Group' on the admin site."""

    list_display = (
        "pk",
        "title",
        "slug",
        "description",
    )
    prepopulated_fields = {"slug": ("title",)}


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    """Table settings for resource 'Comment' on the admin site."""

    list_display = (
        "pk",
        "text",
        "author",
        "post",
    )
    list_editable = ("author",)
