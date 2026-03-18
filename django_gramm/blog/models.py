from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User


class PublishedManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset() \
            .filter(status=Post.Status.PUBLISHED)


class Post(models.Model):
    class Status(models.TextChoices):
        DRAFT = 'DF', 'Draft'
        PUBLISHED = 'PB', 'Published'

    description = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    publish = models.DateTimeField(default=timezone.now)
    updated = models.DateTimeField(auto_now=True)
    author = models.ForeignKey(User,
                               on_delete=models.CASCADE,
                               related_name='posts')
    status = models.CharField(max_length=2,
                              choices=Status.choices,
                              default=Status.DRAFT)
    objects = models.Manager()
    published = PublishedManager()

    class Meta:
        ordering = ['-publish']

    def __str__(self):
        return f'{self.author.username} - {self.description[:15]}'

    def likes_count(self):
        return self.likes.filter(is_like=True).count()

    def dislikes_count(self):
        return self.likes.filter(is_like=False).count()


class Image(models.Model):
    image = models.ImageField(upload_to='post_images/')
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='images')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='images')


class Tag(models.Model):
    name = models.CharField(max_length=150, unique=True)
    posts = models.ManyToManyField(Post, related_name='tags', blank=True)

    def __str__(self):
        return self.name


class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    text = models.TextField()
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created']

    def __str__(self):
        return f'Comment by {self.user.username} on Post {self.post.pk}'

    def likes_count(self):
        return self.likes.filter(is_like=True).count()

    def dislikes_count(self):
        return self.likes.filter(is_like=False).count()


class LikeManager(models.Manager):
    def toggle(self, user, post=None, comment=None, is_like=True):
        like = self.filter(
            user=user,
            post=post,
            comment=comment
        ).first()

        if like and like.is_like == is_like:
            like.delete()
            return None

        if like:
            like.delete()

        return self.create(
            user=user,
            post=post,
            comment=comment,
            is_like=is_like
        )


class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='likes')
    is_like = models.BooleanField(default=True)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='likes', null=True, blank=True)
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name='likes', null=True, blank=True)

    objects = models.Manager()
    vote = LikeManager()

    class Meta:
        unique_together = [
            ('user', 'post'),
            ('user', 'comment')
        ]
