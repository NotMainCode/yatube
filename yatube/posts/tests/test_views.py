import shutil
import tempfile
from http import HTTPStatus
from random import randint

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from ..forms import PostForm
from ..models import Comment, Follow, Group, Post

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)

User = get_user_model()


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class TaskPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username="Author")
        cls.user_follower = User.objects.create_user(username="Follower")
        cls.group = Group.objects.create(
            title="Тестовая группа",
            slug="test-slug",
            description="Тестовое описание",
        )
        small_gif = (
            b"\x47\x49\x46\x38\x39\x61\x02\x00"
            b"\x01\x00\x80\x00\x00\x00\x00\x00"
            b"\xFF\xFF\xFF\x21\xF9\x04\x00\x00"
            b"\x00\x00\x00\x2C\x00\x00\x00\x00"
            b"\x02\x00\x01\x00\x00\x02\x02\x0C"
            b"\x0A\x00\x3B"
        )
        uploaded = SimpleUploadedFile(
            name="small.gif",
            content=small_gif,
            content_type="image/gif",
        )
        cls.post = Post.objects.create(
            text="Тестовый пост",
            author=cls.user,
            group=cls.group,
            image=uploaded,
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        cache.clear()
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(TaskPagesTests.user)

    def test_page_name_uses_correct_template_guest_user(self):
        """Name of public page uses the appropriate template."""

        page_name_template = {
            reverse("posts:index"): "posts/index.html",
            reverse(
                "posts:group_list", args={self.group.slug}
            ): "posts/group_list.html",
            reverse(
                "posts:post_detail", args={self.post.id}
            ): "posts/post_detail.html",
            reverse(
                "posts:profile", args={self.user.username}
            ): "posts/profile.html",
        }
        for reverse_name, template in page_name_template.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.guest_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_page_name_uses_correct_template_post_author(self):
        """
        Name of private page uses the appropriate template.
        """

        private_page_name_templates = {
            reverse(
                "posts:post_edit", args={self.post.id}
            ): "posts/create_post.html",
            reverse("posts:post_create"): "posts/create_post.html",
        }
        for reverse_name, template in private_page_name_templates.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_page_show_correct_context(self):
        """The index template is formed with the correct context."""

        response = self.guest_client.get(reverse("posts:index"))
        self.assertIn(
            "page_obj",
            response.context,
            msg="The 'page_obj' key is missing from the context dictionary.",
        )
        self.assertEqual(response.context["page_obj"][0], self.post)

    def test_group_list_page_show_correct_context(self):
        """The group_list template is formed with the correct context."""

        response = self.guest_client.get(
            reverse("posts:group_list", args={self.group.slug})
        )
        context_key = ["group", "page_obj"]
        for key in context_key:
            with self.subTest(expected_context_key=key):
                self.assertIn(key, response.context)
        value_expected = {
            response.context["group"]: self.group,
            response.context["page_obj"][0]: self.post,
        }
        for value, expected in value_expected.items():
            with self.subTest():
                self.assertEqual(value, expected)

    def test_profile_page_show_correct_context(self):
        """The profile template is formed with the correct context."""

        response = self.authorized_client.get(
            reverse("posts:profile", args={self.user.username})
        )
        context_key = ["author", "page_obj"]
        for key in context_key:
            with self.subTest(expected_context_key=key):
                self.assertIn(key, response.context)
        value_expected = {
            response.context["author"]: self.user,
            response.context["page_obj"][0]: self.post,
        }
        for value, expected in value_expected.items():
            with self.subTest(expected=expected):
                self.assertEqual(value, expected)

    def test_post_detail_show_correct_context(self):
        """The post_detail template is formed with the correct context."""

        response = self.guest_client.get(
            reverse("posts:post_detail", args={self.post.id}),
        )
        self.assertIn(
            "post",
            response.context,
            msg="The 'post' key is missing from the context dictionary.",
        )
        self.assertEqual(response.context["post"], self.post)

    def test_post_create_edit_show_correct_context(self):
        """
        The post_create/edit template is formed with the correct context.
        """

        address = [
            reverse("posts:post_create"),
            reverse("posts:post_edit", args={self.post.id}),
        ]
        for address in address:
            with self.subTest():
                response = self.authorized_client.get(address)
                self.assertIn("form", response.context)
                self.assertEqual(type(response.context["form"]), PostForm)
                try:
                    self.assertEqual(response.context["is_edit"], True)
                except KeyError:
                    pass

    def test_new_post_created_correctly(self):
        """The new post is displayed correctly on the pages."""

        new_post = Post.objects.create(
            text="Новый пост",
            author=self.user,
            group=self.group,
        )
        address_list = [
            reverse("posts:index"),
            reverse("posts:profile", args={self.user.username}),
            reverse("posts:group_list", args={self.group.slug}),
        ]
        for address in address_list:
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertIn(new_post, response.context["page_obj"])

    def test_paginator(self):
        """The paginator test."""

        add_num_post = randint(0, settings.NUM_POSTS)
        num_post = settings.NUM_POSTS + add_num_post
        post_list = []
        for i in range(1, num_post):
            post_list.append(
                Post(
                    text=f"Тестовый пост{i}",
                    author=self.user,
                    group=self.group,
                )
            )
        Post.objects.bulk_create(post_list)
        addresses = [
            reverse("posts:index"),
            reverse("posts:group_list", args={self.group.slug}),
            reverse("posts:profile", args={self.user.username}),
        ]
        page_post_count = {
            1: settings.NUM_POSTS,
            2: add_num_post,
        }
        for address in addresses:
            for page, post_count in page_post_count.items():
                with self.subTest(address=address):
                    response = self.authorized_client.get(
                        address, {"page": page}
                    )
                    self.assertEqual(
                        len(response.context["page_obj"]), post_count
                    )

    def test_new_comment_created_correctly(self):
        """The new comment is displayed on the post page."""

        new_comment = Comment.objects.create(
            text="Новый комментарий",
            post=self.post,
            author=self.user,
        )
        response = self.guest_client.get(
            reverse("posts:post_detail", args={self.post.id})
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertIn(new_comment, response.context["comments"])

    def test_authorized_user_follow(self):
        """Authorized user can follow other user."""

        self.authorized_client.force_login(self.user_follower)
        new_follow_count = Follow.objects.count() + 1
        response = self.authorized_client.get(
            reverse("posts:profile_follow", args={self.user.username})
        )
        subscription = Follow.objects.first()
        current_expected = {
            response.status_code: HTTPStatus.FOUND,
            Follow.objects.count(): new_follow_count,
            subscription.user: self.user_follower,
            subscription.author: self.user,
        }
        for current, expected in current_expected.items():
            with self.subTest():
                self.assertEqual(current, expected)
        self.assertRedirects(
            response, reverse("posts:profile", args={self.user.username})
        )

    def test_authorized_user_unfollow(self):
        """Authorized user can unfollow other user."""

        self.authorized_client.force_login(self.user_follower)
        Follow.objects.create(
            user=self.user_follower,
            author=self.user,
        )
        response = self.authorized_client.get(
            reverse("posts:profile_unfollow", args={self.user.username})
        )
        current_expected = {
            response.status_code: HTTPStatus.FOUND,
            Follow.objects.filter(
                user=self.user_follower, author=self.user
            ).exists(): False,
        }
        for current, expected in current_expected.items():
            with self.subTest():
                self.assertEqual(current, expected)
        self.assertRedirects(
            response, reverse("posts:profile", args={self.user.username})
        )

    def test_follower_feed(self):
        """Correctness of the subscription page."""

        self.authorized_client.force_login(self.user_follower)
        Follow.objects.create(
            user=self.user_follower,
            author=self.user,
        )
        new_post = Post.objects.create(
            text="Новый пост в ленте подписок",
            author=self.user,
        )
        response = self.authorized_client.get(reverse("posts:follow_index"))
        current_expected = {
            response.status_code: HTTPStatus.OK,
            response.context["page_obj"][0]: new_post,
        }
        for current, expected in current_expected.items():
            with self.subTest():
                self.assertEqual(
                    current,
                    expected,
                    msg="The subscription feed is incorrect.",
                )
        user_not_follower = User.objects.create_user(username="NotFollower")
        self.authorized_client.force_login(user_not_follower)
        response = self.authorized_client.get(reverse("posts:follow_index"))
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertNotIn(
            new_post,
            response.context["page_obj"],
            msg="The subscription feed is incorrect.",
        )
