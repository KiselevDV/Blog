from django.urls import path

from . import views
from .feeds import LatestPostFeed

app_name = 'blog'
urlpatterns = [
    # Обработчики приложения блога
    path('', views.post_list, name='post-list'),
    # path('', views.PostListView.as_view(), name='post-list'),
    path('<int:year>/<int:month>/<int:day>/<slug:post>/',
         views.post_detail, name='post-detail'),
    # Отправка данных на e-mail
    path('<int:post_id>/share/', views.post_share, name='post-share'),
    # Вывод стандартной страницы с тегами
    path('tag/<slug:tag_slug>/', views.post_list, name='post-list-by-tag'),
    # RSS для статей
    path('feed/', LatestPostFeed(), name='post_feed'),
    # Поиск по нескольким полям (полнотекстовый поиск)
    path('search/', views.post_search, name='post_search'),
]
