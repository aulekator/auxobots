from django.db import models
from django.utils import timezone

class Meeting(models.Model):
    selected_time = models.CharField(max_length=100)
    created_at = models.DateTimeField(default=timezone.now)
    user_email = models.EmailField(blank=True, null=True)  # Optional: collect user email

    def __str__(self):
        return f'Meeting at {self.selected_time}'