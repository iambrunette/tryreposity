import logging
from functools import wraps

logger = logging.getLogger(__name__)

def log_request_response(func):
    """
    Логирует входные параметры функции и её результат.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        logger.info(f"Calling {func.__name__} with args={args}, kwargs={kwargs}")
        result = func(*args, **kwargs)
        logger.info(f"{func.__name__} returned {result}")
        return result
    return wrapper
