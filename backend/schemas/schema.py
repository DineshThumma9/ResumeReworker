import re
from datetime import datetime
from typing import Any, Dict, List, Optional, TypedDict

from pydantic import BaseModel, Field, model_serializer, model_validator


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
    company_name: Optional[str] = Field(
        description="Extract the target company name from the job description if present, otherwise default to 'Company'",
        default="Company",
    )

    @model_validator(mode="before")
    @classmethod
    def clean_fields(cls, data: Any) -> Any:
        if isinstance(data, dict):
            # Clean potential_improvements
            pi = data.get("potential_improvements")
            if isinstance(pi, list):
                cleaned = []
                for item in pi:
                    if isinstance(item, dict):
                        val = (
                            item.get("action")
                            or item.get("improvement")
                            or item.get("text")
                            or (list(item.values())[0] if item.values() else "")
                        )
                        cleaned.append(str(val))
                    else:
                        cleaned.append(str(item))
                data["potential_improvements"] = cleaned

            # Clean negative_points
            np = data.get("negative_points")
            if isinstance(np, list):
                cleaned = []
                for item in np:
                    if isinstance(item, dict):
                        val = (
                            item.get("point")
                            or item.get("issue")
                            or item.get("text")
                            or (list(item.values())[0] if item.values() else "")
                        )
                        cleaned.append(str(val))
                    else:
                        cleaned.append(str(item))
                data["negative_points"] = cleaned
        return data


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


class ProfileSummary(BaseModel):
    profile_summary: Optional[str] = Field(
        default="",
        description=(
            "Professional summary/objective. Rewrite to be ATS-optimized and concise. "
            "MUST be shorter than or equal to the original in word count. "
            "Do NOT expand it into multiple sentences if the original was one sentence."
        ),
    )


class Details(BaseModel):
    name: str = Field(description="Full name of the candidate")
    profile_links: Dict[str, Optional[str]] = Field(
        description=(
            "Dictionary of ALL links and contact info found in the resume. "
            "Keys should be the platform name (e.g., 'github', 'linkedin', 'phone', 'email', "
            "'gitlab', 'medium', 'hackerrank', 'portfolio', 'website', 'location'). "
            "Values are FULL URLs or raw values (e.g., '+91XXXXXXXXXX', 'user@email.com', "
            "'https://github.com/username'). "
            "Scan the ENTIRE resume text for any profile links (GitHub, LinkedIn, GitLab, LeetCode, etc), "
            "mailto:, http/https links, phone numbers, and email addresses. "
            "If a field is not found, set it to null — do NOT omit the key. "
            "NEVER leave this dict empty if the resume has any links or contact info."
        ),
        default_factory=dict,
    )

    @model_validator(mode="before")
    @classmethod
    def extract_links_fallback(cls, data: Any) -> Any:
        """If LLM left profile_links empty/incomplete, regex-scan any raw text fields to fill gaps."""
        if not isinstance(data, dict):
            return data

        links: Dict[str, Optional[str]] = data.get("profile_links") or {}
        
        # Normalize keys in case LLM used the URL as the key
        normalized_links = {}
        for k, v in links.items():
            if not v:
                continue
            k_lower = k.lower()
            if k_lower.startswith("http") or "." in k_lower:
                m = re.search(r"https?://(?:www\.)?([\w\-\.]+)", v)
                if m:
                    domain = m.group(1).lower()
                    if domain.endswith(".com") or domain.endswith(".org") or domain.endswith(".net") or domain.endswith(".io"):
                        domain = domain[:-4]
                    normalized_links[domain] = v
                else:
                    normalized_links[k_lower] = v
            else:
                normalized_links[k_lower] = v
        links = normalized_links

        # Collect raw text to scan (from any field that might contain resume text)
        raw_text = " ".join(str(v) for v in data.values() if isinstance(v, str))

        def _first(pattern: str, text: str) -> Optional[str]:
            m = re.search(pattern, text, re.IGNORECASE)
            return m.group(0) if m else None

        # Generic fallback for any other http/https links
        urls = re.findall(r"https?://(?:www\.)?([\w\-\.]+)[/\w\-\.\?\=\&\%]*", raw_text)
        for domain in urls:
            if domain.endswith(".com"):
                domain = domain[:-4]
            elif domain.endswith(".org") or domain.endswith(".net") or domain.endswith(".io"):
                domain = domain[:-4]
            # normalize domain to generic key, e.g. linkedin, github
            key = domain.lower()
            if key not in links:
                # Find the full match in text
                match = re.search(r"https?://(?:www\.)?" + re.escape(domain) + r"[a-zA-Z]{0,4}[/\w\-\.\?\=\&\%]*", raw_text)
                if match:
                    links[key] = match.group(0)

        # Phone — Indian (+91) and generic
        if not links.get("phone"):
            phone = _first(
                r"(?:\+91[\s\-]?)?[6-9]\d{9}|\+?\d[\d\s\-\.]{8,14}\d", raw_text
            )
            if phone:
                links["phone"] = phone.strip()

        # Email
        if not links.get("email"):
            email = _first(
                r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}", raw_text
            )
            if email:
                links["email"] = email

        data["profile_links"] = links
        return data

    @property
    def contact(self) -> Optional[str]:
        return self.profile_links.get("phone") or ""

    @contact.setter
    def contact(self, val: Optional[str]):
        self.profile_links["phone"] = val

    @property
    def email(self) -> Optional[str]:
        return self.profile_links.get("email") or ""

    @email.setter
    def email(self, val: Optional[str]):
        self.profile_links["email"] = val

    @property
    def other_links(self) -> Dict[str, str]:
        """Returns all links except email, phone, location."""
        return {
            k: v
            for k, v in self.profile_links.items()
            if v and k.lower() not in ["email", "phone", "location", "contact"]
        }

    @property
    def github(self) -> Optional[str]:
        return self.profile_links.get("github") or ""

    @github.setter
    def github(self, val: Optional[str]):
        self.profile_links["github"] = val

    @property
    def linkedin(self) -> Optional[str]:
        return self.profile_links.get("linkedin") or ""

    @linkedin.setter
    def linkedin(self, val: Optional[str]):
        self.profile_links["linkedin"] = val

    @property
    def leetcode(self) -> Optional[str]:
        return self.profile_links.get("leetcode") or ""

    @leetcode.setter
    def leetcode(self, val: Optional[str]):
        self.profile_links["leetcode"] = val

    @property
    def codechef(self) -> Optional[str]:
        return self.profile_links.get("codechef") or ""

    @codechef.setter
    def codechef(self, val: Optional[str]):
        self.profile_links["codechef"] = val

    @property
    def portfolio(self) -> Optional[str]:
        return (
            self.profile_links.get("portfolio")
            or self.profile_links.get("website")
            or ""
        )

    @portfolio.setter
    def portfolio(self, val: Optional[str]):
        self.profile_links["portfolio"] = val

    @property
    def location(self) -> Optional[str]:
        return self.profile_links.get("location") or ""

    @location.setter
    def location(self, val: Optional[str]):
        self.profile_links["location"] = val

    @model_serializer
    def serialize_model(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "profile_links": self.profile_links,
            "contact": self.contact,
            "email": self.email,
            "github": self.github,
            "linkedin": self.linkedin,
            "leetcode": self.leetcode,
            "codechef": self.codechef,
            "portfolio": self.portfolio,
            "location": self.location,
        }


class RewriteResume(BaseModel):
    """Structured content for rewritten resume"""

    profile_summary: Optional[ProfileSummary] = Field(
        description="Professional Summary"
    )

    details: Optional[Details] = Field(description="Personal details")

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
        description=(
            "Achievements, awards, competitive programming stats, and certifications. "
            "Do NOT include open source contributions here — those go in open_source. "
            "Do NOT include hackathons — those go in hackathons."
        ),
        default=None,
    )

    open_source: Optional[List[str]] = Field(
        description=(
            "Open source contributions ONLY — merged PRs, filed issues, maintainer credits. "
            "Each entry is one contribution as a string. "
            "Do NOT include hackathons, certificates, or LeetCode stats here."
        ),
        default=None,
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

    @model_validator(mode="before")
    @classmethod
    def clean_input(cls, data: Any) -> Any:
        if not isinstance(data, dict):
            return data

        # Fix profile_summary if LLM returns a string instead of dict
        if "profile_summary" in data and isinstance(data["profile_summary"], str):
            data["profile_summary"] = {"profile_summary": data["profile_summary"]}

        # 1. Clean technical_skills
        if "technical_skills" in data and data["technical_skills"] is not None:
            ts = data["technical_skills"]
            if isinstance(ts, dict):
                if "technical_skills" in ts:
                    ts = ts["technical_skills"]
                elif "skills" in ts:
                    ts = ts["skills"]
                else:
                    # e.g. {"Languages": "Python, Java", "Frameworks": "React"}
                    ts = [
                        {
                            "category": str(k),
                            "skills": val if isinstance(val, list) else [str(val)],
                        }
                        for k, val in ts.items()
                    ]

            # Now, if ts is a list, clean each item if they are dicts with list values or strings
            if isinstance(ts, list):
                cleaned_ts = []
                for item in ts:
                    if isinstance(item, dict):
                        category = item.get("category") or item.get("name") or ""
                        skills = item.get("skills") or item.get("values") or []
                        if isinstance(skills, str):
                            skills = [s.strip() for s in skills.split(",") if s.strip()]
                        elif not isinstance(skills, list):
                            skills = [str(skills)]
                        cleaned_ts.append(
                            {
                                "category": str(category),
                                "skills": [str(s) for s in skills],
                            }
                        )
                    else:
                        # Fallback if item is just a string or list
                        cleaned_ts.append({"category": "Skills", "skills": [str(item)]})
                data["technical_skills"] = cleaned_ts

        # 2. Clean list of strings fields
        list_fields = [
            "open_source",
            "coursework",
            "achivements",
            "hackathons",
            "certifications",
            "extracircular_activities",
        ]
        for field in list_fields:
            if field in data and data[field] is not None:
                val = data[field]
                # If it's a dictionary (like {"open_source": [...]})
                if isinstance(val, dict):
                    # Check if the field name is a key in the dict
                    if field in val:
                        val = val[field]
                    else:
                        for sub_val in val.values():
                            if isinstance(sub_val, list):
                                val = sub_val
                                break
                        else:
                            val = list(val.values())

                # If it is a list, clean its items to be strings
                if isinstance(val, list):
                    cleaned_list = []
                    for item in val:
                        if isinstance(item, dict):
                            # Extract any string fields or list values
                            name = (
                                item.get("name")
                                or item.get("title")
                                or item.get("description")
                                or item.get("project")
                            )
                            if name:
                                cleaned_list.append(str(name))
                            else:
                                parts = []
                                for sub_item_val in item.values():
                                    if isinstance(sub_item_val, list):
                                        parts.extend(str(x) for x in sub_item_val)
                                    else:
                                        parts.append(str(sub_item_val))
                                cleaned_list.append(" - ".join(parts))
                        elif isinstance(item, list):
                            cleaned_list.append(", ".join(str(x) for x in item))
                        else:
                            cleaned_list.append(str(item))
                    data[field] = cleaned_list
                elif isinstance(val, str):
                    data[field] = [val]

        # Deduplicate open_source and achivements
        if "open_source" in data and "achivements" in data:
            os_items = data.get("open_source") or []
            ach_items = data.get("achivements") or []
            if os_items and ach_items:
                # Remove any achievement that is also in open_source
                os_set = {str(item).lower().strip() for item in os_items}
                new_ach = []
                for ach in ach_items:
                    if str(ach).lower().strip() not in os_set:
                        new_ach.append(ach)
                data["achivements"] = new_ach

        return data


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
    label: Optional[str] = None


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


class ResumeState(TypedDict, total=False):
    jd: str
    resume: str
    analysis: Optional[Any]
    changes_content: Optional[Any]
    latex_code: str
    diff_latex_code: str
    tone: str
    model: str
    provider: str
    api_key: str
    exclude_sections: Dict[str, bool]
    output_path: str
    judgement: Any
    pdf_base64: str
    template_source: str
    template_id: Optional[int]
    error: Optional[str]  # propagated from any node on failure
    iteration: int


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
    education: Optional[bool] = True
    latex_code: Optional[str] = None


class API_KEY_REQUEST(BaseModel):
    api_provider: str
    api_key: str


class API_KEY_RESPONSE(BaseModel):
    provider: str
    encrypted_key: str


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


class ResumeUpdate(BaseModel):
    label: Optional[str] = None
    tex_source: Optional[str] = None
    pdf_url: Optional[str] = None


class ResumeCreate(BaseModel):
    label: str
    tex_source: str
    jd_snippet: Optional[str] = None
    template_id: Optional[int] = None
    pdf_url: Optional[str] = None
    content: Optional[dict] = None


class CompileRequest(BaseModel):
    latex_code: str
    id: Optional[int] = None


class BulletRewriteOutput(BaseModel):
    id: str = Field(
        description="The unique ID matching the input bullet point (e.g. 'exp_0_1')"
    )
    rewritten_text: str = Field(
        description="Optimized, ATS-friendly text incorporating keywords naturally"
    )


class BatchedRewriteResponse(BaseModel):
    rewritten_bullets: List[BulletRewriteOutput] = Field(default_factory=list)
    rewritten_summary: Optional[str] = Field(
        default=None,
        description="Optimized profile summary/objective. Null if summary was not provided in input.",
    )
    optimized_skills: Optional[List[Skill]] = Field(
        default=None,
        description="Optimized skills list, keeping skills candidate actually has but aligning headers/keywords with JD. Null if not provided.",
    )


class JudgeResume(BaseModel):
    request_changes: List[str]
    should_rewrite: bool
