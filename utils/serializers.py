import json
import re
from django.core.cache import cache
from django.http import JsonResponse, HttpRequest, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework import serializers

from utils.serializers import (
    CardInfoSerializer,
    TransferCreateSerializer,
    TransferConfirmSerializer,
    TransferCancelSerializer,
)
from utils.security import verify_signature 
from utils.ratelimit import hit_or_block 

CARD_RE = re.compile(r"^\d{16}$")
PHONE_RE = re.compile(r"^\+998\d{9}$")  # +998XXXXXXXXX
EXPIRY_RE = re.compile(r"^(0[1-9]|1[0-2])\/\d{2}$")  # MM/YY

class CardInfoSerializer(serializers.Serializer):
    card_number = serializers.CharField()
    expiry = serializers.CharField()

    def validate_card_number(self, v):
        v = re.sub(r"\D", "", v)
        if not CARD_RE.match(v):
            raise serializers.ValidationError("card_number must be 16 digits")
        return v

    def validate_expiry(self, v):
        if not EXPIRY_RE.match(v):
            raise serializers.ValidationError("expiry must be MM/YY")
        return v

class TransferCreateSerializer(serializers.Serializer):
    ext_id = serializers.CharField(max_length=50)
    sender_card_number = serializers.CharField()
    sender_card_expiry = serializers.CharField() # type: ignore
    receiver_card_number = serializers.CharField()
    sending_amount = serializers.IntegerField(min_value=1)
    currency = serializers.IntegerField()  # 643 or 840

    def _clean_card(self, v):
        v = re.sub(r"\D", "", v)
        if not CARD_RE.match(v):
            raise serializers.ValidationError("card_number must be 16 digits")
        return v

    def validate_sender_card_number(self, v): return self._clean_card(v)
    def validate_receiver_card_number(self, v): return self._clean_card(v)

    def validate_sender_card_expiry(self, v):
        if not EXPIRY_RE.match(v):
            raise serializers.ValidationError("expiry must be MM/YY")
        return v

    def validate_currency(self, v):
        if v not in (643, 840):
            raise serializers.ValidationError("currency must be 643 or 840")
        return v

class TransferConfirmSerializer(serializers.Serializer):
    ext_id = serializers.CharField(max_length=50)
    otp = serializers.CharField(min_length=6, max_length=6)

class TransferCancelSerializer(serializers.Serializer):
    ext_id = serializers.CharField(max_length=50)
