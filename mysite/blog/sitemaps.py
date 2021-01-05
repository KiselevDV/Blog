from django.contrib.sitemaps import Sitemap

from .models import Post


class PostSitemap(Sitemap):
    """Карта сайта"""
    # Частота обновления страниц и степень их совпадения
    changefreq = 'weekly'
    priority = 0.9

    def items(self):
        # Возвращает  QuerySet объектов, которые будут отображаться на карте сайта
        return Post.published.all()

    def lastmod(self, obj):
        # Принимает каждый объект и из результата вызова 'items'
        # и возвращает время последней модификации статьи
        return obj.updated
