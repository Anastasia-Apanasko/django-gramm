import pytest
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.test import override_settings
from users.models import Profile, Subscription
from blog.models import Post
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from users.tokens import account_activation_token

User = get_user_model()


@pytest.fixture
def logged(client):
    user = User.objects.create_user(username="john", password="123")
    Profile.objects.create(user=user)
    client.login(username="john", password="123")
    return client, user


@pytest.mark.django_db
def test_signup_sends_email(client, mailoutbox):
    response = client.post(
        reverse("users:signup"),
        {
            "username": "newuser",
            "email": "test@example.com",
            "password1": "C0mpl3xP@ssword!2025",
            "password2": "C0mpl3xP@ssword!2025",
        },
    )

    assert response.status_code == 200
    assert len(mailoutbox) == 1
    assert User.objects.filter(username="newuser").exists()
    assert not User.objects.get(username="newuser").is_active


@pytest.mark.django_db
@override_settings(AUTHENTICATION_BACKENDS=['django.contrib.auth.backends.ModelBackend'])
def test_activate_user(client):
    User = get_user_model()
    user = User.objects.create_user("inactive", password="123", is_active=False)
    user.backend = 'django.contrib.auth.backends.ModelBackend'

    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = account_activation_token.make_token(user)

    url = reverse("users:activate", kwargs={"uidb64": uid, "token": token})
    response = client.get(url)

    user.refresh_from_db()
    assert response.status_code == 302
    assert user.is_active is True


@pytest.mark.django_db
def test_edit_profile(logged):
    client, user = logged

    response = client.post(
        reverse("users:edit"),
        {"first_name": "John", "bio": "New bio"}
    )

    user.refresh_from_db()
    assert response.status_code == 302
    assert user.first_name == "John"
    assert user.profile.bio == "New bio"


@pytest.mark.django_db
def test_profile_view_pagination(logged):
    client, user = logged

    for i in range(15):
        Post.objects.create(
            author=user,
            description=f"Post {i}",
            status=Post.Status.PUBLISHED,
        )

    response = client.get(reverse("users:profile", kwargs={"username": user.username}))

    assert response.status_code == 200
    assert response.context["posts"].paginator.num_pages == 2


@pytest.mark.django_db
def test_follow(logged):
    client, user = logged
    target = User.objects.create_user("target")
    Profile.objects.create(user=target)

    response = client.get(reverse("users:follow", kwargs={"username": "target"}))

    assert response.status_code == 302
    assert Subscription.objects.filter(follower=user, following=target).exists()


@pytest.mark.django_db
def test_unfollow(logged):
    client, user = logged
    target = User.objects.create_user("target")
    Profile.objects.create(user=target)

    Subscription.objects.create(follower=user, following=target)

    response = client.get(reverse("users:unfollow", kwargs={"username": "target"}))

    assert response.status_code == 302
    assert not Subscription.objects.filter(follower=user, following=target).exists()


@pytest.mark.django_db
def test_followers_list(logged):
    client, user = logged
    target = User.objects.create_user("target")
    Profile.objects.create(user=target)

    Subscription.objects.create(follower=target, following=user)

    response = client.get(reverse("users:followers_list", kwargs={"username": user.username}))

    assert response.status_code == 200
    assert target in response.context["followers"]


@pytest.mark.django_db
def test_following_list(logged):
    client, user = logged
    target = User.objects.create_user("target")
    Profile.objects.create(user=target)

    Subscription.objects.create(follower=user, following=target)

    response = client.get(reverse("users:following_list", kwargs={"username": user.username}))

    assert response.status_code == 200
    assert target in response.context["following"]
