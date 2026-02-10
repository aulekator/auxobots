from django.urls import path
from .views import PostListView, PostDetailView, CommentCreateView

app_name = 'sqblog'

urlpatterns = [
    path('blog/', PostListView.as_view(), name='post_list'),
    path('category/<slug:category_slug>/', PostListView.as_view(), name='post_list_by_category'),
    path('tag/<slug:tag_slug>/', PostListView.as_view(), name='post_list_by_tag'),
    path('post/<slug:slug>/', PostDetailView.as_view(), name='post_detail'),
    path('post/<slug:slug>/comment/', CommentCreateView.as_view(), name='comment_create'),
]