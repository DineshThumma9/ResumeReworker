"""
resume_request_schema.py
------------------------
Schemas for resume CRUD API request/response bodies.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class ResumeCreate(BaseModel):
    label: str
    tex_source: str
    jd_snippet: Optional[str] = None
    template_id: Optional[int] = None
    pdf_url: Optional[str] = None
    content: Optional[dict] = None


class ResumeUpdate(BaseModel):
    label: Optional[str] = None
    tex_source: Optional[str] = None
    pdf_url: Optional[str] = None


class ResumeOut(BaseModel):
    id: int
    label: str
    jd_snippet: Optional[str] = None
    template_id: Optional[int] = None
    tex_source: Optional[str] = None
    pdf_url: Optional[str] = None
    preview_url: Optional[str] = None
    created_at: datetime = Field(default=datetime.now())
    updated_at: datetime = Field(default=datetime.now())
    content: Optional[Dict[str, Any]] = None

    class Config:
        from_attributes = True


class PaginatedResume(BaseModel):
    resumes: List[ResumeOut]
    skip: int
    limit: int
    total_count: int

    class Config:
        from_attributes = True


class AnalyzeRequest(BaseModel):
    jd: str
    tone: str = Field(default="Professional")
    exclude_sections: Dict[str, bool] = Field(default_factory=dict)
    template_id: str = Field(default="jake")
    label: Optional[str] = None


class CompileRequest(BaseModel):
    latex_code: str
    id: Optional[int] = None


class ModifyRequest(BaseModel):
    latex_code: str
    instruction: str
    provider: str = "groq"
    model: str = "llama-3.3-70b-versatile"


class MaskDetails(BaseModel):
    name: Optional[bool] = True
    email: Optional[bool] = True
    phone: Optional[bool] = True
    location: Optional[bool] = True
    github: Optional[bool] = True
    linkedin: Optional[bool] = True
    leetcode: Optional[bool] = True
    portfolio: Optional[bool] = True
    project_name: Optional[bool] = True
    company_name: Optional[bool] = True
    education: Optional[bool] = True
    latex_code: Optional[str] = None


class TemplateOut(BaseModel):
    id: int
    name: str
    tex_source: str
    preview_url: Optional[str] = None
    is_builtin: bool
    created_at: datetime

    class Config:
        from_attributes = True


class PaginatedTemplateResponse(BaseModel):
    templates: List[TemplateOut]
    skip: int
    limit: int
    total_count: int

    class Config:
        from_attributes = True


class TemplateCreate(BaseModel):
    name: str
    tex_source: str


class TemplateUpdate(BaseModel):
    name: str
    tex_source: str
