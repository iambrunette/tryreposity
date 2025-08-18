from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    telegram_id = models.CharField(max_length=30, blank=True, null=True)

class Transfer(models.Model):
    CURRENCY_CHOICES = [
        (643, 'RUB'),
        (840, 'USD'),
    ]
    STATE_CHOICES = [
        ('created', 'Created'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, default="PENDING")
    ext_id = models.CharField(max_length=50, unique=True)
    sender_card_number = models.CharField(max_length=16)
    receiver_card_number = models.CharField(max_length=16)
    sender_card_expiry = models.CharField(max_length=5)  # MM/YY
    sender_phone = models.CharField(max_length=20, null=True, blank=True)
    receiver_phone = models.CharField(max_length=20, null=True, blank=True)
    sending_amount = models.DecimalField(max_digits=12, decimal_places=2)
    receiving_amount = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    currency = models.IntegerField(choices=CURRENCY_CHOICES)
    state = models.CharField(max_length=10, choices=STATE_CHOICES, default='created')
    try_count = models.IntegerField(default=0)
    otp = models.CharField(max_length=6, null=True, blank=True)
    confirmed_at = models.DateTimeField(null=True, blank=True)
    cancelled_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)
class Error(models.Model):
    code = models.IntegerField(unique=True)
    en = models.CharField(max_length=255)
    ru = models.CharField(max_length=255)
    uz = models.CharField(max_length=255)

class Card(models.Model):
    card_number = models.CharField(max_length=16, unique=True)
    expiry_date = models.DateField()
    phone = models.CharField(max_length=20, null=True, blank=True)

    def __str__(self):
        return f"{self.card_number} ({self.expiry_date})"
    
