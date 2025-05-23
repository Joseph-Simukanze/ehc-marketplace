from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from django.contrib.auth import get_user_model

# Custom User model
class User(AbstractUser):
    is_seller = models.BooleanField(default=False)
    phone_number = models.CharField(max_length=15, blank=True)
    location = models.CharField(max_length=255, blank=True)
    subscription_end = models.DateTimeField(null=True, blank=True)

    def is_subscription_active(self):
        if self.subscription_end:
            return self.subscription_end > timezone.now()
        return False

# Get the custom User model
User = get_user_model()

# Subscription model linked to User
class Subscription(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='subscriptions')
    start_date = models.DateTimeField(auto_now_add=True)
    end_date = models.DateTimeField()
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2)
    payment_id = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return f"Subscription for {self.user.username} until {self.end_date.strftime('%Y-%m-%d %H:%M:%S')}"

    def is_active(self):
        return self.end_date > timezone.now()

    def duration_in_days(self):
        return (self.end_date - self.start_date).days

# Profile model linked one-to-one with User

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_picture = models.ImageField(upload_to='profiles/', blank=True, null=True)
    bio = models.TextField(blank=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"

    @property
    def image_url(self):
        if self.profile_picture and hasattr(self.profile_picture, 'url'):
            return self.profile_picture.url
        return '/static/images/default_profile.png'  # fallback image path
