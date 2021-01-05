import markdown

from django import template
from django.db.models import Count
from django.utils.safestring import mark_safe

from ..models import Post

# Регистрация всех тегов в файле
register = template.Library()


@register.simple_tag(name='total_posts')
def total_posts():
    """Количество опубликованных статей"""
    return Post.published.count()


@register.inclusion_tag('blog/post/latest_posts.html')
def show_latest_posts(count=5):
    """Последние добавленные статьи"""
    latest_posts = Post.published.order_by('publish')[:count]
    return {'latest_posts': latest_posts}


@register.simple_tag
def get_most_commented_posts(count=5):
    """Статьи с наибольшим кол-вом комментов"""
    # annotate - добавление к каждой статье (Post) количества комментариев (total_comments)
    # Count - ф-ия агрегации
    return Post.published.annotate(
        total_comments=Count('comments')).order_by('-total_comments')[:count]


@register.filter(name='markdown')
def markdown_format(text):
    """Фильтр markdown"""
    # результат работы ф-ии mark_safe - HTML код
    return mark_safe(markdown.markdown(text))
