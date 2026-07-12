"""
utils/resume_text.py
--------------------
Pure data-transformation helpers for resume text.
No HTTP, no DB, no business logic — just string processing.
"""

import json
from typing import Any

from models import User


def extract_profile_details(user: User) -> str:
    """
    Format a user's stored contact info as a plain-text block to append to resume text.
    Used so the LLM has the candidate's actual contact details regardless of what the
    PDF contained.
    """
    profile = (
        f"\n\nCandidate Contact Details:\nName: {user.name}\nEmail: {user.email}"
    )
    if user.phone:
        profile += f"\nPhone: {user.phone}"
    if user.location:
        profile += f"\nLocation: {user.location}"
    if user.github:
        profile += f"\nGitHub: {user.github}"
    if user.linkedin:
        profile += f"\nLinkedIn: {user.linkedin}"
    if user.website:
        profile += f"\nWebsite/Portfolio: {user.website}"
    return profile


def extract_resume_details(raw_resume: Any) -> str:
    """
    Convert a raw resume (JSON dict or plain string) stored in the user profile into a
    human-readable text block suitable for passing to the LLM.
    """
    try:
        if isinstance(raw_resume, str):
            sections_dict = json.loads(raw_resume)
        else:
            sections_dict = raw_resume

        if not isinstance(sections_dict, dict):
            return str(raw_resume) if raw_resume else ""

        resume_text = ""
        for sec_name, items in sections_dict.items():
            if not items:
                continue
            clean_title = sec_name.replace("_", " ").upper()
            resume_text += f"\n\n## {clean_title}"
            if isinstance(items, list):
                for item in items:
                    title = item.get("title", "")
                    subtitle = item.get("subtitle", "")
                    date = item.get("date", "")
                    skills = item.get("skills", "")
                    link = item.get("link", "")
                    desc = item.get("description", "")

                    header_parts = []
                    if title:
                        header_parts.append(f"**{title}**")
                    if subtitle:
                        header_parts.append(f"at {subtitle}")
                    if date:
                        header_parts.append(f"({date})")

                    if header_parts:
                        resume_text += "\n- " + " ".join(header_parts)
                    if link:
                        resume_text += f"\n  Link: {link}"
                    if skills:
                        resume_text += f"\n  Skills/Tech: {skills}"
                    if desc:
                        indented_desc = "\n  ".join(desc.split("\n"))
                        resume_text += f"\n  Details: {indented_desc}"
            elif isinstance(items, str) and items.strip():
                resume_text += f"\n{items}"
        return resume_text
    except Exception:
        return str(raw_resume) if raw_resume else ""


def resolve_resume_label(label: str, analysis_data: dict | None, user: User) -> str:
    """
    Derive a display label for a newly created resume.
    If the user supplied one, use it as-is. Otherwise derive one from name + company.
    """
    if label and label.strip():
        return label

    company_name = "Company"
    if analysis_data and isinstance(analysis_data, dict):
        company_name = analysis_data.get("company_name", "Company") or "Company"

    clean_name = "".join(
        c for c in user.name if c.isalnum() or c in (" ", "_", "-")
    ).strip().replace(" ", "") or "User"

    clean_company = "".join(
        c for c in company_name if c.isalnum() or c in (" ", "_", "-")
    ).strip().replace(" ", "") or "Company"

    return f"{clean_name}{clean_company}"
