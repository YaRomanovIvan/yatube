from django.urls import path

from . import views


urlpatterns = [
    path("follow/", views.follow_index, name="follow_index"),
    path('new/', views.new_post, name='new_post'),
    path('group/<slug:slug>/', views.group_posts, name='group_posts'),
    path("<str:username>/follow/", views.profile_follow, name="profile_follow"),
    path("<str:username>/unfollow/", views.profile_unfollow, name="profile_unfollow"),
    path("<username>/<int:post_id>/comment", views.add_comment, name="add_comment"),
    path("<int:comment_id>/<int:post_id>/edit_comment", views.edit_comment, name="edit_comment"),
    path("<int:comment_id>/<int:post_id>/delete_comment", views.delete_comment, name="delete_comment"),
    path('<str:username>/', views.profile, name='profile'),
    path('<str:username>/<int:post_id>/', views.post_view, name='post'),
    path(
        '<str:username>/<int:post_id>/edit/',
        views.post_edit,
        name='post_edit'
    ),
    path('', views.index, name='index'),
]
