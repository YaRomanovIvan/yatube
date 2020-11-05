from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404, redirect

from .forms import PostForm, CommentForm
from .models import Post, Group, User, Follow


def page_not_found(request, exception):
    # Переменная exception содержит отладочную информацию, 
    # выводить её в шаблон пользователской страницы 404 мы не станем
    return render(
        request, 
        "misc/404.html", 
        {"path": request.path}, 
        status=404
    )


def server_error(request):
    return render(request, "misc/500.html", status=500) 


def index(request):
    post_list = Post.objects.all()
    paginator = Paginator(post_list, 10)

    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(
         request,
         'index.html',
         {'page': page, 'paginator': paginator}
     ) 


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.all()
    paginator = Paginator(posts, 10)

    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, "group.html", {'group': group, 'page': page, 'paginator': paginator})


@login_required
def new_post(request):
    """
    Создает новый пост
    """
    if request.method != 'POST':
        return render(request, 'new.html', {'form':PostForm()})
    form = PostForm(request.POST)
    if not form.is_valid():
        return render(request, 'new.html', {'form':PostForm()})
    user = form.save(commit=False)
    user.author = request.user
    user.save()
    return redirect('index')


def profile_info(_author, _user):
    author = get_object_or_404(User, username=_author)
    follow = Follow.objects.filter(author=author, user=_user).exists()
    following = author.following.count()
    follower = author.follower.count()
    post_cnt = author.posts.count()
    context = {
        'author': author,
        'post_cnt': post_cnt,
        'follow': follow,
        'following': following,
        'follower': follower

    }
    return context


def profile(request, username):
    info = profile_info(username, request.user)
    author_post = info['author'].posts.all()
    paginator = Paginator(author_post, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    context = {
        'page': page,
        'paginator': paginator,
    }
    context.update(info)
    return render(request, 'profile.html', context)


def post_view(request, username, post_id):
    info = profile_info(username, request.user)
    post = info['author'].posts.get(pk=post_id)
    comments = post.comments.all()
    context = {
        'comments': comments,
        'post': post,
        'form': CommentForm(),
    }
    context.update(info)
    return render(request, 'post.html', context)


@login_required
def post_edit(request, username, post_id):
    info = profile_info(username, request.user)
    post = info['author'].posts.get(pk=post_id)
    if request.user != post.author:
        context = {
            'post':post,
        }
        context.update(info)
        return render(request, 'post.html', context)
    if request.method != 'POST':
        context = {
            'form':PostForm(instance=post),
            'post':post,
        }
        context.update(info)
        return render(request, 'new.html', context)
    form = PostForm(request.POST, instance=post)
    if not form.is_valid():
        context = {
            'post':post,
        }
        context.update(info)
        return render(request, 'post.html', context)
    form.save()
    return redirect('post', username=f'{username}', post_id=f'{post_id}')
    

@login_required
def add_comment(request, username, post_id):
    post = get_object_or_404(Post, pk=post_id)
    author = get_object_or_404(User, username=username)
    if request.method != "POST":
        return redirect('post', post.author, post_id)
    form = CommentForm(request.POST)
    if not form.is_valid():
        return redirect('post', post.author, post_id)
    comment = form.save(commit=False)
    comment.post = post
    comment.author = author
    comment.save()
    return redirect('post', post.author, post_id)


@login_required
def follow_index(request):
    # информация о текущем пользователе доступна в переменной request.user
    user = User.objects.get(username=request.user)
    author = Follow.objects.values('author').filter(user=user)
    post = Post.objects.filter(author__in=author)
    paginator = Paginator(post, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    context = {
        'page': page,
        'paginator': paginator,
    }
    return render(request, "follow.html", context)


@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    user = get_object_or_404(User, username=request.user)
    if author == user:
        return redirect('index')

    if Follow.objects.filter(author=author, user=user).exists():
        return redirect('index')
    follow = Follow.objects.create(
        author=author,
        user=user
    )
    follow.save()
    return redirect('follow_index')


@login_required
def profile_unfollow(request, username):
    author = get_object_or_404(User, username=username)
    user = get_object_or_404(User, username=request.user)
    follow = user.follower.filter(author=author)
    follow.delete()
    return redirect('index')