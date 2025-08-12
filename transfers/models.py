from django.db import models
from django.utils import timezone

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
    created_at = models.DateTimeField(default=timezone.now)
    confirmed_at = models.DateTimeField(null=True, blank=True)
    cancelled_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Error(models.Model):
    code = models.IntegerField(unique=True)
    en = models.CharField(max_length=255)
    ru = models.CharField(max_length=255)
    uz = models.CharField(max_length=255)
