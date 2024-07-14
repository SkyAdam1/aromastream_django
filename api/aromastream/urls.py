from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainSlidingView)
from . import views


urlpatterns = [
    path('login', TokenObtainSlidingView.as_view(), name='login'),
    path('signup', views.UserCreateView.as_view(), name='login'),
    path('user', views.UserView.as_view(), name='user'),
    path('password_reset', views.UserPasswordUpdateView.as_view(), name='password_reset'),
    path('password_reset/confirm', views.UserPasswordUpdateConfirmView.as_view(), name='password_reset_confirm'),
    path('timestamps', views.TimeStampCreateView.as_view(), name='timestamp_create'),
    path('timestamps/<int:video_id>', views.TimeStampListView.as_view(), name='timestamp_list'),
    path('videos', views.VideoListView.as_view(), name='videos'),
    path('videos/<int:video_id>', views.VideoDetailView.as_view(), name='video_detail'),
    path('videos/popular', views.PopularVideoListView.as_view(), name='popular_videos'),
    path('videos/search', views.SearchVideoListView.as_view(), name='search_video'),
]