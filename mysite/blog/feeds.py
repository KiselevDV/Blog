from django.contrib.syndication.views import Feed
from django.template.defaultfilters import truncatewords

from .models import Post


class LatestPostFeed(Feed):
    """RSS для статей"""
    title_template = 'My blog'
    link = '/blog/'
    description_template = 'New posts of my blog'

    def items(self):
        #  Объекты включённые в рассылку
        return Post.published.all()[:5]

    def item_title(self, item):
        # Получить для каждого объекта 'item' заголовок
        return item.title

    def item_description(self, item):
        # Получить для каждого объекта 'item' описание
        # truncatewords - ограничить item.body 30 словами
        return truncatewords(item.body, 30)
