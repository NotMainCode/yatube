"""Utilities"""

from django.conf import settings
from django.core.paginator import Paginator


def paginator_func(request, post_list):
    """Splitting data into multiple pages."""

    paginator = Paginator(post_list, settings.NUM_POSTS)
    page_number = request.GET.get("page")
    return paginator.get_page(page_number)
