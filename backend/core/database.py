"""
backend/db.py

Async SQLAlchemy engine and session setup.
Tables are created on app startup via create_tables().
"""

import os
from typing import AsyncGenerator

from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlmodel import SQLModel
from core.config import settings
load_dotenv()


# echo=True logs all SQL — turn off in prod
engine = create_async_engine(settings.database_url, echo=True, future=True)

AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency — yields an async DB session per request."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


from sqlalchemy import text
from sqlmodel import select
import models  # noqa: F401
from models.models import Template

async def seed_templates(session: AsyncSession):
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    templates_dir = os.path.join(base_dir, 'templates')
    
    builtin_templates = ['jakes1.tex', 'jakes2.tex', 'jakes3.tex']
    
    for template_filename in builtin_templates:
        template_name = template_filename.replace('.tex', '')
        
        # Check if exists
        result = await session.execute(
            select(Template).where(Template.name == template_name, Template.is_builtin == True)
        )
        existing = result.scalar_one_or_none()
        
        if not existing:
            template_path = os.path.join(templates_dir, template_filename)
            if os.path.exists(template_path):
                with open(template_path, 'r', encoding='utf-8') as f:
                    tex_source = f.read()
                
                template = Template(
                    name=template_name,
                    tex_source=tex_source,
                    is_builtin=True
                )
                session.add(template)
    
    await session.commit()

async def create_tables() -> None:
    """Called on app startup. Creates all tables if they don't exist."""
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
        
        # Add new columns to users table if they don't exist
        for col in ["github", "linkedin", "website", "location", "phone", "raw_resume"]:
            try:
                # Use subqueries or try/catch around alter table statements for compatibility
                await conn.execute(text(f"ALTER TABLE users ADD COLUMN IF NOT EXISTS {col} TEXT"))
            except Exception:
                try:
                    await conn.execute(text(f"ALTER TABLE users ADD COLUMN {col} TEXT"))
                except Exception:
                    pass
    
    # Seed builtin templates
    async with AsyncSessionLocal() as session:
        await seed_templates(session)
