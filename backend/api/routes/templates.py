from typing import Annotated

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import func, or_, select

from core.database import get_session
from models.models import Template
from schemas.schema import (
    PaginatedTemplateResponse,
    TemplateCreate,
    TemplateOut,
    TemplateUpdate,
)
from services.preview import generate_template_preview_task
from services.resume_service import CurrentUser

router = APIRouter(prefix="/templates", tags=["templates"])

DB = Annotated[AsyncSession, Depends(get_session)]


@router.get("", response_model=PaginatedTemplateResponse)
async def list_templates(
    current_user: CurrentUser, db: DB, skip: int = 0, limit: int = 100
):
    query = select(Template).where(
        or_(Template.is_builtin, Template.user_id == current_user.id)
    )
    result = await db.execute(query.offset(skip).limit(limit))
    templates = result.scalars().all()

    count_query = select(func.count()).select_from(query.subquery())
    count_result = await db.execute(count_query)
    total_count = count_result.scalar() or 0

    return PaginatedTemplateResponse(
        templates=templates,  # type: ignore
        skip=skip,
        limit=limit,
        total_count=total_count,  # type: ignore
    )


@router.post("", response_model=TemplateOut)
async def create_template(
    body: TemplateCreate,
    current_user: CurrentUser,
    db: DB,
    background_tasks: BackgroundTasks,
):
    template = Template(
        name=body.name, tex_source=body.tex_source, user_id=current_user.id
    )
    db.add(template)
    await db.commit()
    await db.refresh(template)
    background_tasks.add_task(generate_template_preview_task, template.id)  # type: ignore
    return template


@router.put("/{template_id}", response_model=TemplateOut)
async def update_template(
    template_id: int,
    body: TemplateUpdate,
    current_user: CurrentUser,
    db: DB,
    background_tasks: BackgroundTasks,
):
    result = await db.execute(
        select(Template).where(
            Template.id == template_id, Template.user_id == current_user.id
        )
    )
    template = result.scalar_one_or_none()
    if not template:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Template not found")

    template.name = body.name
    template.tex_source = body.tex_source
    await db.commit()
    await db.refresh(template)
    background_tasks.add_task(generate_template_preview_task, template.id)  # type: ignore
    return template


@router.delete("/{template_id}")
async def delete_template(template_id: int, current_user: CurrentUser, db: DB):
    result = await db.execute(
        select(Template).where(
            Template.id == template_id, Template.user_id == current_user.id
        )
    )
    template = result.scalar_one_or_none()
    if not template:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Template not found")

    await db.delete(template)
    await db.commit()
    return {"message": "Template deleted"}
