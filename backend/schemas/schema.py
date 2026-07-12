"""
schema.py — backward-compatible re-export shim
------------------------------------------------
All schemas are now split into focused domain modules:
  - schemas.resume_schema   → AI workflow models (RewriteResume, Details, JudgeResume, …)
  - schemas.auth_schema     → Authentication & user profile models
  - schemas.resume_request_schema → Resume CRUD request/response models

This file re-exports everything so existing `from schemas.schema import X` imports
continue to work without modification.
"""

# ruff: noqa: F401

from schemas.auth_schema import (
    API_KEY_REQUEST,
    API_KEY_RESPONSE,
    GoogleExchangeBody,
    LoginBody,
    ProfileOut,
    ProfileUpdate,
    SignupBody,
)
from schemas.resume_request_schema import (
    AnalyzeRequest,
    CompileRequest,
    MaskDetails,
    ModifyRequest,
    PaginatedResume,
    PaginatedTemplateResponse,
    ResumeCreate,
    ResumeOut,
    ResumeUpdate,
    TemplateCreate,
    TemplateOut,
    TemplateUpdate,
)
from schemas.resume_schema import (
    BatchedRewriteResponse,
    BulletRewriteOutput,
    Details,
    Education,
    Experience,
    JudgeResume,
    ProfileSummary,
    Project,
    ResumeAnalysis,
    ResumeState,
    RewriteResume,
    Skill,
)

__all__ = [
    # resume_schema
    "BatchedRewriteResponse",
    "BulletRewriteOutput",
    "Details",
    "Education",
    "Experience",
    "JudgeResume",
    "ProfileSummary",
    "Project",
    "ResumeAnalysis",
    "ResumeState",
    "RewriteResume",
    "Skill",
    # auth_schema
    "API_KEY_REQUEST",
    "API_KEY_RESPONSE",
    "GoogleExchangeBody",
    "LoginBody",
    "ProfileOut",
    "ProfileUpdate",
    "SignupBody",
    # resume_request_schema
    "AnalyzeRequest",
    "CompileRequest",
    "MaskDetails",
    "ModifyRequest",
    "PaginatedResume",
    "PaginatedTemplateResponse",
    "ResumeCreate",
    "ResumeOut",
    "ResumeUpdate",
    "TemplateCreate",
    "TemplateOut",
    "TemplateUpdate",
]
