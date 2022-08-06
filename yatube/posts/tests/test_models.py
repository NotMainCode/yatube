from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import TestCase

from ..models import Group, Post

User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username="auth")
        cls.group = Group.objects.create(
            title="Тестовая группа",
            slug="test-slug",
            description="Тестовое описание",
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text="Длинный тестовый пост",
            group=cls.group,
        )

    def test_models_have_correct_object_names(self):
        """Models __str__ work correctly."""

        value_expected = {
            str(self.group.title): self.group.title,
            str(self.post): self.post.text[: settings.NUM_CHAR],
        }
        for value, expected in value_expected.items():
            with self.subTest(expected_object_name=expected):
                self.assertEqual(value, expected)
