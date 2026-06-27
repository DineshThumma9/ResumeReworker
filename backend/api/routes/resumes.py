import json
from typing import Annotated

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from core.database import get_session
from services.workflow import ResumeWorkflowService
from services.auth_service import AuthService

from models.models import Resume
from schemas.schema import ResumeOut, PaginatedResume
from services.resume_service import CurrentUser

router = APIRouter(prefix="/resumes", tags=["resumes"])

DB = Annotated[AsyncSession, Depends(get_session)]

from sqlalchemy import func

@router.get("/resumes", response_model=PaginatedResume)
async def get_resumes(user: CurrentUser, db: DB, skip: int = 0, limit: int = 10):
    """List all resumes for the authenticated user."""
    result = await db.execute(
        select(Resume)
        .where(Resume.user_id == user.id)
        .order_by(Resume.updated_at.desc())
        .offset(skip)
        .limit(limit)
    )
    resumes = result.scalars().all()
    
    count_result = await db.execute(
        select(func.count(Resume.id)).where(Resume.user_id == user.id)
    )
    total_count = count_result.scalar_one()
    
    return PaginatedResume(
        resumes=resumes,
        skip=skip,
        limit=limit,
        total_count=total_count
    )


@router.get("/resumes/{resume_id}", response_model=ResumeOut)
async def get_resume(resume_id: int, user: CurrentUser, db: DB):
    result = await db.execute(
        select(Resume).where(Resume.id == resume_id, Resume.user_id == user.id)
    )
    resume = result.scalar_one_or_none()
    if not resume:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Resume not found")
    return resume


@router.delete("/resumes/{resume_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_resume(resume_id: int, user: CurrentUser, db: DB):
    result = await db.execute(
        select(Resume).where(Resume.id == resume_id, Resume.user_id == user.id)
    )
    resume = result.scalar_one_or_none()
    if not resume:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Resume not found")
    await db.delete(resume)


@router.put("/resumes/{resume_id}/render")
async def render_resume(resume_id: int, user: CurrentUser, db: DB, template_id: str = "jake"):
    """Re-render with a different template without re-running AI."""
    # TODO: load Resume.content, feed to template engine, recompile LaTeX
    return {"status": "not_implemented"}


@router.post("/analyze")
async def analyze(
    user: CurrentUser,
    db: DB,
    jd: str = Form(...),
    label: str = Form(...),
    tone: str = Form("Professional"),
    template_id: str = Form("jake"),
    provider: str = Form("groq"),
    model: str = Form("llama-3.3-70b-versatile"),
    exclude_sections: str = Form("{}"),
    resume_file: UploadFile = File(...),
):
    """
    Main AI workflow. Streams progress as Server-Sent Events.
    Events: progress | complete | error
    """
    pdf_bytes = await resume_file.read()
    
    async def event_stream():
        import fitz
        try:
            doc = fitz.open(stream=pdf_bytes, filetype="pdf")
            resume_text = ""
            for page in doc:
                resume_text += page.get_text()
        except Exception as e:
            yield f"data: {json.dumps({'event': 'error', 'message': f'Failed to read PDF: {str(e)}'})}\n\n"
            return
        
        auth_service = AuthService(db)
        api_key = ""
        try:
            api_key = await auth_service.get_api_key(provider, user)
        except Exception:
            pass
            
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
            "output_path": "/output"
        }
        
        service = ResumeWorkflowService()
        graph = service.graph
        
        async for event in graph.astream(initial_state, stream_mode="updates"):
            if "match_jd" in event:
                yield f"data: {json.dumps({'event': 'progress', 'step': 'match_jd', 'message': 'Finished matching JD...'})}\n\n"
            elif "rewrite_resume" in event:
                yield f"data: {json.dumps({'event': 'progress', 'step': 'rewrite_resume', 'message': 'Finished rewriting resume...'})}\n\n"
            elif "rewrite_latex" in event:
                data = event["rewrite_latex"]
                latex_code = data.get("latex_code", "")
                pdf_base64 = data.get("pdf_base64", "")
                
                payload = {
                    'event': 'complete', 
                    'message': 'Done!',
                    'latexCode': latex_code,
                    'pdfUrl': pdf_base64
                }
                yield f"data: {json.dumps(payload)}\n\n"
                
    return StreamingResponse(event_stream(), media_type="text/event-stream")
