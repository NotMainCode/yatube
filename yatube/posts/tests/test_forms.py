import shutil
import tempfile
from http import HTTPStatus

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from ..models import Group, Post

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)

User = get_user_model()


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostFormTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user_1 = User.objects.create_user(username="Author")
        cls.user_2 = User.objects.create_user(username="NotAuthor")
        cls.group_1 = Group.objects.create(
            title="Тестовая группа 1",
            slug="test-slug_1",
            description="Тестовое описание 1",
        )
        cls.group_2 = Group.objects.create(
            title="Тестовая группа 2",
            slug="test-slug_2",
            description="Тестовое описание 2",
        )
        cls.post = Post.objects.create(
            text="Тестовый пост",
            author=cls.user_1,
            group=cls.group_1,
        )

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(PostFormTests.user_1)

    def test_create_post_authorized_user(self):
        """A valid form creates a new post (authorized user)."""

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
        new_posts_count = Post.objects.count() + 1
        form_data = {
            "text": "Текст из формы",
            "group": self.group_2.id,
            "image": uploaded,
        }
        response = self.authorized_client.post(
            reverse("posts:post_create"),
            data=form_data,
            follow=True,
        )
        self.assertRedirects(
            response,
            reverse(
                "posts:profile",
                args=(self.user_1.username,),
            ),
        )
        new_post = Post.objects.first()
        value_expected = {
            response.status_code: HTTPStatus.OK,
            Post.objects.count(): new_posts_count,
            new_post.text: form_data["text"],
            new_post.group: self.group_2,
            new_post.author: self.user_1,
            new_post.image: f"posts/{uploaded.name}",
        }
        for value, expected in value_expected.items():
            with self.subTest():
                self.assertEqual(value, expected)
        self.assertTrue(new_post.image)

    def test_create_post_reject_authorized_user(self):
        """Invalid form do not creates a post entry (authorized user)."""

        new_posts_count = Post.objects.count()
        form_data = {
            "text": "",
            "group": self.group_1.id,
        }
        response = self.authorized_client.post(
            reverse("posts:post_create"),
            data=form_data,
            follow=True,
        )
        value_expected = {
            response.status_code: HTTPStatus.OK,
            Post.objects.count(): new_posts_count,
        }
        for value, expected in value_expected.items():
            with self.subTest():
                self.assertEqual(value, expected)
        self.assertFormError(response, "form", "text", "Обязательное поле.")

    def test_edit_post_authorized_user(self):
        """Valid editing form changes the post (authorized user)."""

        editable_post = Post.objects.create(
            text="Пост для редактирования",
            author=self.user_1,
            group=self.group_1,
        )
        new_posts_count = Post.objects.count()
        form_data = {
            "text": "Изменённый текст из формы",
            "group": self.group_2.id,
        }
        response = self.authorized_client.post(
            reverse("posts:post_edit", args=(editable_post.id,)),
            data=form_data,
            follow=True,
        )
        editable_post.refresh_from_db()
        current_expected = {
            response.status_code: HTTPStatus.OK,
            Post.objects.count(): new_posts_count,
            editable_post.text: form_data["text"],
            editable_post.group: self.group_2,
        }
        for current, expected in current_expected.items():
            with self.subTest():
                self.assertEqual(current, expected)
        self.assertRedirects(
            response,
            reverse("posts:post_detail", args=(editable_post.id,)),
        )

    def test_edit_post_reject_authorized_user(self):
        """Invalid editing form do not change the post (authorized user)."""

        new_posts_count = Post.objects.count()
        form_data = {
            "text": "",
            "group": self.group_2.id,
        }
        response = self.authorized_client.post(
            reverse("posts:post_edit", args=(self.post.id,)),
            data=form_data,
            follow=True,
        )
        editable_post = Post.objects.get(id=self.post.id)
        current_expected = {
            response.status_code: HTTPStatus.OK,
            Post.objects.count(): new_posts_count,
            editable_post.text: self.post.text,
            editable_post.group: self.post.group,
        }
        for current, expected in current_expected.items():
            self.assertEqual(current, expected)
        self.assertFormError(response, "form", "text", "Обязательное поле.")

    def test_edit_post_reject_not_post_author(self):
        """The not post author cannot edit the post."""

        self.authorized_client.force_login(self.user_2)
        new_posts_count = Post.objects.count()
        form_data = {
            "text": "Текст не автора поста",
            "group": PostFormTests.group_2.id,
        }
        response = self.authorized_client.post(
            reverse("posts:post_edit", args=(self.post.id,)),
            data=form_data,
            follow=True,
        )
        editable_post = Post.objects.get(id=self.post.id)
        current_expected = {
            response.status_code: HTTPStatus.OK,
            Post.objects.count(): new_posts_count,
            editable_post.text: self.post.text,
            editable_post.group: self.post.group,
        }
        for current, expected in current_expected.items():
            self.assertEqual(current, expected)
        self.assertRedirects(
            response,
            reverse("posts:post_detail", args=(self.post.id,)),
        )

    def test_create_post_reject_guest_user(self):
        """
        The guest user cannot create a post, and is redirected to login page.
        """

        new_posts_count = Post.objects.count()
        form_data = {
            "text": "Текст пользователя-гостя",
            "group": self.group_1.id,
        }
        login_url = reverse("users:login")
        post_create_url = reverse("posts:post_create")
        target_url = f"{login_url}?next={post_create_url}"
        response = self.client.post(
            post_create_url,
            data=form_data,
            follow=True,
        )
        value_expected = {
            response.status_code: HTTPStatus.OK,
            Post.objects.count(): new_posts_count,
        }
        for value, expected in value_expected.items():
            with self.subTest():
                self.assertEqual(value, expected)
        self.assertRedirects(response, target_url)

    def test_add_comment_available_authorized_user(self):
        """Authorized user can comment on posts."""

        new_comments_count = self.post.comments.count() + 1
        form_data = {"text": "Комментарий авторизованного пользователя"}
        response = self.authorized_client.post(
            reverse("posts:add_comment", args=(self.post.id,)),
            data=form_data,
            follow=True,
        )
        comments = self.post.comments
        current_expected = {
            response.status_code: HTTPStatus.OK,
            comments.count(): new_comments_count,
            comments.last().text: form_data["text"],
        }
        for current, expected in current_expected.items():
            with self.subTest():
                self.assertEqual(current, expected)
        self.assertRedirects(
            response,
            reverse("posts:post_detail", args=(self.post.id,)),
        )

    def test_add_comment_reject_guest_user(self):
        """
        Guest user cannot comment on posts, and is redirected to login page.
        """

        new_comments_count = self.post.comments.count()
        form_data = {"text": "Комментарий гостя"}
        login_url = reverse("users:login")
        add_comment_url = reverse("posts:add_comment", args=(self.post.id,))
        target_url = f"{login_url}?next={add_comment_url}"
        response = self.client.post(
            add_comment_url,
            data=form_data,
            follow=True,
        )
        current_expected = {
            response.status_code: HTTPStatus.OK,
            self.post.comments.count(): new_comments_count,
        }
        for current, expected in current_expected.items():
            with self.subTest():
                self.assertEqual(current, expected)
        self.assertRedirects(response, target_url)
