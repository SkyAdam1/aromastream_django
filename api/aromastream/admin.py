from django.contrib import admin
from .models import Video, TimeStamp, ChangeRequest
from django.contrib.auth import get_user_model

User = get_user_model()

@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'created_at', 'updated_at', 'views')
    search_fields = ('title', 'description')
    list_filter = ('created_at', 'updated_at')

@admin.register(TimeStamp)
class TimeStampAdmin(admin.ModelAdmin):
    list_display = ('id', 'get_video_title', 'aroma', 'moment')
    search_fields = ('video__title', 'aroma')
    list_filter = ('aroma',)

    def get_video_title(self, obj):
        return obj.video.title
    get_video_title.admin_order_field = 'video' 
    get_video_title.short_description = 'Video Title' 

@admin.register(ChangeRequest)
class ChangeRequestAdmin(admin.ModelAdmin):
    list_display = ('id', 'get_user_username', 'field', 'created_at')
    search_fields = ('user__username', 'field')
    list_filter = ('created_at',)

    def get_user_username(self, obj):
        return obj.user.username
    get_user_username.admin_order_field = 'user'  # Allows column to be sortable
    get_user_username.short_description = 'User'