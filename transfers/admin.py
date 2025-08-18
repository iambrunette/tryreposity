from django.contrib import admin
from .models import Transfer

@admin.register(Transfer)
class TransferAdmin(admin.ModelAdmin):
    list_display = ('ext_id', 'sender_card_number', 'receiver_card_number', 'sending_amount', 'currency', 'state', 'otp', 'created_at')
