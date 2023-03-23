# user_management/models.py
from django.contrib.auth.models import User
from django.db import models

class Image(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='images/')
    title=models.CharField(max_length=50)
    description=models.CharField(max_length=500)
    upload_date = models.DateTimeField(auto_now_add=True)
    grid_position = models.PositiveIntegerField()

    class Meta:
        ordering = ['-upload_date']
        unique_together = ('user', 'grid_position')
