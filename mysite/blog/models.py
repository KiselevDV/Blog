from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse
from django.utils import timezone
from taggit.managers import TaggableManager


class PublishedManager(models.Manager):
    """Свой менеджер Queryset,
    published вместо objects"""

    def get_queryset(self):
        return super().get_queryset().filter(status='published')


class Post(models.Model):
    """Статьи блога"""
    STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('published', 'Published'),
    )
    title = models.CharField('Заголовок', max_length=250)
    body = models.TextField('Основное содержание')
    author = models.ForeignKey(
        User, verbose_name='Автор', on_delete=models.CASCADE,
        related_name='blog_posts')
    publish = models.DateTimeField('Дата публикации', default=timezone.now)
    created = models.DateTimeField('Дата создания', auto_now_add=True)
    updated = models.DateTimeField('Последнее редактирование', auto_now=True)
    status = models.CharField(
        'Статус статьи', max_length=10, choices=STATUS_CHOICES, default='draft')
    slug = models.SlugField(max_length=250, unique_for_date='publish')

    objects = models.Manager()  # менеджер по умолчанию
    published = PublishedManager()  # наш новый менеджер

    tags = TaggableManager(blank=True)  # подсистема тегов (django-taggit==0.22.2)

    def get_absolute_url(self):
        return reverse('blog:post-detail',
                       args=(self.publish.year,
                             self.publish.month,
                             self.publish.day,
                             self.slug))

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Статья'
        verbose_name_plural = 'Статьи'
        ordering = ('-publish',)


class Comment(models.Model):
    """Комментарии для блога"""
    post = models.ForeignKey(
        Post, verbose_name='Статья', on_delete=models.CASCADE,
        related_name='comments')
    name = models.CharField('Имя пользователя', max_length=80)
    email = models.EmailField('Почта')
    body = models.TextField('Сообщение')
    created = models.DateTimeField('Дата создания', auto_now_add=True)
    updated = models.DateTimeField('Последнее редактирование', auto_now=True)
    active = models.BooleanField(default=True)

    def __str__(self):
        return f'Comment by {self.name} on {self.post}'

    class Meta:
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'
        ordering = ('created',)
