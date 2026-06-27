from pydantic import BaseModel, Field
from typing import Any, Dict, List, Optional
from typing_extensions import TypedDict
from datetime import datetime


class ResumeAnalysis(BaseModel):
    score: int = Field(
        description="How well resume scores against job description (0-100)",
        ge=0,
        le=100,
    )
    match: bool = Field(
        description="Does user's skill set justify or align with the job description domain"
    )
    match_explanation: str = Field(
        description="Detailed explanation of how the resume matches the job description",
        default="",
    )
    missing_keywords: List[str] = Field(
        description="Keywords included in job description but not mentioned in resume",
        default_factory=list,
    )
    negative_points: List[str] = Field(
        description="Things which are holding the resume back", default_factory=list
    )
    potential_improvements: List[str] = Field(
        description="What can be done to improve this resume", default_factory=list
    )
    resume_quality: str = Field(
        description="Overall quality of the resume in terms of structure, readability, and ATS-friendliness",
        default="",
    )
    urgency: Optional[str] = Field(
        description="If deadline is mentioned, urgency to submit from current date and time",
        default=None,
    )


class Project(BaseModel):
    """Individual project details"""

    name: Optional[str] = Field(description="Project name/title", default="")
    description: Optional[str] = Field(
        description="Brief project description", default=""
    )
    date: Optional[str] = Field(
        description="Date or duration of the project", default=""
    )
    link: Optional[str] = Field(description="URL or link to the project", default="")
    technologies: List[str] = Field(
        description="Technologies/tools used in the project", default_factory=list
    )
    highlights: List[str] = Field(
        description="Key achievements or bullet points", default_factory=list
    )


class Education(BaseModel):
    institution: Optional[str] = Field(default="", description="Institution name")
    location: Optional[str] = Field(
        default="", description="Location of the institution"
    )
    year: Optional[str] = Field(default="", description="Year of education")
    gpa: Optional[str] = Field(default="", description="GPA of education")
    course: Optional[str] = Field(default="", description="Course name")


class Experience(BaseModel):
    company: Optional[str] = Field(default="", description="Company name")
    location: Optional[str] = Field(default="", description="Location of the company")
    role: Optional[str] = Field(default="", description="Role/Position held")
    duration: Optional[str] = Field(default="", description="Duration of employment")
    responsibilities: List[str] = Field(
        description="Key responsibilities and achievements", default_factory=list
    )


class Skill(BaseModel):
    category: Optional[str] = Field(
        default="",
        description="Skill category name (e.g., 'Programming Languages', 'Frameworks', 'Tools')",
    )
    skills: List[str] = Field(
        description="List of specific skills in this category (e.g., ['Python', 'Java', 'C++'])"
    )


class Details(BaseModel):
    name: str = Field(description="Full name of the candidate")
    profile_summary: Optional[str] = Field(
        default="",
        description="Professional summary/objective statement for the resume keep it short and simple and don't go overboard and write paragraphs",
    )
    contact: Optional[str] = Field(
        default="",
        description="Contact information as a single string (phone)",
    )
    email: Optional[str] = Field(
        default="",
        description="Email address",
    )
    linkedin: Optional[str] = Field(
        default="",
        description="LinkedIn profile URL",
    )
    leetcode: Optional[str] = Field(
        default="",
        description="LeetCode profile URL",
    )
    codechef: Optional[str] = Field(
        default="",
        description="CodeChef profile URL",
    )
    location: Optional[str] = Field(
        default="",
        description="Location of the candidate",
    )
    github: Optional[str] = Field(
        default="",
        description="GitHub profile URL",
    )
    portfolio: Optional[str] = Field(
        default="",
        description="Portfolio website URL",
    )
    profile_links: Dict[str, Optional[str]] = Field(
        description="""Extract ALL personal contact details and professional profile links with their COMPLETE URLs as values and platform names as keys. 
        Expected keys: phone, email, github, linkedin, leetcode, portfolio, website.
        For URLs, include the full link (e.g., 'https://github.com/username', 'https://linkedin.com/in/username').
        For email, include the full email address.
        For phone, include the complete phone number.
        Example: {"phone": "+1234567890", "email": "user@email.com", "github": "https://github.com/username", "linkedin": "https://linkedin.com/in/username"}""",
        default_factory=dict,
    )


class RewriteResume(BaseModel):
    """Structured content for rewritten resume"""

    details: Details = Field(description="Personal details and profile summary")

    education: Optional[List[Education]] = Field(
        description="List of education entries (must match Education schema precisely)",
        default=None,
    )

    experience: Optional[List[Experience]] = Field(
        description="List of work experiences (must match Experience schema precisely)",
        default=None,
    )

    technical_skills: Optional[List[Skill]] = Field(
        description="List of technical skills categorized (e.g., 'Languages: Python, Java')",
        default=None,
    )

    projects: Optional[List[Project]] = Field(
        description="List of projects (must match Project schema precisely)",
        default=None,
    )

    coursework: Optional[List[str]] = Field(
        description="List of relevant coursework or academic projects as strings",
        default=None,
    )

    achivements: Optional[List[str]] = Field(
        description="List of achievements, awards, and certifications as strings",
        default=None,
    )

    open_source: Optional[List[str]] = Field(
        description="List of open source projects and contributions as strings", default=None
    )

    internships: Optional[List[Experience]] = Field(
        description="List of internships (must match Experience schema precisely)",
        default=None,
    )

    hackathons: Optional[List[str]] = Field(
        description="List of hackathons participated as strings", default=None
    )

    certifications: Optional[List[str]] = Field(
        description="List of certifications obtained as strings", default=None
    )

    extracircular_activities: Optional[List[str]] = Field(
        description="List of extracurricular activities as strings", default=None
    )


class SignupBody(BaseModel):
    username: str
    name: str
    email: str
    password: str


class LoginBody(BaseModel):
    email_or_username: str
    password: str


class AnalyzeRequest(BaseModel):
    jd: str
    tone: str = Field(default="Professional")
    exclude_sections: Dict[str, bool] = Field(default_factory=dict)
    template_id: str = Field(default="jake")
    label: str


class ResumeOut(BaseModel):
    id: int
    label: str
    jd_snippet: Optional[str] = None
    template_id: Optional[int] = None
    pdf_url: Optional[str] = None
    preview_url: Optional[str] = None
    created_at: datetime = Field(default=datetime.now())
    updated_at: datetime = Field(default=datetime.now())

    class Config:
        from_attributes = True


# class ShareLinkOut(BaseModel):
#     """POST /resumes/{id}/share — what we return after creating a share link."""

#     token: str
#     resume_id: int
#     is_active: bool
#     view_count: int


class ResumeState(TypedDict, total=False):
    jd: str  
    resume: str
    analysis: Optional[Any]
    changes_content: Optional[Any]
    latex_code: str
    tone: str
    model: str
    provider: str
    api_key: str
    exclude_sections: Dict[str, bool]
    output_path: str
    pdf_base64: str
    template_source: str


class PaginatedResume(BaseModel):
    resumes: List[ResumeOut]
    skip: int
    limit: int
    total_count: int

    class Config:
        from_attributes = True


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





class API_KEY_REQUEST(BaseModel):
    api_provider: str
    api_key: str


class API_KEY_RESPONSE(BaseModel):
    provider: str
    encrypted_key: str
