import asyncio
import base64
import json
from datetime import datetime
from typing import Annotated, Optional

import fitz
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from core.database import get_session
from models.models import Resume, Template
from schemas.schema import PaginatedResume, ResumeOut, ResumeUpdate
from services.auth_service import AuthService
from services.renderer import render_resume_template, render_resume_template_from_string
from services.resume_service import CurrentUser
from services.workflow import ResumeWorkflowService

router = APIRouter(prefix="/resumes", tags=["resumes"])

DB = Annotated[AsyncSession, Depends(get_session)]


class ResumeCreate(BaseModel):
    label: str
    tex_source: str
    jd_snippet: Optional[str] = None
    template_id: Optional[int] = None
    pdf_url: Optional[str] = None


class CompileRequest(BaseModel):
    latex_code: str
    id: Optional[int] = None


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
    resume = Resume(
        user_id=user.id,
        label=body.label,
        tex_source=body.tex_source,
        jd_snippet=body.jd_snippet,
        template_id=body.template_id,
        pdf_url=body.pdf_url,
    )
    db.add(resume)
    await db.commit()
    await db.refresh(resume)
    return resume


@router.post("/compile")
async def compile_latex(body: CompileRequest, user: CurrentUser, db: DB):
    try:
        service = ResumeWorkflowService()
        pdf_bytes = await service.latex_to_pdf(body.latex_code, "resume.pdf")
        pdf_base64 = base64.b64encode(pdf_bytes).decode("utf-8")
        pdf_url = f"data:application/pdf;base64,{pdf_base64}"

        if body.id is not None:
            result = await db.execute(
                select(Resume).where(Resume.id == body.id, Resume.user_id == user.id)
            )
            resume = result.scalar_one_or_none()
            if resume:
                resume.tex_source = body.latex_code
                resume.pdf_url = pdf_url
                resume.updated_at = datetime.utcnow()
                await db.commit()

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
    if body.pdf_url is not None:
        resume.pdf_url = body.pdf_url
    resume.updated_at = datetime.utcnow()
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

        # Recompile
        pdf_url = ResumeWorkflowService.latex_to_pdf(latex_code)  # type: ignore

        resume.tex_source = latex_code
        resume.pdf_url = pdf_url
        resume.template_id = db_template_id
        resume.updated_at = datetime.utcnow()
        db.add(resume)
        await db.commit()
        await db.refresh(resume)
        return resume
    except Exception as e:
        raise HTTPException(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            f"Failed to re-render resume: {str(e)}",
        )


@router.post("/analyze")
async def analyze(
    user: CurrentUser,
    db: DB,
    jd: str = Form(...),
    label: str = Form(...),
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
                                anchor_text = page.get_text("text", clip=rect).strip()
                                anchor_text = " ".join(anchor_text.split())
                            
                            if anchor_text:
                                extracted_links.append(f"Text: '{anchor_text}' -> URL: {uri}")
                            else:
                                extracted_links.append(f"URL: {uri}")
                                
                if extracted_links:
                    # Deduplicate while preserving order
                    seen: set[str] = set()
                    unique_links = [u for u in extracted_links if not (u in seen or seen.add(u))]  # type: ignore
                    resume_text += "\n\n[HYPERLINKS FOUND IN RESUME — use these to fill profile_links and project links]\n"
                    resume_text += "\n".join(unique_links)
            except Exception as e:
                yield f"data: {json.dumps({'event': 'error', 'message': f'Failed to read PDF: {str(e)}'})}\n\n"
                return
        else:
            if not user.raw_resume or not user.raw_resume.strip():
                yield f"data: {json.dumps({'event': 'error', 'message': 'No resume provided. Please upload a PDF resume or type your resume in your Profile.'})}\n\n"
                return
            try:
                sections_dict = json.loads(user.raw_resume)
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
                else:
                    resume_text = user.raw_resume
            except Exception:
                resume_text = user.raw_resume

        # Append candidate profile details
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

        resume_text += profile_details

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

        service = ResumeWorkflowService()
        graph = service.graph

        analysis_data = None
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
                            await asyncio.sleep(0.025)

                    # 3. Explanation — stream word by word
                    explanation = analysis_data.get("match_explanation") or ""
                    if explanation:
                        words = explanation.split()
                        for i, _ in enumerate(words):
                            partial = " ".join(words[: i + 1])
                            yield f"data: {json.dumps({'event': 'analysis_explanation', 'text': partial})}\n\n"
                            await asyncio.sleep(0.025)

                    # 4. Missing keywords — one per event
                    for kw in analysis_data.get("missing_keywords") or []:
                        yield f"data: {json.dumps({'event': 'analysis_keyword', 'keyword': kw})}\n\n"
                        await asyncio.sleep(0.06)

                    # 5. Negative points — one per event
                    for pt in analysis_data.get("negative_points") or []:
                        yield f"data: {json.dumps({'event': 'analysis_negative', 'text': pt})}\n\n"
                        await asyncio.sleep(0.08)

                    # 6. Improvements — one per event
                    for imp in analysis_data.get("potential_improvements") or []:
                        yield f"data: {json.dumps({'event': 'analysis_improvement', 'text': imp})}\n\n"
                        await asyncio.sleep(0.08)

                    # 7. Done — triggers UI to flip to success state
                    yield f"data: {json.dumps({'event': 'analysis_done'})}\n\n"
                else:
                    yield f"data: {json.dumps({'event': 'analysis_done'})}\n\n"
            elif "rewrite_resume" in event:
                yield f"data: {json.dumps({'event': 'progress', 'step': 'rewrite_resume', 'message': 'Finished rewriting resume...'})}\n\n"
            elif "rewrite_latex" in event:
                data = event["rewrite_latex"]
                latex_code = data.get("latex_code", "")
                pdf_base64 = data.get("pdf_base64", "")
                error_msg = data.get("error", None)

                resume_id = None
                if latex_code and not latex_code.startswith("Error:") and not error_msg:
                    try:
                        changes_content = data.get("changes_content")
                        content_dict = None
                        if changes_content:
                            if hasattr(changes_content, "model_dump"):
                                content_dict = changes_content.model_dump()
                            elif isinstance(changes_content, dict):
                                content_dict = changes_content

                        resolved_label = label
                        if not resolved_label or not resolved_label.strip():
                            company_name = "Company"
                            if analysis_data and isinstance(analysis_data, dict):
                                company_name = analysis_data.get(
                                    "company_name", "Company"
                                )

                            # Clean up name & company name to form a nice slug
                            clean_name = "".join(
                                c
                                for c in user.name
                                if c.isalnum() or c in (" ", "_", "-")
                            ).strip()
                            clean_company = "".join(
                                c
                                for c in company_name
                                if c.isalnum() or c in (" ", "_", "-")
                            ).strip()

                            # Remove spaces to make it direct {Name}{CompanyName} style with underscore
                            clean_name = clean_name.replace(" ", "")
                            clean_company = clean_company.replace(" ", "")

                            if not clean_name:
                                clean_name = "User"
                            if not clean_company:
                                clean_company = "Company"

                            resolved_label = f"{clean_name}_{clean_company}"

                        resume = Resume(
                            user_id=user.id,
                            label=resolved_label,
                            jd_snippet=jd,
                            content=content_dict,
                            tex_source=latex_code,
                            pdf_url=pdf_base64,
                            template_id=initial_state.get("template_id"),
                            created_at=datetime.utcnow(),
                            updated_at=datetime.utcnow(),
                        )
                        db.add(resume)
                        await db.commit()
                        await db.refresh(resume)
                        resume_id = resume.id
                    except Exception as db_err:
                        print(f"Failed to save resume to DB: {db_err}")

                payload = {
                    "event": "complete",
                    "message": "Done!",
                    "latexCode": latex_code,
                    "pdfUrl": pdf_base64,
                }
                if error_msg:
                    payload["error"] = error_msg
                if resume_id is not None:
                    payload["resumeId"] = resume_id

                yield f"data: {json.dumps(payload)}\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")
