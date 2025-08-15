import os
from typing import Optional
from cryptography.fernet import Fernet, InvalidToken

_FERNET: Optional[Fernet] = None

def get_cipher() -> Fernet:
    global _FERNET
    if _FERNET is not None:
        return _FERNET
    key = os.getenv("ENCRYPTION_KEY")
    if not key:
        # В dev можно сгенерировать (раскомментируй при необходимости):
        # key = Fernet.generate_key().decode()
        # print("[crypto] ENCRYPTION_KEY was missing, generated DEV key (DO NOT USE IN PROD):", key)
        # os.environ["ENCRYPTION_KEY"] = key
        raise RuntimeError("ENCRYPTION_KEY is not set")
    _FERNET = Fernet(key.encode() if not key.startswith("gAAAA") else key) if isinstance(key, str) else Fernet(key)
    # Примечание: обычный ключ — base64 строка длиной 44, не начинается с gAAAA
    if isinstance(_FERNET, str):  # страховка
        _FERNET = Fernet(key.encode())
    return _FERNET

def encrypt_card(card: str) -> str:
    cipher = get_cipher()
    return cipher.encrypt(card.encode()).decode()

def decrypt_card(enc: str) -> str:
    cipher = get_cipher()
    try:
        return cipher.decrypt(enc.encode()).decode()
    except InvalidToken:
        raise ValueError("Invalid encryption token")

def mask_card(card: str) -> str:
    digits = "".join(ch for ch in card if ch.isdigit())
    if len(digits) < 6:
        return "******"
    return f"{digits[:6]}******{digits[-4:]}"
