from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_cookie

from .forms import CommentForm, PostForm
from .models import Follow, Group, Post
from .utils import paginator_util

User = get_user_model()


@cache_page(20)
@vary_on_cookie
def index(request):
    """Шаблон главной страницы."""
    template = 'posts/index.html'
    page_obj = paginator_util(Post.objects.all(), request)
    context = {
        'page_obj': page_obj,
    }
    return render(request, template, context)


def group_posts(request, slug):
    """Шаблон страницы группы."""
    template = 'posts/group_list.html'
    group = get_object_or_404(Group, slug=slug)
    page_obj = paginator_util(group.posts.all(), request)
    context = {
        'page_obj': page_obj,
        'group': group,
    }
    return render(request, template, context)


def profile(request, username):
    """Шаблон страницы пользователя."""
    template = 'posts/profile.html'
    author = get_object_or_404(User, username=username)
    following = request.user.is_authenticated and Follow.objects.filter(
        author=author, user=request.user,
    ).exists()
    page_obj = paginator_util(author.posts.all(), request)
    context = {
        'author': author,
        'page_obj': page_obj,
        'following': following,
    }
    return render(request, template, context)


def post_detail(request, post_id):
    """Шаблон страницы поста."""
    template = 'posts/post_detail.html'
    post = get_object_or_404(Post, pk=post_id)
    comments = post.comments.all()
    form = CommentForm(request.POST or None)
    context = {
        'post': post,
        'form': form,
        'comments': comments,
    }
    return render(request, template, context)


@login_required
def post_create(request):
    """Шаблон страницы новой записи."""
    template = 'posts/create_post.html'
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
    )
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect('posts:profile', username=post.author)
    context = {
        'form': form,
    }
    return render(request, template, context)


@login_required
def post_edit(request, post_id):
    """Шаблон страницы редактирования записи."""
    template = 'posts/create_post.html'
    post = get_object_or_404(Post, pk=post_id)
    if request.user != post.author:
        return redirect('posts:post_detail', post.pk)
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post
    )
    if form.is_valid():
        form.save()
        return redirect('posts:post_detail', post_id)
    context = {'form': form, 'is_edit': True, 'post': post}
    return render(request, template, context)


@login_required
def add_comment(request, post_id):
    """Шаблон нового комментария."""
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def follow_index(request):
    """Шаблон страницы подписок."""
    template = 'posts/follow.html'
    page_obj = paginator_util(
        Post.objects.filter(author__following__user=request.user), request
    )
    context = {
        'page_obj': page_obj,
    }
    return render(request, template, context)


@login_required
def profile_follow(request, username):
    """Шаблон профиля автора для подписки."""
    template = 'posts/profile.html'
    author = get_object_or_404(User, username=username)
    if author != request.user:
        Follow.objects.get_or_create(
            user=request.user,
            author=author
        )
        return redirect('posts:profile', username)
    return redirect(template, username=author.username)


@login_required
def profile_unfollow(request, username):
    """Шаблон профиля автора для отписки."""
    Follow.objects.filter(
        user=request.user, author=get_object_or_404(User, username=username)
    ).delete()
    return redirect('posts:profile', username)


def groups(request):
    """Шаблон страницы списка групп."""
    template = 'posts/groups.html'
    page_obj = paginator_util(Group.objects.all(), request)
    context = {
        'page_obj': page_obj,
    }
    return render(request, template, context)
