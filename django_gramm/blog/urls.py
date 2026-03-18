from django.urls import path
from . import views

app_name = "blog"

urlpatterns = [
    path("", views.feed, name="feed"),
    path('new_post/', views.new_post, name='new_post'),
    path("<int:post_pk>/", views.post_detail, name="post_detail"),
    path("<int:post_pk>/edit/", views.edit_post, name="edit_post"),
    path("<int:post_pk>/delete/", views.delete_post, name="delete_post"),
    path('drafts/', views.drafts, name='drafts'),
    path('vote/', views.vote, name='vote'),
    path("<int:post_pk>/add_comment/", views.add_comment, name="add_comment"),

]