from fastapi import Request
from slowapi import Limiter
from slowapi.util import get_remote_address

from core.config import settings


def get_user_id(request: Request) -> str:
    """
    Rate limit by user ID if authenticated (set by auth dependency),
    otherwise fall back to IP address.
    """
    user = getattr(request.state, "user", None)
    if user:
        return str(user.id)
    return get_remote_address(request)


# Limiter for unauthenticated endpoints (Auth) using IP
limiter = Limiter(key_func=get_remote_address, storage_uri=settings.redis_url)

# Limiter for authenticated endpoints (LLM) using User ID
user_limiter = Limiter(key_func=get_user_id, storage_uri=settings.redis_url)
