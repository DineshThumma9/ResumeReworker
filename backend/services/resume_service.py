from typing import Annotated

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from core.database import get_session
from core.security import decode_access_token
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
        if resume_content.projects:
            for project in resume_content.projects:
                project.name = "PROJECT NAME"

    if mask_details.company_name:
        if resume_content.experience:
            for exp in resume_content.experience:
                exp.company = "COMPANY NAME"
        if resume_content.internships:
            for internship in resume_content.internships:
                internship.company = "COMPANY NAME"

    if mask_details.name:
        resume_content.details.name = "John Doe"
    if mask_details.email:
        resume_content.details.email = "doejohn"
    if mask_details.phone:
        resume_content.details.contact = "1234567890"
    if mask_details.location:
        resume_content.details.location = "LOCATION"
    if mask_details.github:
        resume_content.details.github = "GITHUB_USERNAME"
    if mask_details.linkedin:
        resume_content.details.linkedin = "LINKEDIN_USERNAME"
    if mask_details.leetcode:
        resume_content.details.leetcode = "[LEETCODE_USERNAME]"
    if mask_details.portfolio:
        resume_content.details.portfolio = "[PORTFOLIO_URL]"

    if resume_content.details.profile_links:
        for k in list(resume_content.details.profile_links.keys()):
            if k == "phone" and mask_details.phone:
                resume_content.details.profile_links[k] = "[PHONE_NUMBER]"
            elif k == "email" and mask_details.email:
                resume_content.details.profile_links[k] = "[EMAIL_ADDRESS]"
            elif k == "github" and mask_details.github:
                resume_content.details.profile_links[k] = "[GITHUB_USERNAME]"
            elif k == "linkedin" and mask_details.linkedin:
                resume_content.details.profile_links[k] = "[LINKEDIN_USERNAME]"
            elif k == "leetcode" and mask_details.leetcode:
                resume_content.details.profile_links[k] = "[LEETCODE_USERNAME]"
            elif k in ("portfolio", "website") and mask_details.portfolio:
                resume_content.details.profile_links[k] = "[PORTFOLIO_URL]"

    return resume_content.model_dump_json()


# Convenient shorthand for use in route signatures
CurrentUser = Annotated[User, Depends(get_current_user)]
