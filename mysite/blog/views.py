from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank, TrigramSimilarity
from django.core.mail import send_mail
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import Count  # подсчёт кол-ва
from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView
from taggit.models import Tag

from .forms import EmailPostForm, CommentForm, SearchForm
from .models import Post, Comment


def post_list(request, tag_slug=None):
    """Список статей"""
    object_list = Post.published.all()

    # Фильтрация по тегу, подсистема тегов (django-taggit==0.22.2)
    tag = None

    if tag_slug:
        tag = get_object_or_404(Tag, slug=tag_slug)
        object_list = object_list.filter(tags__in=[tag])

    paginator = Paginator(object_list, 3)  # по 3 статьи на каждой странице
    # извлекаем из запроса GET параметр 'page' - текущая страница
    page = request.GET.get('page')
    try:
        # Получаем список объектов на нужной странице с помощью метода page()
        posts = paginator.page(page)
    except PageNotAnInteger:
        # Если страница не является целым числом, возращает первую страницу
        posts = paginator.page(1)
    except EmptyPage:
        # Если номер страницы больше, чем общее количество страниц, возращаем последнюю
        posts = paginator.page(paginator.num_pages)

    return render(request, 'blog/post/list.html', {
        'page': page,
        'posts': posts,
        'tag': tag,
    })


# class PostListView(ListView):
#     """Список статей. Замена обработчика post_list"""
#     queryset = Post.published.all()
#     context_object_name = 'posts'  # по умолчанию object_list
#     paginate_by = 3
#     template_name = 'blog/post/list.html'  # по умолчанию blog/post_list.html


def post_detail(request, year, month, day, post):
    """Отображение статьи"""
    post = get_object_or_404(Post, slug=post,
                             status='published',
                             publish__year=year,
                             publish__month=month,
                             publish__day=day)

    # Список активных комментариев для этой статьи
    comments = post.comments.filter(active=True)

    new_comment = None

    if request.method == 'POST':
        # Пользователь отправил комментарий
        comment_form = CommentForm(data=request.POST)
        if comment_form.is_valid():
            # Создаём комментарий, но пока не сохраняем в базе данных
            new_comment = comment_form.save(commit=False)
            # Привязываем комментарий к текущей статье
            new_comment.post = post
            # Сохраняем комментарий в базе данных
            new_comment.save()
    else:
        comment_form = CommentForm()

    # Формирование списка похожих статей
    # Получаем id всех тегов текущей статьи
    post_tags_ids = post.tags.values_list('id', flat=True)
    # Получаем все статьи содержащий хотябы один из полученных тегов
    similar_posts = Post.published.filter(
        tags__in=post_tags_ids).exclude(id=post.id)
    similar_posts = similar_posts.annotate(
        same_tags=Count('tags')).order_by('-same_tags', '-publish')[:4]

    return render(request, 'blog/post/detail.html', {
        'post': post,
        'comments': comments,
        'new_comment': new_comment,
        'comment_form': comment_form,
        'similar_posts': similar_posts,
    })


def post_share(request, post_id):
    """Отправка данных из формы на почту"""
    # Получение статьи по id, status='published' - статья опубликована
    post = get_object_or_404(Post, id=post_id, status='published')
    sent = False  # для вывода сообщения об успешной отправке

    if request.method == 'POST':
        # Форма (EmailPostForm) с данными (request.POST), при POST запросе
        form = EmailPostForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data  # словарь с полями форм и их значениями

            # Отправка электронной почты
            # Получаем абсолютную ссылку на статью
            post_url = request.build_absolute_uri(post.get_absolute_url())
            subject = ('{} ({}) recommends you reading "{}"'.format(
                cd['name'], cd['email'], post.title))
            message = ('Read "{}" at {}\n\n{}\'s comments: {}'.format(
                post.title, post_url, cd['name'], cd['comments']))
            send_mail(subject, message, 'admin@example.com', [cd['to']])
            sent = True
    else:
        # Пустая форма (EmailPostForm) при GET запросе
        form = EmailPostForm()

    return render(request, 'blog/post/share.html', {
        'post': post,
        'form': form,
        'sent': sent,
    })


def post_search(request):
    """Полнотекстовый поиск"""
    form = SearchForm()
    query = None
    results = []

    # Определяем отправленна ли форма для поиска
    if 'query' in request.GET:
        form = SearchForm(request.GET)
        if form.is_valid():
            query = form.cleaned_data['query']
            # search_vector = SearchVector('title', 'body')
            # results = Post.objects.annotate(search=search_vector).filter(search=query)
            search_vector = SearchVector('title', weight='A') + SearchVector('body', weight='B')
            search_query = SearchQuery(query)
            # results = Post.objects.annotate(
            #     search=search_vector,
            #     rank=SearchRank(search_vector, search_query)
            # ).filter(rank__gte=0.3).order_by('-rank')
            results = Post.objects.annotate(
                similarity=TrigramSimilarity('title', query),
            ).filter(similarity__gt=0.3).order_by('-similarity')

    return render(request, 'blog/post/search.html', {
        'form': form,
        'query': query,
        'results': results,
    })
