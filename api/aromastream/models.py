from django.db import models
from uuid import uuid4
from datetime import datetime
from django.contrib.auth import get_user_model
from datetime import timedelta
from django.utils import timezone
from django.core.validators import FileExtensionValidator
def upload_file_path(instance, file_name):
    ext = file_name.split('.')[-1]
    date = datetime.now()
    year = date.year
    month = date.month
    day = date.day
    name = uuid4().hex
    file_path = '{}/{}/{}/{}.{}'.format(year, month, day, name, ext)
    return file_path
 
class Video(models.Model):
    title = models.CharField(max_length=400)
    description = models.TextField()
    file = models.FileField(upload_to=upload_file_path, validators=[FileExtensionValidator(allowed_extensions=['mp4'])])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    views = models.IntegerField(default=0, blank=True)
    
    def __str__(self):
        return self.title
    
class TimeStamp(models.Model):
    aroma_choices = [('A', 'A'), ('B', 'B'), ('C', 'C'), ('D', 'D')]
    video = models.ForeignKey(Video, on_delete=models.CASCADE)
    aroma = models.CharField(max_length=1, choices=aroma_choices)
    moment = models.TimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"id - {self.id}"

class ChangeRequest(models.Model):
    field_choices = [('password', 'password')]
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='recovery_records')
    field = models.CharField(max_length=100, choices=field_choices)
    new_value = models.TextField()
    confirm_code = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    @classmethod
    def cleanup_expired_user_change_requests(cls, user, field):
        cls.objects.filter(user=user, field=field, created_at__lt=timezone.now() - timedelta(hours=1)).delete()

    def __str__(self):
        return f"{self.user.username} - {self.field} - {self.created_at}"

