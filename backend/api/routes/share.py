from typing import Annotated

from fastapi import APIRouter, Depends
from core.database import get_session
from services.resume_service import CurrentUser
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/share", tags=["share"])

DB = Annotated[AsyncSession, Depends(get_session)]


from schemas.schema import MaskDetails
from services.resume_service import mask_resume


@router.post("/share/{resume_id}")
async def share_anomyous(
    resume_content, user: CurrentUser, db: DB, mask_details: MaskDetails
):
    return await mask_resume(resume_content, mask_details)
