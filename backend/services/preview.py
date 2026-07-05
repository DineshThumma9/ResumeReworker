import logging

from sqlalchemy import select

from core.database import AsyncSessionLocal
from models.models import Template
from services.renderer import render_resume_template_from_string
from services.storage import upload_pdf_to_cloudinary
from services.workflow import ResumeWorkflowService
from utils.constants import DUMMY_RESUME_DATA

logger = logging.getLogger(__name__)


async def generate_template_preview_task(template_id: int):
    """
    Background task to generate a preview image for a template.
    1. Fetches the template from DB.
    2. Renders the template with dummy data.
    3. Compiles the LaTeX to PDF.
    4. Uploads the PDF to Cloudinary to get a preview image URL.
    5. Updates the template in the DB with the preview URL.
    """
    logger.info(f"Starting preview generation for template_id: {template_id}")
    try:
        async with AsyncSessionLocal() as session:
            # 1. Fetch template
            result = await session.execute(
                select(Template).where(Template.id == template_id)  # type: ignore
            )
            template = result.scalar_one_or_none()
            if not template:
                logger.error(
                    f"Template {template_id} not found for preview generation."
                )
                return

            # 2. Render LaTeX
            tex_source = template.tex_source
            latex_code = render_resume_template_from_string(
                tex_source, DUMMY_RESUME_DATA
            )

            # 3. Compile to PDF
            workflow_service = ResumeWorkflowService()
            filename = f"template_{template_id}.pdf"
            pdf_bytes = await workflow_service.latex_to_pdf(latex_code, filename)

            if not pdf_bytes:
                logger.error(
                    f"PDF compilation failed for template {template_id}, resulting bytes are empty."
                )
                return

            # 4. Upload to Cloudinary to get preview
            upload_res = await upload_pdf_to_cloudinary(pdf_bytes, filename)
            preview_url = upload_res.get("preview_image_url")

            if not preview_url:
                logger.error(f"Cloudinary upload failed for template {template_id}")
                return

            # 5. Update DB
            logger.info(
                f"Successfully generated Cloudinary preview URL for template {template_id}: {preview_url}"
            )
            template.preview_url = preview_url
            session.add(template)
            await session.commit()

    except Exception as e:
        logger.error(
            f"Exception during preview generation for template {template_id}: {e}",
            exc_info=True,
        )
