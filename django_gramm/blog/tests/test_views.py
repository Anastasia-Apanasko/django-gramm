import pytest
from django.urls import reverse
from django.contrib.auth.models import User
from blog.models import Post, Comment, Like, Tag
from users.models import Subscription


@pytest.fixture
def client_logged(client):
    user = User.objects.create_user(username='test', password='123')
    client.login(username='test', password='123')
    return client, user


@pytest.mark.django_db
def test_feed_view_shows_followed_posts(client_logged):
    client, user = client_logged
    other = User.objects.create_user("v")

    Subscription.objects.create(follower=user, following=other)
    post = Post.objects.create(author=other, description="hello")

    response = client.get(reverse('blog:feed'))

    assert response.status_code == 200
    assert post in response.context['posts']


@pytest.mark.django_db
def test_post_detail_add_comment(client_logged):
    client, user = client_logged
    post = Post.objects.create(author=user, description="abc")

    response = client.post(
        reverse('blog:post_detail', kwargs={"post_pk": post.pk}),
        {"add_comment": "1", "text": "hi"}
    )
    assert response.status_code == 302
    assert post.comments.count() == 1


@pytest.mark.django_db
def test_post_detail_add_tag_by_author(client_logged):
    client, user = client_logged
    post = Post.objects.create(author=user, description="abc")

    client.post(
        reverse('blog:post_detail', kwargs={"post_pk": post.pk}),
        {"add_tag": 1, "name": "python"}
    )

    assert Tag.objects.filter(name="python").exists()
    assert post.tags.filter(name="python").exists()


@pytest.mark.django_db
def test_post_detail_like_post(client_logged):
    client, user = client_logged
    post = Post.objects.create(author=user, description="abc")

    client.post(reverse('blog:post_detail', kwargs={'post_pk': post.pk}), {"like_post": 1})

    assert Like.objects.filter(post=post, user=user, is_like=True).exists()


@pytest.mark.django_db
def test_post_detail_like_comment(client_logged):
    client, user = client_logged
    post = Post.objects.create(author=user, description="abc")
    comment = Comment.objects.create(user=user, post=post, text="lol")

    client.post(
        reverse('blog:post_detail', kwargs={'post_pk': post.pk}),
        {"like_comment": 1, "comment_id": comment.pk}
    )

    assert Like.objects.filter(comment=comment, user=user).exists()


@pytest.mark.django_db
def test_new_post_create(client_logged):
    client, user = client_logged

    response = client.post(
        reverse('blog:new_post'),
        {"description": "new post", "status": Post.Status.PUBLISHED}
    )

    assert response.status_code == 302
    assert Post.objects.filter(description="new post").exists()


@pytest.mark.django_db
def test_edit_post(client_logged):
    client, user = client_logged
    post = Post.objects.create(author=user, description="old text")

    client.post(
        reverse('blog:edit_post', kwargs={'post_pk': post.pk}),
        {"description": "updated", "status": Post.Status.PUBLISHED}
    )

    post.refresh_from_db()
    assert post.description == "updated"


@pytest.mark.django_db
def test_delete_post(client_logged):
    client, user = client_logged
    post = Post.objects.create(author=user, description="test")

    client.post(reverse('blog:delete_post', kwargs={'post_pk': post.pk}))

    assert not Post.objects.filter(pk=post.pk).exists()


@pytest.mark.django_db
def test_vote_like_post(client_logged):
    client, user = client_logged
    post = Post.objects.create(author=user, description="abc")

    response = client.get(reverse('blog:like_post', kwargs={"post_pk": post.pk}))
    assert response.status_code == 302
    assert Like.objects.filter(post=post, user=user, is_like=True).exists()


@pytest.mark.django_db
def test_vote_dislike_post(client_logged):
    client, user = client_logged
    post = Post.objects.create(author=user, description="abc")

    response = client.get(reverse('blog:dislike_post', kwargs={"post_pk": post.pk}))
    assert response.status_code == 302
    assert Like.objects.filter(post=post, user=user, is_like=False).exists()


@pytest.mark.django_db
def test_vote_like_comment(client_logged):
    client, user = client_logged
    post = Post.objects.create(author=user, description="abc")
    comment = Comment.objects.create(user=user, post=post, text="qwe")

    response = client.get(reverse('blog:like_comment', kwargs={"comment_pk": comment.pk}))
    assert response.status_code == 302
    assert Like.objects.filter(comment=comment, user=user, is_like=True).exists()


@pytest.mark.django_db
def test_vote_dislike_comment(client_logged):
    client, user = client_logged
    post = Post.objects.create(author=user, description="abc")
    comment = Comment.objects.create(user=user, post=post, text="qwe")

    response = client.get(reverse('blog:dislike_comment', kwargs={"comment_pk": comment.pk}))
    assert response.status_code == 302
    assert Like.objects.filter(comment=comment, user=user, is_like=False).exists()
