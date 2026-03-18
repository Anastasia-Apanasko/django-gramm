from django.contrib import admin
from .models import Profile, Subscription

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'date_of_birth', 'photo')
    search_fields = ('user__username', 'bio')

@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('id', 'follower', 'following')
    search_fields = ('follower__username', 'following__username')
