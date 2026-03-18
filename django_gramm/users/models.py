from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model

User = get_user_model()


class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL,
                                on_delete=models.CASCADE)
    date_of_birth = models.DateField(blank=True, null=True)
    photo = models.ImageField(upload_to='users/%Y/%m/%d/',
                              blank=True, default='avatars/default_avatar.jpg')
    bio =  models.CharField(max_length=200, blank=True, null=True)

    def __str__(self):
        return f'Profile of {self.user.username}'


class SubscriptionManager(models.Manager):
    def followers_of(self, user):
        return User.objects.filter(following_set__following=user)

    def following_of(self, user):
        return User.objects.filter(follower_set__follower=user)

    def count_followers(self, user):
        return self.followers_of(user).count()

    def count_following(self, user):
        return self.following_of(user).count()


class Subscription(models.Model):
    follower = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='following_set'
    )
    following = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='follower_set'
    )

    objects = models.Manager()
    subscriptions = SubscriptionManager()

    class Meta:
        unique_together = ('follower', 'following')

    def clean(self):
        if self.follower == self.following:
            raise ValidationError("You can't subscribe to yourself.")
        super().clean()

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
