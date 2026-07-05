import secrets
from typing import Annotated

from fastapi import APIRouter, Cookie, Depends, HTTPException, status
from fastapi.responses import RedirectResponse, Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from core.config import settings
from core.database import get_session
from core.security import (
    create_access_token,
    exchange_google_code,
    google_auth_url,
    hash_password,
    verify_password,
)
from models import User
from schemas.schema import LoginBody, ProfileOut, ProfileUpdate, SignupBody
from services.resume_service import CurrentUser

router = APIRouter(prefix="/auth", tags=["auth"])

DB = Annotated[AsyncSession, Depends(get_session)]


@router.post("/signup", status_code=status.HTTP_201_CREATED)
async def signup(body: SignupBody, db: DB):
    existing = await db.execute(
        select(User).where(
            (User.email == body.email) | (User.username == body.username)
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status.HTTP_409_CONFLICT, "Email or username already taken")

    user = User(
        username=body.username,
        name=body.name,
        email=body.email,
        hashed_password=hash_password(body.password),
    )
    db.add(user)
    await db.flush()
    await db.refresh(user)

    return {"access_token": create_access_token(user.id), "token_type": "bearer"}  # type: ignore


@router.post("/login")
async def login(body: LoginBody, db: DB):
    result = await db.execute(select(User).where(User.email == body.email_or_username))
    user = result.scalar_one_or_none()

    if not user or not verify_password(body.password, user.hashed_password):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid email or password")

    return {"access_token": create_access_token(user.id), "token_type": "bearer"}  # type: ignore


@router.post("/logout")
async def logout():
    return {"message": "Logged out"}


@router.get("/google")
async def google_login(response: Response):
    """Redirect browser to Google consent screen with a CSRF-protecting state cookie."""
    state = secrets.token_urlsafe(32)
    redirect = RedirectResponse(google_auth_url(state=state))
    # HttpOnly + SameSite=Lax keeps the state out of JS and prevents CSRF
    redirect.set_cookie(
        key="oauth_state",
        value=state,
        httponly=True,
        samesite="lax",
        max_age=300,  # 5 minutes — enough time to complete the OAuth flow
    )
    return redirect


@router.get("/google/callback")
async def google_callback(
    code: str,
    state: str,
    db: DB,
    oauth_state: str | None = Cookie(default=None),
):
    """
    Google redirects here with ?code=...&state=...
    Validate the CSRF state before exchanging the code.
    """
    # --- CSRF validation ---
    if not oauth_state or not secrets.compare_digest(state, oauth_state):
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST, "Invalid OAuth state — possible CSRF attempt"
        )
    try:
        profile = await exchange_google_code(code)
    except Exception:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST, "Failed to exchange Google code"
        )

    result = await db.execute(select(User).where(User.email == profile["email"]))
    user = result.scalar_one_or_none()

    is_new = False
    if not user:
        is_new = True
        user = User(
            username=profile["email"].split("@")[0],
            name=profile["name"],
            email=profile["email"],
            # Hash a random credential so hashed_password is never empty.
            # Google-authed users cannot log in via password; this is intentional.
            hashed_password=hash_password(secrets.token_hex(32)),
        )
        db.add(user)
        await db.flush()
        await db.refresh(user)

    token = create_access_token(user.id)  # type: ignore
    new_str = "true" if is_new else "false"

    return RedirectResponse(
        url=f"{settings.frontend_url}/login?token={token}&new={new_str}"
    )


@router.get("/profile", response_model=ProfileOut)
async def get_profile(user: CurrentUser):
    return user


@router.put("/profile", response_model=ProfileOut)
async def update_profile(body: ProfileUpdate, user: CurrentUser, db: DB):
    user.name = body.name
    user.email = body.email
    user.github = body.github
    user.linkedin = body.linkedin
    user.website = body.website
    user.location = body.location
    user.phone = body.phone
    user.raw_resume = body.raw_resume

    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user
