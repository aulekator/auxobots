from django.views.generic import ListView, DetailView, View
from django.shortcuts import get_object_or_404, redirect, render
from .models import Post, Category, Tag
from .forms import CommentForm


class PostListView(ListView):
    model = Post
    template_name = 'blog/post_list.html'
    context_object_name = 'posts'
    paginate_by = 5

    def get_queryset(self):
        queryset = super().get_queryset().select_related('author').prefetch_related('categories', 'tags')
        category_slug = self.kwargs.get('category_slug')
        tag_slug = self.kwargs.get('tag_slug')
        if category_slug:
            category = get_object_or_404(Category, slug=category_slug)
            queryset = queryset.filter(categories=category)
        elif tag_slug:
            tag = get_object_or_404(Tag, slug=tag_slug)
            queryset = queryset.filter(tags=tag)
        else:
            queryset = queryset.order_by('-pub_date')
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context
     
class PostDetailView(DetailView):
    model = Post
    template_name = 'blog/post_detail.html'
    context_object_name = 'post'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['comment_form'] = CommentForm()
        context['comments'] = self.object.comments.filter(approved=True)
        return context

class CommentCreateView(View):
    def post(self, request, slug):
        post = get_object_or_404(Post, slug=slug)
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.approved = False
            comment.save()
            return redirect('sqblog:post_detail', slug=post.slug)
        context = {
            'post': post,
            'comment_form': form,
            'comments': post.comments.filter(approved=True),
        }
        return render(request, 'blog/post_detail.html', context)