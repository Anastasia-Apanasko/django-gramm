from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.http import JsonResponse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from .forms import PostForm, CommentForm, TagForm
from users.models import Subscription
from .models import Post, Image, Like, Comment, Tag


@login_required
def feed(request):
    following_users = Subscription.subscriptions.following_of(request.user)
    posts = Post.objects.filter(
        (Q(author__in=following_users) | Q(author=request.user)) &
        Q(status=Post.Status.PUBLISHED)
    )
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    try:
        posts = paginator.page(page_number)
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)

    return render(request, 'blog/feed.html', {'posts': posts})


@login_required
def post_detail(request, post_pk):
    post = get_object_or_404(Post, pk=post_pk)
    comments = post.comments.all()
    tags = post.tags.all()
    user = request.user

    comment_form = CommentForm()
    tag_form = TagForm()

    if request.method == 'POST':
        if 'add_comment' in request.POST:
            comment_form = CommentForm(request.POST)
            if comment_form.is_valid():
                comment = comment_form.save(commit=False)
                comment.user = user
                comment.post = post
                comment.save()
                messages.success(request, "Comment added.")
                return redirect('blog:post_detail', post_pk=post.pk)
            else:
                messages.error(request, "Invalid comment form.")


        elif 'add_tag' in request.POST:
            if user != post.author:
                messages.error(request, "Only the author can add tags.")
                return redirect('blog:post_detail', post_pk=post.pk)
            tag_name = request.POST.get('name', '').strip()
            if not tag_name:
                messages.error(request, "Tag cannot be empty.")
                return redirect('blog:post_detail', post_pk=post.pk)
            tag, created = Tag.objects.get_or_create(name=tag_name)
            post.tags.add(tag)
            messages.success(request, f"Tag '{tag_name}' added.")
            return redirect('blog:post_detail', post_pk=post.pk)

        elif 'like_post' in request.POST:
            Like.vote.toggle(user=user, post=post, is_like=True)
            return redirect('blog:post_detail', post_pk=post.pk)
        elif 'dislike_post' in request.POST:
            Like.vote.toggle(user=user, post=post, is_like=False)
            return redirect('blog:post_detail', post_pk=post.pk)

        elif 'like_comment' in request.POST or 'dislike_comment' in request.POST:
            comment_id = request.POST.get('comment_id')
            comment = get_object_or_404(Comment, id=comment_id)
            is_like = 'like_comment' in request.POST
            Like.vote.toggle(user=user, comment=comment, is_like=is_like)
            return redirect('blog:post_detail', post_pk=post.pk)

    context = {
        'post': post,
        'comments': comments,
        'tags': tags,
        'comment_form': comment_form,
        'tag_form': tag_form,
        'user': user,
    }
    return render(request, 'blog/post/post_detail.html', context)


@login_required
def new_post(request):
    if request.method == 'POST':
        form = PostForm(request.POST)
        tag_names = request.POST.get('tags', '').split(',')  # теги через запятую
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()

            for image_file in request.FILES.getlist('images'):
                Image.objects.create(post=post, owner=request.user, image=image_file)

            for tag_name in tag_names:
                tag_name = tag_name.strip()
                if tag_name:
                    tag, _ = Tag.objects.get_or_create(name=tag_name)
                    post.tags.add(tag)

            messages.success(request, "Post created successfully.")
            if post.status == Post.Status.DRAFT:
                return redirect('blog:drafts')
            return redirect('users:profile', username=request.user.username)
        else:
            messages.error(request, "Invalid post form.")
    else:
        form = PostForm()

    return render(request, 'blog/post/new_post.html', {'form': form})


@login_required
def edit_post(request, post_pk):
    post = get_object_or_404(Post, pk=post_pk, author=request.user)

    if request.method == 'POST':
        form = PostForm(instance=post, data=request.POST)
        tag_names = request.POST.get('tags', '').split(',')

        if form.is_valid():
            form.save()

            delete_ids = request.POST.getlist('delete_images')
            if delete_ids:
                post.images.filter(id__in=delete_ids).delete()

            for image_file in request.FILES.getlist('images'):
                Image.objects.create(post=post, owner=request.user, image=image_file)

            post.tags.clear()
            for tag_name in tag_names:
                tag_name = tag_name.strip()
                if tag_name:
                    tag, _ = Tag.objects.get_or_create(name=tag_name)
                    post.tags.add(tag)

            messages.success(request, "Post updated successfully.")
            return redirect('users:profile', username=request.user.username)
        else:
            messages.error(request, "Invalid post form.")
    else:
        form = PostForm(instance=post)
        existing_tags = ', '.join([t.name for t in post.tags.all()])

    context = {
        'form': form,
        'post': post,
        'existing_images': post.images.all(),
        'existing_tags': existing_tags if request.method == 'GET' else '',
    }
    return render(request, 'blog/post/edit_post.html', context)


@login_required
def delete_post(request, post_pk):
    post = get_object_or_404(Post, pk=post_pk, author=request.user)

    if request.method == 'POST':
        post.delete()
        return redirect('users:profile', username=request.user.username)

    context = {'post': post}
    return render(request, 'blog/post/delete_post.html', context)

@login_required
def drafts(request):
    drafts = Post.objects.filter(author=request.user, status=Post.Status.DRAFT)
    return render(request, 'blog/post/drafts.html', {'drafts': drafts})


@login_required
@require_POST
def vote(request):
    post_pk = request.POST.get('post_pk')
    comment_pk = request.POST.get('comment_pk')
    is_like = request.POST.get('is_like', 'true') == 'true'

    if post_pk:
        post = get_object_or_404(Post, pk=post_pk)
        Like.vote.toggle(request.user, post=post, is_like=is_like)

        likes_count = post.likes_count()
        dislikes_count = post.dislikes_count()

        return JsonResponse({
            'status': 'ok',
            'type': 'post',
            'id': post_pk,
            'likes_count': likes_count,
            'dislikes_count': dislikes_count,
            'user_action': 'like' if is_like else 'dislike',
        })

    elif comment_pk:
        comment = get_object_or_404(Comment, pk=comment_pk)
        Like.vote.toggle(request.user, comment=comment, is_like=is_like)

        likes_count = comment.likes_count()
        dislikes_count = comment.dislikes_count()

        return JsonResponse({
            'status': 'ok',
            'type': 'comment',
            'id': comment_pk,
            'likes_count': likes_count,
            'dislikes_count': dislikes_count,
            'user_action': 'like' if is_like else 'dislike',
        })

    return JsonResponse({'status': 'error', 'message': 'No target provided'})


@login_required
@require_POST
def add_comment(request, post_pk):
    text = request.POST.get('content', '').strip()
    if not text:
        return JsonResponse({'status': 'error', 'message': 'Empty comment'})

    post = get_object_or_404(Post, pk=post_pk)
    comment = Comment.objects.create(user=request.user, post=post, text=text)

    return JsonResponse({
        'status': 'ok',
        'id': comment.pk,
        'author': comment.user.username,
        'content': comment.text,
        'created_at': comment.created.strftime('%Y-%m-%d %H:%M'),
    })
