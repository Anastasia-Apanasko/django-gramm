from django.contrib import admin
from .models import Post, Image, Comment, Tag, Like

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('id', 'author', 'description_short', 'status', 'publish', 'created')
    list_filter = ('status', 'publish', 'author')
    search_fields = ('description', 'author__username')
    date_hierarchy = 'publish'
    ordering = ('-publish',)

    def description_short(self, obj):
        return obj.description[:50]
    description_short.short_description = 'Description'

@admin.register(Image)
class ImageAdmin(admin.ModelAdmin):
    list_display = ('id', 'owner', 'post', 'image')
    search_fields = ('owner__username', 'post__description')

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'post', 'short_text', 'created')
    search_fields = ('user__username', 'post__description', 'text')
    list_filter = ('created',)

    def short_text(self, obj):
        return obj.text[:50]
    short_text.short_description = 'Comment'

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)

@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'is_like', 'post', 'comment')
    list_filter = ('is_like',)
    search_fields = ('user__username', 'post__description', 'comment__text')
