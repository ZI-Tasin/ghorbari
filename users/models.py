from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):

    USER_TYPE_CHOICES = (
        ('STUDENT', 'BracU Student'),
        ('LANDLORD', 'Landlord'),
        )

    bio = models.TextField(default = '', blank = True)
    profile_picture = models.ImageField(upload_to = 'profile_pics/', null = True, blank = True)
    email = models.EmailField(unique = True)
    verified = models.BooleanField(default = False)
    user_type = models.CharField(max_length = 8, choices = USER_TYPE_CHOICES)

    def __str__(self):
        return self.username

