from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Group, Post

User = get_user_model()


class PostURLTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username="Author")
        cls.group = Group.objects.create(
            title="Тестовая группа",
            slug="test-slug",
            description="Тестовое описание",
        )
        cls.post = Post.objects.create(
            text="Тестовый пост",
            author=cls.user,
            group=cls.group,
        )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(PostURLTests.user)

    def test_public_addresses_accessible_unauthorized_user(self):
        """
        Public addresses are available  to unauthorized users.
        """

        public_address = [
            reverse("posts:index"),
            reverse("posts:group_list", args=(self.group.slug,)),
            reverse("posts:post_detail", args=(self.post.id,)),
            reverse("posts:profile", args=(self.user.username,)),
        ]
        for address in public_address:
            with self.subTest(address=address):
                response = self.client.get(address)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_private_addresses_available_author(self):
        """
        Private addresses are available to the author.
        """

        private_address = [
            reverse("posts:post_edit", args=(self.post.id,)),
            reverse("posts:post_create"),
        ]
        for address in private_address:
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_url_redirect_anonymous(self):
        """Redirects for an unauthorized user."""

        login_url = reverse("users:login")
        url_with_redirect = [
            reverse("posts:post_edit", args=(self.post.id,)),
            reverse("posts:post_create"),
        ]
        for url in url_with_redirect:
            with self.subTest(address=url):
                response = self.client.get(url, follow=True)
                target_url = f"{login_url}?next={url}"
                self.assertRedirects(response, target_url)

    def test_editing_post_only_for_post_author(self):
        """The post editing page is unavailable to the not post author."""

        not_author = User.objects.create_user(username="NotAuthor")
        self.authorized_client.force_login(not_author)
        response = self.authorized_client.get(
            reverse("posts:post_edit", args=(self.post.id,)), follow=True
        )
        self.assertRedirects(
            response, reverse("posts:post_detail", args=(self.post.id,))
        )

    def test_error_404_for_unknown_page(self):
        """Error 404 when navigating to unexisting page."""

        response = self.client.get("/unexisting_page/")
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
