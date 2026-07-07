import secrets
from typing import Annotated, Any, Dict

import fitz
from fastapi import APIRouter, Cookie, Depends, File, HTTPException, UploadFile, status
from fastapi.responses import RedirectResponse, Response
from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage, SystemMessage
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
from models.models import UserLLMConfig
from schemas.schema import (
    LoginBody,
    ProfileOut,
    ProfileUpdate,
    RewriteResume,
    SignupBody,
)
from services.auth_service import AuthService
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


def map_llm_to_profile(parsed: Any) -> Dict[str, Any]:
    details = parsed.details
    links = details.profile_links or {}

    profile_data = {
        "name": details.name or "",
        "phone": links.get("phone") or "",
        "location": links.get("location") or "",
        "github": links.get("github") or "",
        "linkedin": links.get("linkedin") or "",
        "website": links.get("website") or links.get("portfolio") or "",
        "sections": {},
    }

    sections = {}

    # Map Education
    if parsed.education:
        edu_list = []
        for idx, edu in enumerate(parsed.education):
            edu_list.append(
                {
                    "id": f"edu_{idx}",
                    "title": edu.course or "",
                    "subtitle": edu.institution or "",
                    "date": edu.year or "",
                    "description": f"GPA: {edu.gpa}" if edu.gpa else "",
                }
            )
        if edu_list:
            sections["education"] = edu_list

    # Map Experience
    if parsed.experience:
        exp_list = []
        for idx, exp in enumerate(parsed.experience):
            resp_str = (
                "\n".join([f"- {r}" for r in exp.responsibilities])
                if exp.responsibilities
                else ""
            )
            exp_list.append(
                {
                    "id": f"exp_{idx}",
                    "title": exp.role or "",
                    "subtitle": exp.company or "",
                    "date": exp.duration or "",
                    "description": resp_str,
                }
            )
        if exp_list:
            sections["experience"] = exp_list

    # Map Projects
    if parsed.projects:
        proj_list = []
        for idx, proj in enumerate(parsed.projects):
            tech_str = ", ".join(proj.technologies) if proj.technologies else ""
            desc_str = proj.description or ""
            if proj.highlights:
                desc_str += "\n" + "\n".join([f"- {h}" for h in proj.highlights])
            proj_list.append(
                {
                    "id": f"proj_{idx}",
                    "title": proj.name or "",
                    "subtitle": "",
                    "skills": tech_str,
                    "link": proj.link or "",
                    "description": desc_str.strip(),
                }
            )
        if proj_list:
            sections["projects"] = proj_list

    # Map Skills
    if parsed.technical_skills:
        skills_list = []
        for idx, sk in enumerate(parsed.technical_skills):
            skills_list.append(
                {
                    "id": f"skill_{idx}",
                    "title": sk.category or "",
                    "skills": ", ".join(sk.skills) if sk.skills else "",
                }
            )
        if skills_list:
            sections["skills"] = skills_list

    # Map Achievements
    if parsed.achivements:
        ach_list = []
        for idx, ach in enumerate(parsed.achivements):
            ach_list.append({"id": f"ach_{idx}", "title": ach, "description": ""})
        if ach_list:
            sections["achievements"] = ach_list

    # Map Open Source
    if parsed.open_source:
        os_list = []
        for idx, os_item in enumerate(parsed.open_source):
            os_list.append({"id": f"os_{idx}", "description": os_item})
        if os_list:
            sections["open_source"] = os_list

    # Map Certifications
    if parsed.certifications:
        cert_list = []
        for idx, cert in enumerate(parsed.certifications):
            cert_list.append({"id": f"cert_{idx}", "title": cert})
        if cert_list:
            sections["certifications"] = cert_list

    # Map Hackathons
    if parsed.hackathons:
        hack_list = []
        for idx, hack in enumerate(parsed.hackathons):
            hack_list.append({"id": f"hack_{idx}", "title": hack})
        if hack_list:
            sections["hackathons"] = hack_list

    # Map Coursework
    if parsed.coursework:
        course_list = []
        for idx, course in enumerate(parsed.coursework):
            course_list.append({"id": f"course_{idx}", "description": course})
        if course_list:
            sections["coursework"] = course_list

    profile_data["sections"] = sections
    return profile_data


@router.post("/profile/autofill", response_model=Dict[str, Any])
async def autofill_profile(
    user: CurrentUser,
    db: DB,
    file: UploadFile = File(...),
):
    try:
        pdf_bytes = await file.read()
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        resume_text = ""
        for page in doc:
            text = page.get_text()
            if isinstance(text, str):
                resume_text += text
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to read PDF file: {str(e)}",
        )

    if not resume_text.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The uploaded PDF is empty or could not be parsed.",
        )

    # Resolve LLM configuration and key
    result = await db.execute(
        select(UserLLMConfig).where(UserLLMConfig.user_id == user.id)
    )
    config = result.scalars().first()

    provider = "groq"
    model = "llama-3.3-70b-versatile"
    if config:
        provider = config.provider
        model = config.model

    api_key = None
    try:
        auth_service = AuthService(db)
        api_key = await auth_service.get_api_key(provider, user)
    except Exception:
        # Fallback to system settings keys if user has not configured their own
        provider_keys = {
            "openai": settings.openai_api_key,
            "anthropic": settings.anthropic_api_key,
            "google_genai": settings.google_api_key,
            "groq": settings.groq_api_key,
            "mistralai": settings.mistral_api_key,
            "openrouter": settings.openrouter_api_key,
            "huggingface": settings.huggingface_api_key,
        }
        api_key = provider_keys.get(provider)

    try:
        llm_kwargs = {}
        if api_key:
            llm_kwargs["api_key"] = api_key

        llm = init_chat_model(model, model_provider=provider, **llm_kwargs)
        structured_llm = llm.with_structured_output(RewriteResume)

        parse_resume_prompt = """
        You are an expert resume parser. Your ONLY job is to extract the candidate's resume content into the structured schema format.
        Do NOT invent details. Do NOT summarize or rewrite the content. Simply parse the sections verbatim into the appropriate fields.

        For each section:
        1. details: Extract candidate's name, profile summary, and contact/social links (phone, email, github, linkedin, website, location, etc.).
        2. experience: Extract all work experience entries. Join responsibilities into a list of strings (each bullet point is one list item).
        3. education: Extract all education entries.
        4. projects: Extract all projects.
        5. technical_skills: Extract technical skills categorized by category name and flat list of skills.
        6. achivements: Extract all achievements, certifications, coursework, open-source, or hackathons if they fit the schema.
        """

        messages = [
            SystemMessage(content=parse_resume_prompt),
            HumanMessage(content=f"Resume text:\n{resume_text}"),
        ]

        parsed = await structured_llm.ainvoke(messages)
        if not parsed:
            raise Exception("LLM returned empty parsed result.")

        return map_llm_to_profile(parsed)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to parse resume details: {str(e)}",
        )
