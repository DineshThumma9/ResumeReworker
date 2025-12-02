
from pydantic import BaseModel, Field
from typing import Dict, List, Optional
from typing_extensions import TypedDict

class ResumeAnalysis(BaseModel):
    score: int = Field(description="How well resume scores against job description (0-100)", ge=0, le=100)
    match: bool = Field(description="Does user's skill set justify or align with the job description domain")
    match_explanation: str = Field(description="Detailed explanation of how the resume matches the job description", default="")
    missing_keywords: List[str] = Field(description="Keywords included in job description but not mentioned in resume", default_factory=list)
    negative_points: List[str] = Field(description="Things which are holding the resume back", default_factory=list)
    potential_improvements: List[str] = Field(description="What can be done to improve this resume", default_factory=list)
    resume_quality: str = Field(description="Overall quality of the resume in terms of structure, readability, and ATS-friendliness", default="")
    urgency: Optional[str] = Field(description="If deadline is mentioned, urgency to submit from current date and time", default=None)






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



class Education(BaseModel):
    institution: str = Field("Institution", description="Institution name")
    year:Optional[str] = Field("Year", description="Year of education")
    gpa:Optional[str] = Field("GPA", description="GPA of education")
    course:str = Field("Course", description="Course name")



class Experience(BaseModel):
    company: str = Field("Company", description="Company name")
    role: str = Field("Role", description="Role/Position held")
    duration: str = Field("Duration", description="Duration of employment")
    responsibilities: List[str] = Field(
        description="Key responsibilities and achievements",
        default_factory=list
    )

class Skill(BaseModel):
    skill: str = Field("Skill", description="Skill name")
    skill_set:List[str] = Field(description="Skill set name")



class Details(BaseModel):
    name: str = Field(description="Full name of the candidate")
    profile_summary: Optional[str] = Field(
        description="Professional summary/objective statement for the resume keep it short and simple and don't go overboard and write paragraphs",   
    )
    contact:Optional[str] = Field(
        description="Contact information as a single string (phone)",
    )
    email:Optional[str] = Field(
        description="Email address",
    )
    linkedin:Optional[str] = Field(
        description="LinkedIn profile URL",
    )
    leetcode:Optional[str] = Field(
        description="LeetCode profile URL",
    )
    codechef:Optional[str] = Field(
        description="CodeChef profile URL",
    )
    location:Optional[str] = Field(
        description="Location of the candidate",   
    )
    github:Optional[str] = Field(
        description="GitHub profile URL",
    )
    portfolio:Optional[str] = Field(
        description="Portfolio website URL",
    )
    profile_links: Dict[str, str] = Field(
        description="""Extract ALL personal contact details and professional profile links with their COMPLETE URLs as values and platform names as keys. 
        Expected keys: phone, email, github, linkedin, leetcode, portfolio, website.
        For URLs, include the full link (e.g., 'https://github.com/username', 'https://linkedin.com/in/username').
        For email, include the full email address.
        For phone, include the complete phone number.
        Example: {"phone": "+1234567890", "email": "user@email.com", "github": "https://github.com/username", "linkedin": "https://linkedin.com/in/username"}""",  
        default_factory=dict
    )
    

class RewriteResume(BaseModel):
    """Structured content for rewritten resume"""

    details: Details = Field(
        description="Personal details and profile summary"
    )
    

    education: List[Education] = Field(
        description="Education entries (degree, institution, year, GPA if applicable)",
        default_factory=list
    )
    
    experience:Optional[List[Experience]] = Field(
        description="Experience (startups,companies etc..)",
        default_factory=list
    )

    technical_skills: List[Skill] = Field(
        description="Technical skills categorized (e.g., 'Languages: Python, Java')",
        default_factory=list
    )

    projects: List[Project] = Field(
        description="Project details with structured information",
        default_factory=list
    )

    coursework: Optional[List[str]] = Field(
        description="Relevant coursework or academic projects",
        default_factory=list
    )
    
    achivements: Optional[List[str]] = Field(
        description="Achievements, awards, and certifications",
        default_factory=list
    )
    

    hackathons_and_certificates: Optional[List[str]] = Field(
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
    tone:str
    exclude_sections:Dict[str, bool]
    output_path :str ="/output"