from datetime import datetime, timedelta, timezone

import httpx
from jose import JWTError, jwt
from passlib.context import CryptContext

from core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_truncated_password(plain: str) -> str:
    # Bcrypt strictly limits inputs to 72 *bytes*, not characters.
    # We must encode, slice, and decode safely.
    return plain.encode("utf-8")[:72].decode("utf-8", "ignore")


def hash_password(plain: str) -> str:
    return pwd_context.hash(get_truncated_password(plain))


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(get_truncated_password(plain), hashed)


def create_access_token(user_id: int) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.jwt_expire)
    payload = {"sub": str(user_id), "exp": expire}
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def decode_access_token(token: str) -> int | None:
    try:
        payload = jwt.decode(
            token, settings.jwt_secret, algorithms=[settings.jwt_algorithm]
        )
        return int(payload["sub"])
    except JWTError, KeyError, ValueError:
        return None


def google_auth_url(state: str = "") -> str:
    params = {
        "client_id": settings.google_client_id,
        "redirect_uri": settings.google_redirect_uri,
        "response_type": "code",
        "scope": "openid email profile",
        "access_type": "offline",
        "state": state,
    }
    query = "&".join(f"{k}={v}" for k, v in params.items())
    return f"{settings.google_auth_url}?{query}"


async def exchange_google_code(code: str) -> dict:
    async with httpx.AsyncClient() as client:
        token_resp = await client.post(
            settings.google_token_url,
            data={
                "code": code,
                "client_id": settings.google_client_id,
                "client_secret": settings.google_client_secret,
                "redirect_uri": settings.google_redirect_uri,
                "grant_type": "authorization_code",
            },
        )
        token_resp.raise_for_status()
        tokens = token_resp.json()

        user_resp = await client.get(
            settings.google_user_url,
            headers={"Authorization": f"Bearer {tokens['access_token']}"},
        )
        user_resp.raise_for_status()
        profile = user_resp.json()

    return {
        "email": profile.get("email"),
        "name": profile.get("name", ""),
        "google_id": profile.get("sub"),
        "picture": profile.get("picture"),
    }
