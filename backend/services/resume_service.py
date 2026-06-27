from typing import Annotated

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from core.security import decode_access_token
from core.database import get_session
from models import User
from schemas.schema import MaskDetails, RewriteResume

bearer = HTTPBearer(auto_error=False)


async def get_current_user(
    request: Request,
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer)] = None,
    db: AsyncSession = Depends(get_session),
) -> User:
    """
    FastAPI dependency that resolves the authenticated user.

    DEV_MODE=true  → always returns a mock user, no token needed.
    DEV_MODE=false → validates JWT and fetches user from DB.
    """
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id = decode_access_token(credentials.credentials)
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found"
        )

    return user


async def mask_resume(resume_content, mask_details: MaskDetails):
    resume_content = RewriteResume.model_validate(resume_content)
    if mask_details.project_name:
        for project in resume_content.projects:
            project.name = "[PROJECT NAME]"

    if mask_details.company_name:
        for project in resume_content.projects:
            project.company = "[COMPANY NAME]"

    if mask_details.email:
        resume_content.details.email = "[EMAIL_ADDRESS]"
    if mask_details.phone:
        resume_content.details.phone = "[PHONE_NUMBER]"
    if mask_details.location:
        resume_content.details.location = "[LOCATION]"
    if mask_details.github:
        resume_content.details.github = "[GITHUB_USERNAME]"
    if mask_details.linkedin:
        resume_content.details.linkedin = "[LINKEDIN_USERNAME]"
    if mask_details.leetcode:
        resume_content.details.leetcode = "[LEETCODE_USERNAME]"
    if mask_details.portfolio:
        resume_content.details.portfolio = "[PORTFOLIO_URL]"

    return resume_content.model_dump_json()

# Convenient shorthand for use in route signatures
CurrentUser = Annotated[User, Depends(get_current_user)]