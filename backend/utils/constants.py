DUMMY_RESUME_DATA = {
    "details": {
        "name": "Alex Applicant",
        "profile_summary": "Resourceful and driven software engineer with 5+ years of experience developing robust web applications and scalable backend systems. Proven ability to lead teams and deliver high-quality solutions on time.",
        "profile_links": {
            "phone": "+1 (555) 123-4567",
            "email": "alex.applicant@example.com",
            "linkedin": "linkedin.com/in/alexapplicant",
            "github": "github.com/alexapplicant",
            "location": "San Francisco, CA",
        },
    },
    "education": [
        {
            "institution": "University of Technology",
            "year": "2016 - 2020",
            "gpa": "3.9/4.0",
            "course": "B.S. in Computer Science",
        }
    ],
    "experience": [
        {
            "company": "Tech Innovations Inc.",
            "role": "Senior Backend Engineer",
            "duration": "Jan 2022 - Present",
            "responsibilities": [
                "Architected and deployed microservices using FastAPI and Docker, improving system scalability by 40%.",
                "Optimized PostgreSQL queries, reducing average API response times from 800ms to 200ms.",
                "Mentored 3 junior developers and established CI/CD pipelines using GitHub Actions.",
            ],
        },
        {
            "company": "Web Solutions LLC",
            "role": "Full Stack Developer",
            "duration": "Jun 2020 - Dec 2021",
            "responsibilities": [
                "Developed responsive front-end interfaces using React and Tailwind CSS.",
                "Integrated third-party payment gateways like Stripe for secure transactions.",
                "Collaborated with product managers to define and execute quarterly roadmaps.",
            ],
        },
    ],
    "technical_skills": [
        {
            "category": "Languages",
            "skills": ["Python", "TypeScript", "JavaScript", "SQL", "Go"],
        },
        {
            "category": "Frameworks",
            "skills": ["FastAPI", "React", "Node.js", "Express", "Next.js"],
        },
        {
            "category": "Tools",
            "skills": ["Docker", "Kubernetes", "AWS", "Git", "PostgreSQL", "Redis"],
        },
    ],
    "projects": [
        {
            "name": "E-Commerce Platform Redesign",
            "description": "A high-performance e-commerce platform built from the ground up.",
            "technologies": ["React", "Node.js", "MongoDB", "Redis"],
            "highlights": [
                "Implemented real-time inventory tracking using WebSockets.",
                "Increased user retention by 25% through an improved checkout flow.",
            ],
        }
    ],
}


_VALIDATION_URLS: dict[str, str] = {
    "groq": "https://api.groq.com/openai/v1/models",
    "openai": "https://api.openai.com/v1/models",
    "anthropic": "https://api.anthropic.com/v1/models",
    "mistralai": "https://api.mistral.ai/v1/models",
    "openrouter": "https://openrouter.ai/api/v1/models",
    "google_genai": "https://generativelanguage.googleapis.com/v1beta/models",
    "huggingface": "https://router.huggingface.co/v1/models",
}


VALID_PROVIDERS = list(_VALIDATION_URLS.keys())


STATIC_MODELS = {
            "openai": ["gpt-4o", "gpt-4-turbo", "gpt-3.5-turbo"],
            "anthropic": [
                "claude-3-5-sonnet-20240620",
                "claude-3-opus-20240229",
                "claude-3-haiku-20240307",
            ],
            "google_genai": ["gemini-1.5-pro", "gemini-1.5-flash", "gemini-pro"],
            "groq": ["llama3-70b-8192", "llama3-8b-8192", "mixtral-8x7b-32768"],
            "mistralai": [
                "mistral-large-latest",
                "mistral-small-latest",
                "open-mixtral-8x7b",
            ],
            "openrouter": [
                "anthropic/claude-3.5-sonnet",
                "openai/gpt-4o",
                "meta-llama/llama-3-70b-instruct",
            ],
            "huggingface": [
                "meta-llama/Meta-Llama-3-70B-Instruct",
                "mistralai/Mixtral-8x7B-Instruct-v0.1",
            ],
        }

DEFAULT_TEMPLATE = "jakes1.tex"
DEFAULT_LLM_PROVIDER = "groq"
DEFAULT_LLM_MODEL = "llama-3.3-70b-versatile"
MAX_REWRITE_ITERATIONS = 5
