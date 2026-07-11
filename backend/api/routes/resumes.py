import base64
import json
import logging
from datetime import datetime, timezone
from typing import Annotated, Optional

import fitz
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from fastapi.responses import StreamingResponse
from fastapi_limiter.depends import RateLimiter
from pydantic import BaseModel
from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from core.config import settings
from core.database import get_session
from models.models import Resume, Template, User
from schemas.schema import PaginatedResume, ResumeOut, ResumeUpdate
from services.auth_service import AuthService
from services.renderer import render_resume_template, render_resume_template_from_string
from services.resume_service import CurrentUser
from services.storage import upload_pdf_to_cloudinary
from services.workflow import ResumeWorkflowService

logger = logging.getLogger(__name__)


def naive_utcnow() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


router = APIRouter(prefix="/resumes", tags=["resumes"])

DB = Annotated[AsyncSession, Depends(get_session)]


class ResumeCreate(BaseModel):
    label: str
    tex_source: str
    jd_snippet: Optional[str] = None
    template_id: Optional[int] = None
    pdf_url: Optional[str] = None
    content: Optional[dict] = None


class CompileRequest(BaseModel):
    latex_code: str
    id: Optional[int] = None


async def save_and_upload(
    latex_code: str, user: User, resume_id: int, pdf_base64: Optional[str] = None
) -> tuple[str, Optional[str]]:
    """Helper to compile LaTeX source to PDF, upload it, and return URLs."""
    if pdf_base64 and "base64," in pdf_base64:
        b64_str = pdf_base64.split("base64,")[1]
        pdf_bytes = base64.b64decode(b64_str)
        pdf_url = pdf_base64
    elif not latex_code or not latex_code.strip():
        # Prevent hanging compiler with empty latex code
        pdf_bytes = b""
        pdf_url = ""
    else:
        service = ResumeWorkflowService()
        pdf_bytes = await service.latex_to_pdf(latex_code, "resume.pdf")
        pdf_b64 = base64.b64encode(pdf_bytes).decode("utf-8")
        pdf_url = f"data:application/pdf;base64,{pdf_b64}"

    preview_url = None
    try:
        filename = f"resume_{user.id}_{resume_id}_{int(datetime.now(timezone.utc).timestamp())}.pdf"
        upload_res = await upload_pdf_to_cloudinary(pdf_bytes, filename)
        if upload_res:
            pdf_url = upload_res.get("pdf_url") or pdf_url
            preview_url = upload_res.get("preview_image_url")
    except Exception as preview_err:
        logger.error(f"Failed to generate preview: {preview_err}")

    return pdf_url, preview_url


@router.get("", response_model=PaginatedResume)
async def get_resumes(user: CurrentUser, db: DB, skip: int = 0, limit: int = 100):
    """List all resumes for the authenticated user."""
    result = await db.execute(
        select(Resume)
        .where(Resume.user_id == user.id)
        .order_by(Resume.updated_at.desc())  # type: ignore
        .offset(skip)
        .limit(limit)
    )
    resumes = result.scalars().all()

    count_result = await db.execute(
        select(func.count(Resume.id)).where(Resume.user_id == user.id)  # type: ignore
    )
    total_count = count_result.scalar_one()

    return PaginatedResume(
        resumes=resumes,  # type: ignore
        skip=skip,
        limit=limit,
        total_count=total_count,
    )


@router.post("", response_model=ResumeOut)
async def create_resume(body: ResumeCreate, user: CurrentUser, db: DB):
    # Compile LaTeX and upload preview if tex_source is provided

    pdf_url, preview_url = await save_and_upload(
        latex_code=body.tex_source,
        user=user,
        resume_id=int(datetime.now(timezone.utc).timestamp()),
        pdf_base64=body.pdf_url,
    )

    resume = Resume(
        user_id=user.id,
        label=body.label,
        tex_source=body.tex_source,
        jd_snippet=body.jd_snippet,
        template_id=body.template_id,
        pdf_url=pdf_url,
        preview_url=preview_url,
        content=body.content,
    )
    db.add(resume)
    await db.commit()
    await db.refresh(resume)
    return resume


@router.post("/compile")
async def compile_latex(body: CompileRequest, user: CurrentUser, db: DB):
    try:
        if body.id is not None:
            result = await db.execute(
                select(Resume).where(Resume.id == body.id, Resume.user_id == user.id)
            )
            resume = result.scalar_one_or_none()
            if resume:
                pdf_url, preview_url = await save_and_upload(
                    latex_code=body.latex_code, user=user, resume_id=body.id
                )
                resume.tex_source = body.latex_code
                resume.pdf_url = pdf_url
                if preview_url:
                    resume.preview_url = preview_url

                resume.updated_at = naive_utcnow()
                await db.commit()
                return {"pdf_url": pdf_url}

        # Fallback if body.id is None or resume not found
        service = ResumeWorkflowService()
        pdf_bytes = await service.latex_to_pdf(body.latex_code, "resume.pdf")
        pdf_base64 = base64.b64encode(pdf_bytes).decode("utf-8")
        pdf_url = f"data:application/pdf;base64,{pdf_base64}"
        return {"pdf_url": pdf_url}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"LaTeX compilation failed: {str(e)}",
        )


@router.get("/{resume_id}", response_model=ResumeOut)
async def get_resume(resume_id: int, user: CurrentUser, db: DB):
    result = await db.execute(
        select(Resume).where(Resume.id == resume_id, Resume.user_id == user.id)
    )
    resume = result.scalar_one_or_none()
    if not resume:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Resume not found")
    return resume


@router.delete("/{resume_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_resume(resume_id: int, user: CurrentUser, db: DB):
    result = await db.execute(
        select(Resume).where(Resume.id == resume_id, Resume.user_id == user.id)
    )
    resume = result.scalar_one_or_none()
    if not resume:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Resume not found")
    await db.delete(resume)
    await db.commit()


@router.put("/{resume_id}", response_model=ResumeOut)
async def update_resume(resume_id: int, body: ResumeUpdate, user: CurrentUser, db: DB):
    result = await db.execute(
        select(Resume).where(Resume.id == resume_id, Resume.user_id == user.id)
    )
    resume = result.scalar_one_or_none()
    if not resume:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Resume not found")
    if body.label is not None:
        resume.label = body.label
    if body.tex_source is not None:
        resume.tex_source = body.tex_source
        pdf_url, preview_url = await save_and_upload(
            latex_code=body.tex_source, user=user, resume_id=resume_id
        )
        if pdf_url is not None:
            resume.pdf_url = pdf_url
        if preview_url is not None:
            resume.preview_url = preview_url

    resume.updated_at = naive_utcnow()
    db.add(resume)
    await db.commit()
    await db.refresh(resume)
    return resume


@router.put("/{resume_id}/render")
async def render_resume(
    resume_id: int, user: CurrentUser, db: DB, template_id: str = ""
):
    """Re-render with a different template without re-running AI."""

    result = await db.execute(
        select(Resume).where(Resume.id == resume_id, Resume.user_id == user.id)
    )
    resume = result.scalar_one_or_none()
    if not resume:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Resume not found")
    if not resume.content:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            "Resume content is empty, please run analysis first",
        )

    template_source = None
    db_template_id = None
    if template_id and template_id.isdigit():
        t_res = await db.execute(
            select(Template).where(Template.id == int(template_id))
        )
        template_obj = t_res.scalar_one_or_none()
        if template_obj:
            template_source = template_obj.tex_source
            db_template_id = template_obj.id

    try:
        data_dict = resume.content
        if template_source and template_source.strip():
            latex_code = render_resume_template_from_string(template_source, data_dict)
        else:
            latex_code = render_resume_template("jakes1.tex", data_dict)

        pdf_url, preview_url = await save_and_upload(
            latex_code=latex_code, user=user, resume_id=resume_id
        )
        resume.tex_source = latex_code
        resume.pdf_url = pdf_url
        if preview_url:
            resume.preview_url = preview_url
        resume.template_id = db_template_id
        resume.updated_at = naive_utcnow()
        db.add(resume)
        await db.commit()
        await db.refresh(resume)
        return resume
    except Exception as e:
        raise HTTPException(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            f"Failed to re-render resume: {str(e)}",
        )


async def extract_details(resume_file):
    resume_text = ""
    if resume_file is not None:
        try:
            pdf_bytes = await resume_file.read()
            doc = fitz.open(stream=pdf_bytes, filetype="pdf")
            extracted_links: list[str] = []
            for page in doc:
                resume_text += page.get_text()  # type: ignore
                # Also extract hyperlink annotations with their anchor text
                for link in page.get_links():  # type: ignore
                    uri = link.get("uri", "")
                    if uri and uri.startswith("http"):
                        rect = link.get("from")
                        anchor_text = ""
                        if rect:
                            raw_text = page.get_text("text", clip=rect)
                            if isinstance(raw_text, str):
                                anchor_text = raw_text.strip()
                            elif isinstance(raw_text, dict):
                                anchor_text = raw_text.get("text", "").strip()
                            elif isinstance(raw_text, list):
                                anchor_text = " ".join(str(x) for x in raw_text).strip()
                            else:
                                anchor_text = str(raw_text).strip()
                            anchor_text = " ".join(anchor_text.split())

                        if anchor_text:
                            extracted_links.append(
                                f"Text: '{anchor_text}' -> URL: {uri}"
                            )
                        else:
                            extracted_links.append(f"URL: {uri}")

            if extracted_links:
                # Deduplicate while preserving order
                seen: set[str] = set()
                unique_links = [
                    u for u in extracted_links if not (u in seen or seen.add(u))
                ]  # type: ignore
                resume_text += "\n\n[HYPERLINKS FOUND IN RESUME — use these to fill profile_links and project links]\n"
                resume_text += "\n".join(unique_links)
            return resume_text
        except Exception as e:
            raise ValueError(f"Failed to read PDF: {str(e)}")
    return resume_text


def extract_profile_details(user):
    profile_details = (
        f"\n\nCandidate Contact Details:\nName: {user.name}\nEmail: {user.email}"
    )
    if user.phone:
        profile_details += f"\nPhone: {user.phone}"
    if user.location:
        profile_details += f"\nLocation: {user.location}"
    if user.github:
        profile_details += f"\nGitHub: {user.github}"
    if user.linkedin:
        profile_details += f"\nLinkedIn: {user.linkedin}"
    if user.website:
        profile_details += f"\nWebsite/Portfolio: {user.website}"

    return profile_details


def extract_resume_details(raw_resume):
    try:
        if isinstance(raw_resume, str):
            sections_dict = json.loads(raw_resume)
        else:
            sections_dict = raw_resume

        if isinstance(sections_dict, dict):
            resume_text = ""
            for sec_name, items in sections_dict.items():
                if not items:
                    continue
                clean_title = sec_name.replace("_", " ").upper()
                resume_text += f"\n\n## {clean_title}"
                if isinstance(items, list):
                    for item in items:
                        title = item.get("title", "")
                        subtitle = item.get("subtitle", "")
                        date = item.get("date", "")
                        skills = item.get("skills", "")
                        link = item.get("link", "")
                        desc = item.get("description", "")

                        header_parts = []
                        if title:
                            header_parts.append(f"**{title}**")
                        if subtitle:
                            header_parts.append(f"at {subtitle}")
                        if date:
                            header_parts.append(f"({date})")

                        if header_parts:
                            resume_text += "\n- " + " ".join(header_parts)
                        if link:
                            resume_text += f"\n  Link: {link}"
                        if skills:
                            resume_text += f"\n  Skills/Tech: {skills}"
                        if desc:
                            indented_desc = "\n  ".join(desc.split("\n"))
                            resume_text += f"\n  Details: {indented_desc}"
                elif isinstance(items, str) and items.strip():
                    resume_text += f"\n{items}"
            return resume_text
        else:
            return raw_resume
    except Exception:
        return raw_resume


async def start_graph(
    db, provider, user, template_id, exclude_sections, model, tone, jd, resume_text
):
    auth_service = AuthService(db)
    api_key = ""
    try:
        api_key = await auth_service.get_api_key(provider, user)
    except Exception:
        pass

    template_source = None
    db_template_id = None

    if template_id and template_id.isdigit():
        t_res = await db.execute(
            select(Template).where(Template.id == int(template_id))
        )
        template_obj = t_res.scalar_one_or_none()
        if template_obj:
            template_source = template_obj.tex_source
            db_template_id = template_obj.id

    initial_state = {
        "jd": jd,
        "resume": resume_text,
        "tone": tone,
        "provider": provider,
        "model": model,
        "api_key": api_key,
        "exclude_sections": json.loads(exclude_sections),
        "analysis": None,
        "changes_content": None,
        "latex_code": "",
        "output_path": "/output",
        "template_source": template_source or "",
        "template_id": db_template_id,
    }

    return initial_state


def resolve_resume_label(label: str, analysis_data: dict | None, user: User) -> str:
    resolved_label = label
    if not resolved_label or not resolved_label.strip():
        company_name = "Company"
        if analysis_data and isinstance(analysis_data, dict):
            company_name = analysis_data.get("company_name", "Company")

        # Clean up name & company name to form a nice slug
        clean_name = "".join(
            c for c in user.name if c.isalnum() or c in (" ", "_", "-")
        ).strip()
        clean_company = "".join(
            c for c in company_name if c.isalnum() or c in (" ", "_", "-")
        ).strip()

        # Remove spaces to make it direct {Name}{CompanyName} style with underscore
        clean_name = clean_name.replace(" ", "")
        clean_company = clean_company.replace(" ", "")

        if not clean_name:
            clean_name = "User"
        if not clean_company:
            clean_company = "Company"

        resolved_label = f"{clean_name}{clean_company}"

    return resolved_label


@router.post("/analyze", dependencies=[Depends(RateLimiter(times=10, seconds=60))])
async def analyze(
    user: CurrentUser,
    db: DB,
    jd: str = Form(...),
    label: str = Form(""),
    tone: str = Form("Professional"),
    template_id: str = Form("1"),
    provider: str = Form("groq"),
    model: str = Form("llama-3.3-70b-versatile"),
    exclude_sections: str = Form("{}"),
    resume_file: Optional[UploadFile] = File(None),
):
    """
    Main AI workflow. Streams progress as Server-Sent Events.
    Events: progress | complete | error
    """

    async def event_stream():
        try:
            resume_text = ""
            if resume_file is not None:
                resume_text += await extract_details(resume_file)
            else:
                raw_res = user.raw_resume
                if isinstance(raw_res, (dict, list)):
                    raw_res_str = json.dumps(raw_res)
                else:
                    raw_res_str = str(raw_res) if raw_res else ""

                if not raw_res_str or not raw_res_str.strip():
                    yield f"data: {json.dumps({'event': 'error', 'message': 'No resume provided. Please upload a PDF resume or type your resume in your Profile.'})}\n\n"
                    return

                resume_text += extract_resume_details(raw_res)

            # Append candidate
            resume_text += extract_profile_details(user)

            initial_state = await start_graph(
                db,
                provider,
                user,
                template_id,
                exclude_sections,
                model,
                tone,
                jd,
                resume_text,
            )
        except Exception as graph_err:
            import traceback

            tb = traceback.format_exc()
            logger.error(f"GRAPH ERROR: {tb}")
            err_msg = f"Internal Error: {str(graph_err)}"
            if settings.dev_mode:
                err_msg += f"\nTraceback:\n{tb}"
            else:
                err_msg += "\nPlease try again or contact support."
            yield f"data: {json.dumps({'event': 'error', 'message': err_msg})}\n\n"
            return

        service = ResumeWorkflowService()
        graph = service.graph

        analysis_data = None
        try:
            async for event in graph.astream(initial_state, stream_mode="updates"):  # type: ignore
                if "match_jd" in event:
                    analysis_data = event["match_jd"].get("analysis")
                    if analysis_data:
                        # 1. Score & match — instant
                        yield f"data: {json.dumps({'event': 'analysis_score', 'score': analysis_data.get('score'), 'match': analysis_data.get('match'), 'urgency': analysis_data.get('urgency')})}\n\n"

                        # 2. Resume quality — stream word by word
                        quality = analysis_data.get("resume_quality") or ""
                        if quality:
                            words = quality.split()
                            for i, _ in enumerate(words):
                                partial = " ".join(words[: i + 1])
                                yield f"data: {json.dumps({'event': 'analysis_quality', 'text': partial})}\n\n"

                        # 3. Explanation — stream word by word
                        explanation = analysis_data.get("match_explanation") or ""
                        if explanation:
                            words = explanation.split()
                            for i, _ in enumerate(words):
                                partial = " ".join(words[: i + 1])
                                yield f"data: {json.dumps({'event': 'analysis_explanation', 'text': partial})}\n\n"

                        # 4. Missing keywords — one per event
                        for kw in analysis_data.get("missing_keywords") or []:
                            yield f"data: {json.dumps({'event': 'analysis_keyword', 'keyword': kw})}\n\n"

                        # 5. Negative points — one per event
                        for pt in analysis_data.get("negative_points") or []:
                            yield f"data: {json.dumps({'event': 'analysis_negative', 'text': pt})}\n\n"

                        # 6. Improvements — one per event
                        for imp in analysis_data.get("potential_improvements") or []:
                            yield f"data: {json.dumps({'event': 'analysis_improvement', 'text': imp})}\n\n"

                        # 7. Done — triggers UI to flip to success state
                        yield f"data: {json.dumps({'event': 'analysis_done'})}\n\n"
                    else:
                        yield f"data: {json.dumps({'event': 'analysis_done'})}\n\n"
                elif "rewrite_resume" in event:
                    yield f"data: {json.dumps({'event': 'progress', 'step': 'rewrite_resume', 'message': 'Finished rewriting resume...'})}\n\n"
                elif "judge_resume" in event:
                    judgement = event["judge_resume"].get("judgements", [])[-1] if event["judge_resume"].get("judgements") else None
                    iteration = event["judge_resume"].get("iteration", 1)
                    if judgement:
                        if isinstance(judgement, dict):
                            should_rewrite = judgement.get("should_rewrite", False)
                            req_changes = judgement.get("request_changes", [])
                        else:
                            should_rewrite = getattr(judgement, "should_rewrite", False)
                            req_changes = getattr(judgement, "request_changes", [])

                        if should_rewrite:
                            msg = f"Judge requested changes (Iteration {iteration}). Rewriting again..."
                            if req_changes:
                                msg += f" Feedback: {'; '.join(req_changes)}"
                        else:
                            msg = f"Judge approved rewrite (Iteration {iteration}). Proceeding to PDF generation..."
                        yield f"data: {json.dumps({'event': 'progress', 'step': 'judge_resume', 'message': msg})}\n\n"
                    else:
                        yield f"data: {json.dumps({'event': 'progress', 'step': 'judge_resume', 'message': f'Evaluating rewritten resume (Iteration {iteration})...'})}\n\n"
                elif "rewrite_latex" in event:
                    data = event["rewrite_latex"]
                    latex_code = data.get("latex_code", "")
                    diff_latex_code = data.get("diff_latex_code", "")
                    pdf_base64 = data.get("pdf_base64", "")
                    diff_pdf_base64 = data.get("diff_pdf_base64", "")
                    error_msg = data.get("error", None)

                    resume_id = None
                    if (
                        latex_code
                        and not latex_code.startswith("Error:")
                        and not error_msg
                    ):
                        try:
                            changes_content = data.get("changes_content")
                            content_dict = None
                            if changes_content:
                                if hasattr(changes_content, "model_dump"):
                                    content_dict = changes_content.model_dump()
                                elif isinstance(changes_content, dict):
                                    content_dict = changes_content

                            resolved_label = resolve_resume_label(
                                label, analysis_data, user
                            )

                            try:
                                template_id_val = initial_state.get("template_id")
                                body = ResumeCreate(
                                    label=resolved_label,
                                    tex_source=latex_code,
                                    jd_snippet=jd,
                                    template_id=int(template_id_val) if template_id_val is not None else None,
                                    pdf_url=pdf_base64,
                                    content=content_dict,
                                )
                                resume = await create_resume(body, user, db)
                                resume_id = resume.id
                                pdf_base64 = (
                                    resume.pdf_url
                                )  # Use the uploaded Cloudinary URL instead!
                            except Exception as db_err:
                                logger.error(
                                    f"Failed to save resume to DB via create_resume: {db_err}"
                                )

                        except Exception as db_err:
                            logger.error(f"Failed to save resume to DB: {db_err}")

                    payload = {
                        "event": "complete",
                        "message": "Done!",
                        "latexCode": latex_code,
                        "diffLatexCode": diff_latex_code,
                        "pdfUrl": pdf_base64,
                        "diffPdfUrl": diff_pdf_base64,
                    }
                    if error_msg:
                        payload["error"] = error_msg
                    if resume_id is not None:
                        payload["resumeId"] = resume_id

                    yield f"data: {json.dumps(payload)}\n\n"

        except Exception as stream_err:
            import traceback

            tb = traceback.format_exc()
            import logging

            logging.getLogger(__name__).error(f"STREAM ERROR: {tb}")
            error_msg = str(stream_err)
            if (
                "429" in error_msg
                or "RESOURCE_EXHAUSTED" in error_msg
                or "quota" in error_msg.lower()
            ):
                error_msg = "API Error: You have exceeded your API quota. Please check your billing or plan."
            elif "401" in error_msg or "403" in error_msg or "API_KEY" in error_msg:
                error_msg = (
                    "API Error: Invalid API key. Please check your API key in Settings."
                )
            else:
                error_msg = f"Internal Error: {error_msg}"
            yield f"data: {json.dumps({'event': 'error', 'message': error_msg})}\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")


class ModifyRequest(BaseModel):
    latex_code: str
    instruction: str
    provider: str = "groq"
    model: str = "llama-3.3-70b-versatile"


@router.post("/modify", dependencies=[Depends(RateLimiter(times=20, seconds=60))])
async def modify_latex(
    req: ModifyRequest,
    user: CurrentUser,
    db: DB,
):
    """
    Modifies raw LaTeX code based on user instruction and streams the updated code.
    """
    import logging

    from langchain.chat_models import init_chat_model
    from langchain_core.messages import HumanMessage, SystemMessage

    from core.config import settings

    # 1. Get user's custom API key if it exists
    auth_service = AuthService(db)
    api_key = ""
    try:
        api_key = await auth_service.get_api_key(req.provider, user)
    except Exception:
        pass

    # 2. Fallback keys from settings
    provider_keys = {
        "openai": settings.openai_api_key,
        "anthropic": settings.anthropic_api_key,
        "google_genai": settings.google_api_key,
        "groq": settings.groq_api_key,
        "mistralai": settings.mistral_api_key,
        "openrouter": settings.openrouter_api_key,
        "huggingface": settings.huggingface_api_key,
    }

    selected_key = api_key or provider_keys.get(req.provider)
    llm_kwargs = {}
    if selected_key:
        llm_kwargs["api_key"] = selected_key

    try:
        llm = init_chat_model(req.model, model_provider=req.provider, **llm_kwargs)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to initialize model '{req.model}' with provider '{req.provider}': {str(e)}",
        )

    async def modify_stream():
        try:
            system_prompt = (
                "You are an expert LaTeX editor.\n"
                "Your task is to modify the provided LaTeX code according to the user's instructions.\n"
                "CRITICAL RULES:\n"
                "1. Return ONLY valid LaTeX code.\n"
                "2. Do NOT wrap your output in markdown code blocks (e.g. do not write ```latex ... ```). Start directly with the LaTeX code.\n"
                "3. Preserve the structure, design, packages, and formatting of the original LaTeX document. Only change what is requested.\n"
                "4. If the instruction is empty or irrelevant, return the original LaTeX document unchanged."
            )

            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(
                    content=f"Original LaTeX:\n{req.latex_code}\n\nUser Instruction:\n{req.instruction}"
                ),
            ]

            async for chunk in llm.astream(messages):
                yield f"data: {json.dumps({'event': 'chunk', 'text': chunk.content})}\n\n"

        except Exception as stream_err:
            import traceback

            tb = traceback.format_exc()
            logging.getLogger(__name__).error(f"MODIFY STREAM ERROR: {tb}")

            error_msg = str(stream_err)
            if (
                "429" in error_msg
                or "RESOURCE_EXHAUSTED" in error_msg
                or "quota" in error_msg.lower()
            ):
                error_msg = "API Error: You have exceeded your API quota. Please check your billing or plan."
            elif "401" in error_msg or "403" in error_msg or "API_KEY" in error_msg:
                error_msg = (
                    "API Error: Invalid API key. Please check your API key in Settings."
                )
            else:
                error_msg = f"Error modifying LaTeX: {error_msg}"

            yield f"data: {json.dumps({'event': 'error', 'message': error_msg})}\n\n"

    return StreamingResponse(modify_stream(), media_type="text/event-stream")
