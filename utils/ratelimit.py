from django.core.cache import cache
import time
from typing import Tuple

def hit_or_block(request, key: str, limit: int, window_seconds: int) -> Tuple[bool, int]:
    """
    Возвращает (blocked, retry_after)
    """
    now = int(time.time())
    window_key = f"rl:{key}:{now // window_seconds}"
    count = cache.get(window_key, 0) + 1
    cache.set(window_key, count, timeout=window_seconds)
    if count > limit:
        # Сколько осталось до конца окна
        retry_after = window_seconds - (now % window_seconds)
        return True, retry_after
    return False, 0
