import json
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from core.database import get_session
from models.models import Resume, Template
from schemas.schema import MaskDetails
from services.renderer import render_resume_template, render_resume_template_from_string
from services.resume_service import CurrentUser, mask_resume
from services.workflow import ResumeWorkflowService

router = APIRouter(prefix="/share", tags=["share"])

DB = Annotated[AsyncSession, Depends(get_session)]


@router.post("/{resume_id}/download-anonymous")
async def download_anonymous(
    resume_id: int,
    mask_details: MaskDetails,
    user: CurrentUser,
    db: DB,
):
    """
    Mask personal identifiable information (PII) on a resume,
    compile the masked resume to PDF, and download the binary directly.
    """
    # 1. Fetch the resume from DB
    result = await db.execute(
        select(Resume).where(Resume.id == resume_id, Resume.user_id == user.id)
    )
    resume = result.scalar_one_or_none()
    if not resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Resume not found"
        )

    # 2. Get the structured content
    content = resume.content
    if not content:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Resume structured content not found. Please re-run analysis first.",
        )

    # 3. Mask the structured content
    try:
        masked_content_json = await mask_resume(content, mask_details)
        masked_content = json.loads(masked_content_json)
        if masked_content is not None and isinstance(masked_content, dict):
            masked_content["jd"] = resume.jd_snippet
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to mask resume data: {str(e)}",
        )

    # 4. Render to LaTeX code
    template_name = "jakes1.tex"
    try:
        if mask_details.latex_code:
            from services.resume_service import mask_latex

            latex_code = mask_latex(mask_details.latex_code, content, mask_details)
        elif resume.template_id:
            t_result = await db.execute(
                select(Template).where(Template.id == resume.template_id)
            )
            template = t_result.scalar_one_or_none()
            if template:
                latex_code = render_resume_template_from_string(
                    template.tex_source, masked_content
                )
            else:
                latex_code = render_resume_template(template_name, masked_content)
        else:
            latex_code = render_resume_template(template_name, masked_content)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Template rendering failed: {str(e)}",
        )

    # 5. Compile LaTeX to PDF
    try:
        service = ResumeWorkflowService()
        pdf_bytes = await service.latex_to_pdf(latex_code, "resume.pdf")
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"LaTeX compilation failed during masking: {str(e)}",
        )

    # 6. Stream/Download the resulting PDF directly
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename=anonymous_resume_{resume_id}.pdf"
        },
    )
