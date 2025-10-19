
from typing import Optional, List
from pydantic import BaseModel,Field

class ResumeAnalysis(BaseModel):
    """Model for analyzing resume against job description"""

    score: int = Field(
        description="How well resume scores against job description (0-100)",
        ge=0,
        le=100
    )

    match: bool = Field(
        description="Does user's skill set justify or align with the job description domain"
    )

    match_explanation: str = Field(
        description="Detailed explanation of how the resume matches the job description",
        default=""
    )

    missing_keywords: List[str] = Field(
        description="Keywords included in job description but not mentioned in resume",
        default_factory=list
    )

    negative_points: List[str] = Field(
        description="Things which are holding the resume back",
        default_factory=list
    )

    potential_improvements: List[str] = Field(
        description="What can be done to improve this resume",
        default_factory=list
    )

    urgency: Optional[str] = Field(
        description="If deadline is mentioned, urgency to submit from current date and time",
        default=None
    )



from pydantic import BaseModel, Field
from typing import List, Optional
from typing_extensions import TypedDict

# Supporting model for better structure
class Project(BaseModel):
    """Individual project details"""
    name: str = Field(description="Project name/title")
    description: str = Field(description="Brief project description")
    technologies: List[str] = Field(
        description="Technologies/tools used in the project",
        default_factory=list
    )
    highlights: List[str] = Field(
        description="Key achievements or bullet points",
        default_factory=list
    )


class RewriteResume(BaseModel):
    """Structured content for rewritten resume"""

    profile_summary: str = Field(
        description="Professional summary/objective statement for the resume"
    )

    education: List[str] = Field(
        description="Education entries (degree, institution, year, GPA if applicable)",
        default_factory=list
    )

    technical_skills: List[str] = Field(
        description="Technical skills categorized (e.g., 'Languages: Python, Java')",
        default_factory=list
    )

    projects: List[Project] = Field(
        description="Project details with structured information",
        default_factory=list
    )

    coursework: List[str] = Field(
        description="Relevant coursework or academic projects",
        default_factory=list
    )

    hackathons_and_certificates: List[str] = Field(
        description="Hackathon participations, awards, and certifications",
        default_factory=list
    )





class ResumeState(TypedDict):
    """State management for resume processing workflow"""
    jd: str  # Job description
    resume: str  # Original resume content
    analysis: ResumeAnalysis  # Analysis results (FIXED TYPO)
    changes_content: RewriteResume  # Rewritten resume content
    latex_code: str  # Generated LaTeX code for resume
    output_path :str ="/output"