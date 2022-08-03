from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import TestCase
from django.urls import reverse

from ..models import Post

User = get_user_model()


class CacheTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

    def test_cache_index_page(self):
        """Checking the caching of the main page."""

        user = User.objects.create_user(username="Author")
        post = Post.objects.create(
            text="Тестовый пост",
            author=user,
        )
        response = self.client.get(reverse("posts:index"))
        index_content = response.content
        Post.objects.get(id=post.id).delete()
        response = self.client.get(reverse("posts:index"))
        index_content_cache = response.content
        cache.clear()
        response = self.client.get(reverse("posts:index"))
        index_content_no_cache = response.content
        self.assertEqual(index_content, index_content_cache)
        self.assertNotEqual(
            index_content,
            index_content_no_cache,
        )
