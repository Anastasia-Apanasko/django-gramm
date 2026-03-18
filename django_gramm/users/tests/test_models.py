import pytest
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from users.models import Profile, Subscription

User = get_user_model()


@pytest.mark.django_db
def test_profile_created_and_str():
    user = User.objects.create_user(username="test", password="123")
    profile = Profile.objects.create(user=user, bio="Hello")

    assert str(profile) == "Profile of test"
    assert profile.bio == "Hello"


@pytest.mark.django_db
def test_subscription_manager_followers_and_following():
    u1 = User.objects.create_user("u1")
    u2 = User.objects.create_user("u2")
    u3 = User.objects.create_user("u3")

    Subscription.objects.create(follower=u1, following=u2)
    Subscription.objects.create(follower=u3, following=u2)

    assert set(Subscription.subscriptions.followers_of(u2)) == {u1, u3}
    assert Subscription.subscriptions.count_followers(u2) == 2

    assert set(Subscription.subscriptions.following_of(u1)) == {u2}
    assert Subscription.subscriptions.count_following(u1) == 1


@pytest.mark.django_db
def test_subscription_cannot_follow_self():
    u = User.objects.create_user("john")

    sub = Subscription(follower=u, following=u)

    with pytest.raises(ValidationError):
        sub.full_clean()
