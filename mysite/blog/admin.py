from django.contrib import admin

from .models import Post, Comment


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug', 'author', 'publish', 'status')
    list_filter = ('status', 'created', 'publish', 'author')
    search_fields = ('title', 'body')
    date_hierarchy = 'publish'  # навигация по датам
    ordering = ('status', 'publish')  # сортировка по
    # автоматическая генерация поля slug
    prepopulated_fields = {'slug': ('title',)}
    raw_id_fields = ('author',)  # поле поиска при заполнении формы


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'post', 'created', 'active')
    list_filter = ('active', 'created', 'updated')
    search_fields = ('name', 'email', 'body')
