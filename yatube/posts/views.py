"""URLs request handlers of the 'Posts' application."""

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.cache import cache_page

from posts.forms import CommentForm, PostForm
from posts.models import Follow, Group, Post, User
from posts.utils import paginator_func


@cache_page(settings.CACHE_TIME, key_prefix="index_page")
def index(request):
    """Main page."""
    post_list = Post.objects.select_related("group", "author")
    page_obj = paginator_func(request, post_list)
    context = {
        "page_obj": page_obj,
        "index": True,
    }
    return render(request, "posts/index.html", context)


def group_posts(request, slug):
    """Page of user posts filtered by groups."""
    group = get_object_or_404(Group, slug=slug)
    post_list = group.posts.select_related("group", "author")
    page_obj = paginator_func(request, post_list)
    context = {
        "group": group,
        "page_obj": page_obj,
    }
    return render(request, "posts/group_list.html", context)


def profile(request, username):
    """Page of user profile."""
    author = get_object_or_404(User, username=username)
    post_list = author.posts.select_related("group", "author")
    page_obj = paginator_func(request, post_list)
    following = (
        request.user.is_authenticated
        and Follow.objects.filter(user=request.user, author=author).exists()
    )
    context = {
        "author": author,
        "page_obj": page_obj,
        "following": following,
    }
    return render(request, "posts/profile.html", context)


def post_detail(request, post_id):
    """Page of single post."""
    post = get_object_or_404(
        Post.objects.select_related("group", "author"), id=post_id
    )
    form = CommentForm()
    comments = post.comments.select_related("author")
    context = {
        "post": post,
        "form": form,
        "comments": comments,
    }
    return render(request, "posts/post_detail.html", context)


@login_required
def post_create(request):
    """Page for adding a new post."""
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
    )
    context = {"form": form}
    if not form.is_valid():
        return render(request, "posts/create_post.html", context)
    form.instance.author = request.user
    form.save()
    return redirect("posts:profile", username=request.user.username)


@login_required
def post_edit(request, post_id):
    """Post editing pages."""
    post = get_object_or_404(Post, pk=post_id)
    if request.user != post.author:
        return redirect("posts:post_detail", post_id=post_id)
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post,
    )
    context = {
        "form": form,
        "is_edit": True,
    }
    if form.is_valid():
        form.save()
        return redirect("posts:post_detail", post_id=post_id)
    return render(request, "posts/create_post.html", context)


@login_required
def add_comment(request, post_id):
    """Creating a comment to the post."""
    form = CommentForm(request.POST or None)
    if form.is_valid():
        form.instance.author = request.user
        form.instance.post = get_object_or_404(Post, id=post_id)
        form.save()
    return redirect("posts:post_detail", post_id=post_id)


@login_required
def follow_index(request):
    """Posts of authors to which the user is subscribed."""
    post_list = Post.objects.filter(author__following__user=request.user)
    page_obj = paginator_func(request, post_list)
    context = {
        "page_obj": page_obj,
        "follow": True,
    }
    return render(request, "posts/follow.html", context)


@login_required
def profile_follow(request, username):
    """Subscribe to the author."""
    if request.user.username != username:
        follow_author = get_object_or_404(User, username=username)
        Follow.objects.get_or_create(user=request.user, author=follow_author)
    return redirect("posts:profile", username=username)


@login_required
def profile_unfollow(request, username):
    """Unsubscribe from the author."""
    unfollow_author = get_object_or_404(User, username=username)
    Follow.objects.filter(user=request.user, author=unfollow_author).delete()
    return redirect("posts:profile", username=username)
