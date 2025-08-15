import hmac, hashlib, os
from typing import Tuple, Optional
from django.contrib.auth.models import User

# Вариант 1: один общий секрет через .env (X-API-Sign)
API_SHARED_SECRET = os.getenv("API_SHARED_SECRET")

# Вариант 2: пер-пользовательский секрет из таблицы (X-API-User + X-API-Sign)
# Создай модель при желании (например, transfers.models.APIUser), тут показан пример с Django User + profile.secret

def _hmac_sha256(payload: bytes, secret: str) -> str:
    return hmac.new(secret.encode(), payload, hashlib.sha256).hexdigest()

def verify_signature(request, body: bytes) -> Tuple[bool, Optional[str]]:
    sign = request.headers.get("X-API-Sign")
    if not sign:
        # Если хочешь сначала “мягкий режим”, верни (True, None)
        return False, "Missing X-API-Sign header"

    # Если используешь user-based секрет:
    api_user = request.headers.get("X-API-User")
    if api_user:
        # пример lookup — адаптируй под свою модель
        try:
            user = User.objects.get(username=api_user)
            # допустим, secret лежит в user.last_name (НЕ делай так в реале; сделай профиль/отдельную модель)
            secret = user.last_name
        except User.DoesNotExist:
            return False, "Unknown API user"
    else:
        secret = API_SHARED_SECRET

    if not secret:
        return False, "Server HMAC secret is not configured"

    expected = _hmac_sha256(body, secret)
    if not hmac.compare_digest(expected, sign):
        return False, "Invalid signature"
    return True, None
