from django.db import models

# Create your models here.
from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    # Add any additional fields you need, e.g.:
    bio = models.TextField(blank=True)
    is_approved = models.BooleanField(default=False)


    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        Profile.objects.get_or_create(user=self)
        if not self.pk:  # If the user is being created for the first time
            if not self.is_superuser:  # If the user is not a superuser
                self.is_active = False  # Set is_active to False by default
        super().save(*args, **kwargs)


class Profile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.SET_NULL, null=True)



