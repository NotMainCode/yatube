"""Database settings of the 'Posts' application."""

from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Group(models.Model):
    """Table settings for groups of user posts."""

    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    description = models.TextField()

    def __str__(self):
        return self.title


class Post(models.Model):
    """Table settings for user posts."""

    text = models.TextField()
    pub_date = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="posts",
    )
    group = models.ForeignKey(
        Group,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="posts",
    )
    image = models.ImageField(
        upload_to="posts/",
        blank=True,
    )

    def __str__(self):
        return self.text[: settings.NUM_CHAR]

    class Meta:
        ordering = ["-pub_date", "text"]


class Comment(models.Model):
    """Table settings for post comment."""

    text = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name="comments",
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="comments",
    )

    def __str__(self):
        return self.text[: settings.NUM_CHAR]


class Follow(models.Model):
    """Table settings for user subscriptions."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="follower",
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="following",
    )
