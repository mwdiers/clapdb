from django import template
from django.utils.html import format_html
from ..models import Snippet

register = template.Library()


@register.simple_tag
def get_snippet(slug):
    try:
        content = Snippet.objects.get(slug=slug).html
    except Snippet.DoesNotExist:
        content = ""
    return format_html(content)
