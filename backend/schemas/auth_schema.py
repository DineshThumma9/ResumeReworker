"""
auth_schema.py
--------------
Schemas for authentication and user profile endpoints.
"""

from typing import Optional

from pydantic import BaseModel


class SignupBody(BaseModel):
    username: str
    name: str
    email: str
    password: str


class LoginBody(BaseModel):
    email_or_username: str
    password: str


class GoogleExchangeBody(BaseModel):
    code: str


class ProfileUpdate(BaseModel):
    name: str
    email: str
    github: Optional[str] = None
    linkedin: Optional[str] = None
    website: Optional[str] = None
    location: Optional[str] = None
    phone: Optional[str] = None
    raw_resume: Optional[str] = None


class ProfileOut(BaseModel):
    id: int
    username: str
    name: str
    email: str
    github: Optional[str] = None
    linkedin: Optional[str] = None
    website: Optional[str] = None
    location: Optional[str] = None
    phone: Optional[str] = None
    raw_resume: Optional[str] = None


class API_KEY_REQUEST(BaseModel):
    api_provider: str
    api_key: str


class API_KEY_RESPONSE(BaseModel):
    provider: str
    encrypted_key: str
