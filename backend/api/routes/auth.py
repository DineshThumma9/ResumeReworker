from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from core.security import (
    create_access_token,
    exchange_google_code,
    google_auth_url,
    hash_password,
    verify_password,
)
from core.config import settings
from core.database import get_session
from models import User
from schemas.schema import LoginBody, SignupBody, ProfileUpdate, ProfileOut
from services.resume_service import CurrentUser

router = APIRouter(prefix="/auth", tags=["auth"])

DB = Annotated[AsyncSession, Depends(get_session)]

@router.post("/signup", status_code=status.HTTP_201_CREATED)
async def signup(body: SignupBody, db: DB):
    existing = await db.execute(
        select(User).where((User.email == body.email) | (User.username == body.username))
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

    return {"access_token": create_access_token(user.id), "token_type": "bearer"}


@router.post("/login")
async def login(body: LoginBody, db: DB):
    result = await db.execute(select(User).where(User.email == body.email_or_username))
    user = result.scalar_one_or_none()

    if not user or not verify_password(body.password, user.hashed_password):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid email or password")

    return {"access_token": create_access_token(user.id), "token_type": "bearer"}


@router.post("/logout")
async def logout():
    return {"message": "Logged out"}


@router.get("/google")
async def google_login():
    """Redirect browser to Google consent screen."""
    return RedirectResponse(google_auth_url())


@router.get("/google/callback")
async def google_callback(code: str, db: DB):
    """
    Google redirects here with ?code=...
    We exchange it for user info, create/find the user, return a JWT.
    """
    try:
        profile = await exchange_google_code(code)
    except Exception:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Failed to exchange Google code")

    result = await db.execute(select(User).where(User.email == profile["email"]))
    user = result.scalar_one_or_none()

    is_new = False
    if not user:
        is_new = True
        user = User(
            username=profile["email"].split("@")[0],
            name=profile["name"],
            email=profile["email"],
            hashed_password="",  
        )
        db.add(user)
        await db.flush()
        await db.refresh(user)

    token = create_access_token(user.id)
    new_str = "true" if is_new else "false"

    return RedirectResponse(url=f"{settings.frontend_url}/login?token={token}&new={new_str}")


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
