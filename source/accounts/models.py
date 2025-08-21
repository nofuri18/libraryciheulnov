from django.contrib.auth.models import User
from django.db import models
from django.conf import settings



class Activation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    code = models.CharField(max_length=20, unique=True)
    email = models.EmailField(blank=True)

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    # kita simpan path manual, bukan pakai ImageField
    profile_photo = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.user.username

