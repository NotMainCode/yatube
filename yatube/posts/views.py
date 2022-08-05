"""URLs request handlers of the 'Posts' application."""

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.cache import cache_page

from .forms import CommentForm, PostForm
from .models import Follow, Group, Post, User
from .utils import paginator_func


@cache_page(settings.CACHE_TIME, key_prefix="index_page")
def index(request):
    """Main page."""

    template = "posts/index.html"
    post_list = Post.objects.select_related("group", "author")
    page_obj = paginator_func(request, post_list)
    context = {
        "page_obj": page_obj,
        "index": True,
    }
    return render(request, template, context)


def group_posts(request, slug):
    """Page of user posts filtered by groups."""

    template = "posts/group_list.html"
    group = get_object_or_404(Group, slug=slug)
    post_list = group.posts.select_related("group", "author")
    page_obj = paginator_func(request, post_list)
    context = {
        "group": group,
        "page_obj": page_obj,
    }
    return render(request, template, context)


def profile(request, username):
    """Page of user profile."""

    template = "posts/profile.html"
    author = get_object_or_404(User, username=username)
    post_list = author.posts.select_related("group", "author")
    page_obj = paginator_func(request, post_list)
    following = (
        Follow.objects.filter(user=request.user, author=author).exists()
        if request.user.is_authenticated
        else False
    )
    context = {
        "author": author,
        "page_obj": page_obj,
        "following": following,
    }
    return render(request, template, context)


def post_detail(request, post_id):
    """Page of single post."""

    template = "posts/post_detail.html"
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
    return render(request, template, context)


@login_required
def post_create(request):
    """Page for adding a new post."""

    template = "posts/create_post.html"
    template_redirect = "posts:profile"
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
    )
    context = {"form": form}
    if not form.is_valid():
        return render(request, template, context)
    post = form.save(commit=False)
    post.author = request.user
    form.save()
    return redirect(template_redirect, username=request.user.username)


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
    template = "posts/create_post.html"
    template_redirect = "posts:post_detail"
    context = {
        "form": form,
        "is_edit": True,
    }
    if form.is_valid():
        form.save()
        return redirect(template_redirect, post_id=post_id)
    return render(request, template, context)


@login_required
def add_comment(request, post_id):
    """Creating a comment to the post."""

    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = get_object_or_404(Post, id=post_id)
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
