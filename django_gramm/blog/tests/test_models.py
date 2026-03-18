import pytest
from django.contrib.auth.models import User
from blog.models import Post, Comment, Like


@pytest.mark.django_db
def test_published_manager():
    user = User.objects.create_user(username='u', password='1')
    post1 = Post.objects.create(author=user, description='text1', status=Post.Status.DRAFT)
    post2 = Post.objects.create(author=user, description='text2', status=Post.Status.PUBLISHED)

    published = Post.published.all()

    assert post2 in published
    assert post1 not in published


@pytest.mark.django_db
def test_post_like_dislike_counts():
    user = User.objects.create_user(username='u', password='1')
    post = Post.objects.create(author=user, description='abc', status=Post.Status.PUBLISHED)

    Like.objects.create(user=user, post=post, is_like=True)
    Like.objects.create(user=User.objects.create_user("u2"), post=post, is_like=False)

    assert post.likes_count() == 1
    assert post.dislikes_count() == 1


@pytest.mark.django_db
def test_comment_like_dislike_counts():
    user = User.objects.create_user(username='u', password='1')
    post = Post.objects.create(author=user, description='abc')
    comment = Comment.objects.create(user=user, post=post, text='hi')

    Like.objects.create(user=user, comment=comment, is_like=True)

    assert comment.likes_count() == 1
    assert comment.dislikes_count() == 0


@pytest.mark.django_db
def test_like_toggle_for_post():
    user = User.objects.create_user("u")
    post = Post.objects.create(author=user, description="test")

    like = Like.vote.toggle(user, post=post, is_like=True)
    assert like.is_like is True
    assert Like.objects.filter(user=user, post=post).count() == 1

    Like.vote.toggle(user, post=post, is_like=True)
    assert Like.objects.filter(user=user, post=post).count() == 0

    dislike = Like.vote.toggle(user, post=post, is_like=False)
    assert dislike.is_like is False
    assert Like.objects.filter(user=user, post=post).count() == 1

    new_like = Like.vote.toggle(user, post=post, is_like=True)
    assert new_like.is_like is True
    assert Like.objects.filter(user=user, post=post).count() == 1
