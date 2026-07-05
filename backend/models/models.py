from datetime import datetime
from typing import Optional

from sqlalchemy import Column, Text
from sqlalchemy.dialects.postgresql import JSON
from sqlmodel import Field, SQLModel


class User(SQLModel, table=True):
    __tablename__ = "users"  # type: ignore

    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(index=True, unique=True)
    hashed_password: str
    name: str
    email: str = Field(index=True, unique=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    github: Optional[str] = Field(default=None, sa_column=Column(Text))
    linkedin: Optional[str] = Field(default=None, sa_column=Column(Text))
    website: Optional[str] = Field(default=None, sa_column=Column(Text))
    location: Optional[str] = Field(default=None, sa_column=Column(Text))
    phone: Optional[str] = Field(default=None, sa_column=Column(Text))
    raw_resume: Optional[str] = Field(default=None, sa_column=Column(Text))


class Template(SQLModel, table=True):
    __tablename__ = "templates"  # type: ignore

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: Optional[int] = Field(default=None, foreign_key="users.id")
    name: str
    tex_source: str = Field(sa_column=Column(Text))
    is_builtin: bool = Field(default=False)
    preview_url: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)


class Resume(SQLModel, table=True):
    __tablename__ = "resumes"  # type: ignore

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: Optional[int] = Field(default=None, foreign_key="users.id")
    label: str
    template_id: Optional[int] = Field(
        default=None, foreign_key="templates.id", ondelete="SET NULL"
    )
    jd_snippet: Optional[str] = None
    content: Optional[dict] = Field(default=None, sa_column=Column(JSON))
    tex_source: Optional[str] = Field(default=None, sa_column=Column(Text))
    pdf_url: Optional[str] = None
    preview_url: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class ShareLink(SQLModel, table=True):
    __tablename__ = "share_links"  # type: ignore

    id: Optional[int] = Field(default=None, primary_key=True)
    # resume_id:  int           = Field(foreign_key="resumes.id")
    # Actually, for an anonymous share, we just want to save the tex_source and compiled pdf_url,
    # instead of linking to a resume directly? Wait, if we link to a resume_id, that's fine too. But we generated an ANONYMIZED tex_source.
    # Let's save the anonymized tex_source directly in ShareLink.
    tex_source: str = Field(sa_column=Column(Text))
    pdf_url: Optional[str] = None
    token: str = Field(unique=True)
    is_active: bool = Field(default=True)
    view_count: int = Field(default=0)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class APIKEYS(SQLModel, table=True):
    __tablename__ = "api_keys"  # type: ignore
    user_id: int = Field(foreign_key="users.id", ondelete="CASCADE", primary_key=True)
    provider: str = Field(primary_key=True, index=True)
    encrypted_key: str


class UserLLMConfig(SQLModel, table=True):
    __tablename__ = "config"  # type: ignore
    user_id: int = Field(foreign_key="users.id", ondelete="CASCADE", primary_key=True)
    provider: str = Field(index=True)
    model: str
