from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required

from .models import Post, Group, User, Follow
from .forms import PostForm, CommentForm
from .utils import get_paginator


# Главная страница
# @cache_page(20)
def index(request):
    page_obj, total_count = get_paginator(Post.objects.all(), request)
    context = {
        'page_obj': page_obj
    }
    return render(request, 'posts/index.html', context)


# Страница со списком опубликованных постов
def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    page_obj, total_count = get_paginator(group.posts.all(), request)
    context = {
        'group': group,
        'page_obj': page_obj
    }
    return render(request, 'posts/group_list.html', context)


def profile(request, username):
    author = get_object_or_404(User, username=username)
    page_obj, posts_amount = get_paginator(author.posts.all(), request)
    user = request.user
    following = False
    if user.is_authenticated:
        following = Follow.objects.filter(user=request.user, author=author)
    context = {
        'author': author,
        'posts_amount': posts_amount,
        'page_obj': page_obj,
        'following': following
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    full_post = get_object_or_404(Post, pk=post_id)
    title = full_post.text
    author_posts = Post.objects.filter(author=full_post.author)
    form = CommentForm()
    comments = full_post.comments.all()
    context = {
        'title': title,
        'post': full_post,
        'posts_amount': author_posts.count(),
        'form': form,
        'comments': comments,
    }
    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
    )
    if form.is_valid():
        form = form.save(commit=False)
        form.author = request.user
        form.save()
        return redirect('posts:profile', form.author)
    template = 'posts/post_create.html'
    context = {
        'form': form,
    }
    return render(request, template, context)


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    if post.author != request.user:
        return redirect('posts:post_detail', post_id=post_id)
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post
    )
    if form.is_valid():
        form.save()
        return redirect('posts:post_detail', post.pk)
    template = 'posts/post_create.html'
    is_edit = True
    context = {
        'form': form,
        'is_edit': is_edit,
    }
    return render(request, template, context)


@login_required
def add_comment(request, post_id):
    post = Post.objects.get(pk=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def follow_index(request):
    posts = Post.objects.filter(author__following__user=request.user)
    page_obj, total_count = get_paginator(posts, request)
    context = {
        'page_obj': page_obj
    }
    return render(request, 'posts/follow.html', context)


@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    follower = Follow.objects.filter(
        user=request.user,
        author=author
    ).exists()
    if author == request.user or follower:
        return redirect(
            'posts:profile',
            username=username
        )
    Follow.objects.create(user=request.user, author=author)
    return redirect(
        'posts:profile',
        username=username
    )


@login_required
def profile_unfollow(request, username):
    author = get_object_or_404(User, username=username)
    if author != request.user:
        following = get_object_or_404(
            Follow, user=request.user, author=author
        )
        following.delete()
    return redirect(
        'posts:profile',
        username=username
    )
