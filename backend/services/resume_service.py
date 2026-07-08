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

    if mask_details.education:
        if resume_content.education:
            for edu in resume_content.education:
                if edu.institution:
                    edu.institution = "UNIVERSITY NAME"

    if resume_content.details:
        if mask_details.name and resume_content.details.name:
            resume_content.details.name = "John Doe"
        if mask_details.email and resume_content.details.email:
            resume_content.details.email = "doejohn"
        if mask_details.phone and resume_content.details.contact:
            resume_content.details.contact = "1234567890"
        if mask_details.location and resume_content.details.location:
            resume_content.details.location = "LOCATION"
        if mask_details.github and resume_content.details.github:
            resume_content.details.github = "GITHUB USERNAME"
        if mask_details.linkedin and resume_content.details.linkedin:
            resume_content.details.linkedin = "LINKEDIN USERNAME"
        if mask_details.leetcode and resume_content.details.leetcode:
            resume_content.details.leetcode = "LEETCODE USERNAME"
        if mask_details.portfolio and resume_content.details.portfolio:
            resume_content.details.portfolio = "PORTFOLIO URL"

        if resume_content.details.profile_links:
            # Type ignoring for dict assignment warnings from linter
            links = resume_content.details.profile_links
            for k in list(links.keys()):  # type: ignore
                if k == "phone" and mask_details.phone:
                    links[k] = "PHONE_NUMBER"  # type: ignore
                elif k == "email" and mask_details.email:
                    links[k] = "EMAIL ADDRESS"  # type: ignore
                elif k == "github" and mask_details.github:
                    links[k] = "GITHUB USERNAME"  # type: ignore
                elif k == "linkedin" and mask_details.linkedin:
                    links[k] = "LINKEDIN USERNAME"  # type: ignore
                elif k == "leetcode" and mask_details.leetcode:
                    links[k] = "LEETCODE USERNAME"  # type: ignore
                elif k in ("portfolio", "website") and mask_details.portfolio:
                    links[k] = "PORTFOLIO URL"  # type: ignore

    return resume_content.model_dump_json()


def extract_username(url: str):
    if not url:
        return None
    url = url.strip().rstrip('/')
    parts = url.split('/')
    if parts and len(parts[-1]) > 3:
        return parts[-1]
    return None


def mask_latex(latex_code: str, resume_content: dict, mask_details: MaskDetails) -> str:
    resume_content_model = RewriteResume.model_validate(resume_content)
    
    replacements = []
    
    if mask_details.project_name and resume_content_model.projects:
        for project in resume_content_model.projects:
            if project.name:
                replacements.append((project.name, "PROJECT NAME"))
                
    if mask_details.company_name:
        if resume_content_model.experience:
            for exp in resume_content_model.experience:
                if exp.company:
                    replacements.append((exp.company, "COMPANY NAME"))
        if resume_content_model.internships:
            for internship in resume_content_model.internships:
                if internship.company:
                    replacements.append((internship.company, "COMPANY NAME"))
                    
    if mask_details.education and resume_content_model.education:
        for edu in resume_content_model.education:
            if edu.institution:
                replacements.append((edu.institution, "UNIVERSITY NAME"))
                
    if resume_content_model.details:
        if mask_details.name and resume_content_model.details.name:
            name = resume_content_model.details.name
            replacements.append((name, "John Doe"))
            parts = name.split()
            if len(parts) >= 2:
                for p in parts:
                    if len(p) > 3:
                        replacements.append((p, "Doe"))
                        
        if mask_details.email and resume_content_model.details.email:
            replacements.append((resume_content_model.details.email, "doejohn@example.com"))
            
        if mask_details.phone and resume_content_model.details.contact:
            contact = resume_content_model.details.contact
            replacements.append((contact, "1234567890"))
            clean_phone = contact.replace(" ", "")
            if clean_phone != contact:
                replacements.append((clean_phone, "1234567890"))
                
        if mask_details.location and resume_content_model.details.location:
            replacements.append((resume_content_model.details.location, "LOCATION"))
            
        if mask_details.github and resume_content_model.details.github:
            replacements.append((resume_content_model.details.github, "GITHUB USERNAME"))
            uname = extract_username(resume_content_model.details.github)
            if uname:
                replacements.append((uname, "GITHUB USERNAME"))
            
        if mask_details.linkedin and resume_content_model.details.linkedin:
            replacements.append((resume_content_model.details.linkedin, "LINKEDIN_USERNAME"))
            uname = extract_username(resume_content_model.details.linkedin)
            if uname:
                replacements.append((uname, "LINKEDIN_USERNAME"))
            
        if mask_details.leetcode and resume_content_model.details.leetcode:
            replacements.append((resume_content_model.details.leetcode, "LEETCODE USERNAME"))
            uname = extract_username(resume_content_model.details.leetcode)
            if uname:
                replacements.append((uname, "LEETCODE USERNAME"))
            
        if mask_details.portfolio and resume_content_model.details.portfolio:
            replacements.append((resume_content_model.details.portfolio, "PORTFOLIO_URL"))

    # deduplicate and sort
    replacements = list(set(replacements))
    replacements.sort(key=lambda x: len(x[0]), reverse=True)
    
    for old, new in replacements:
        if old.strip():
            latex_code = latex_code.replace(old, new)
            
    return latex_code

# Convenient shorthand for use in route signatures
CurrentUser = Annotated[User, Depends(get_current_user)]
