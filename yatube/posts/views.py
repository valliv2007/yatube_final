from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.cache import cache_page

from .forms import CommentForm, PostForm
from .models import Follow, Group, Post
from .utils import paginate_posts

AMOUNT_POSTS = 10

User = get_user_model()


@cache_page(20, key_prefix='index_page')
def index(request):
    post_list = Post.objects.select_related('group', 'author')
    context = {'page_obj': paginate_posts(request, post_list, AMOUNT_POSTS)}
    return render(request, 'posts/index.html', context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    post_list = group.posts.all()
    context = {'group': group,
               'page_obj': paginate_posts(request, post_list, AMOUNT_POSTS)}
    return render(request, 'posts/group_list.html', context)


def profile(request, username):
    author = get_object_or_404(User, username=username)
    post_list = author.posts.all()
    counter = post_list.count()
    following = False
    if request.user.is_authenticated:
        following = request.user.follower.filter(author=author.id).exists()
    context = {'author': author,
               'page_obj': paginate_posts(request, post_list, AMOUNT_POSTS),
               'counter': counter,
               'following': following}
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    author = post.author
    counter = author.posts.count()
    form = CommentForm()
    comments = post.comments
    context = {'author': author,
               'post': post,
               'counter': counter,
               'form': form,
               'comments': comments}
    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):
    form = PostForm(request.POST or None, files=request.FILES or None)
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect('posts:profile', username=post.author)
    return render(request, 'posts/create_post.html', {'form': form})


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    if post.author != request.user:
        return redirect('posts:profile', username=post.author)
    form = PostForm(request.POST or None,
                    files=request.FILES or None,
                    instance=post)
    if form.is_valid():
        form.save()
        return redirect('posts:post_detail', post_id)
    context = {'form': form, 'is_edit': True}
    return render(request, 'posts/create_post.html', context)


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid:
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def follow_index(request):
    post_list = Post.objects.filter(author__following__user=request.user.id)
    context = {'page_obj': paginate_posts(request, post_list, AMOUNT_POSTS)}
    return render(request, 'posts/follow.html', context)


@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    if (not Follow.objects.filter(user=request.user.id,
                                  author=author.id).exists()
            and author != request.user):
        Follow.objects.create(
            user=request.user,
            author=author)
    return redirect('posts:profile', username=username)


@login_required
def profile_unfollow(request, username):
    author = get_object_or_404(User, username=username)
    deleted_subscribe = Follow.objects.filter(user=request.user.id,
                                              author=author.id)
    if deleted_subscribe.exists():
        deleted_subscribe.delete()
    return redirect('posts:profile', username=username)
