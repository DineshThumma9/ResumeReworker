import os

from langchain_core.messages import SystemMessage, HumanMessage
from langchain_groq import ChatGroq
from langchain_mistralai import ChatMistralAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.constants import START, END
from langgraph.graph import StateGraph

from prompts import rewrite_content_prompt, rewrite_latex_prompt, resume_analysis_prompt, jakes_template_reference
from schema import ResumeState, RewriteResume, ResumeAnalysis
from dotenv import load_dotenv


load_dotenv()


def match_jd(state: ResumeState) -> dict:
    """
    Analyze resume against job description
    Returns: {"analysis": ResumeAnalysis}
    """
    print("📊 Analyzing resume against job description...")

    jd = state["jd"]
    resume = state["resume"]

    messages = [
        SystemMessage(content=resume_analysis_prompt),  # FIXED: correct prompt name
        HumanMessage(content=f"Job Description:\n{jd}\n\nResume:\n{resume}")
    ]

    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash",api_key=os.getenv("GEMINI_API_KEY"))
    llm_with_structure = llm.with_structured_output(ResumeAnalysis)

    try:
        analysis = llm_with_structure.invoke(messages)
        print(f"✅ Analysis complete. Score: {analysis.score}/100")
        return {"analysis": analysis}  # FIXED: correct key name
    except Exception as e:
        print(f"❌ Error in match_jd: {e}")
        raise



 # FIXED: Serialize Pydantic object to string for LLM
    analysis_text = f"""
Analysis Results:
- Score: {analysis.score}/100
- Match: {analysis.match}
- Missing Keywords: {', '.join(analysis.missing_keywords)}
- Negative Points:
{chr(10).join(f"  - {point}" for point in analysis.negative_points)}
- Improvements Needed:
{chr(10).join(f"  - {imp}" for imp in analysis.potential_improvements)}
"""


def rewrite_resume(state: ResumeState) -> dict:
    """
    Rewrite resume content based on analysis
    Returns: {"changes_content": RewriteResume}
    """
    print("✍️  Rewriting resume content...")

    jd = state["jd"]
    resume = state["resume"]
    analysis = state["analysis"]  # FIXED: correct key name

    messages = [
        SystemMessage(content=rewrite_content_prompt),
        HumanMessage(content=f"""
    Job Description:
    {jd}

    Original Resume:
    {resume}

    {analysis}

    Please rewrite the resume to better match the job description based on this analysis.
    """)
    ]

    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash",api_key=os.getenv("GEMINI_API_KEY"))
    llm_with_structure = llm.with_structured_output(RewriteResume)

    import streamlit as st

    try:
        rewritten = llm_with_structure.invoke(messages)
        st.markdown(rewritten)
        print(f"✅ Resume rewritten with {len(rewritten.projects)} projects")
        return {"changes_content": rewritten}
    except Exception as e:
        print(f"❌ Error in rewrite_resume: {e}")
        raise


def rewrite_latex(state: ResumeState) -> dict:
    """
    Convert rewritten content to LaTeX
    Returns: {"latex_code": str}
    """
    print("📝 Generating LaTeX code...")

    content = state["changes_content"]

    # FIXED: Serialize Pydantic object to readable format
    content_text = f"""
Profile Summary:
{content.profile_summary}

Education:
{chr(10).join(f"- {edu}" for edu in content.education)}

Technical Skills:
{chr(10).join(f"- {skill}" for skill in content.technical_skills)}

Projects:
{chr(10).join(f'''
Project: {proj.name}
Description: {proj.description}
Technologies: {", ".join(proj.technologies)}
Highlights:
{chr(10).join(f"  - {h}" for h in proj.highlights)}
''' for proj in content.projects)}

Coursework:
{chr(10).join(f"- {course}" for course in content.coursework)}

Hackathons & Certificates:
{chr(10).join(f"- {cert}" for cert in content.hackathons_and_certificates)}
"""

    # FIXED: Include Jake's template reference
    prompt_with_template = rewrite_latex_prompt.replace("{jakes_template}", jakes_template_reference)

    messages = [
        SystemMessage(content=prompt_with_template),
        HumanMessage(content=f"""
Here is the resume content to convert to LaTeX:

{content_text}

Generate complete, compilable LaTeX code using Jake's Resume Template.
""")
    ]

    # FIXED: Correct model name for Google
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-pro",  # or "gemini-2.0-flash-exp"
        api_key=os.getenv("GEMINI_API_KEY")
    )

    try:
        response = llm.invoke(messages)
        latex_code = response.content

        # Clean up response (remove markdown code blocks if present)
        if latex_code.startswith("```latex"):
            latex_code = latex_code.split("```latex")[1].split("```")[0].strip()
        elif latex_code.startswith("```"):
            latex_code = latex_code.split("```")[1].split("```")[0].strip()

        import streamlit as st
        st.markdown(latex_code)
        print(f"✅ LaTeX code generated ({len(latex_code)} characters)")
        return {"latex_code": latex_code}  # FIXED: correct key name
    except Exception as e:
        print(f"❌ Error in rewrite_latex: {e}")
        raise


import tempfile
import subprocess


def generate_pdf(state: ResumeState) -> dict:
    """
    Compile LaTeX to PDF
    Returns: {"output_pdf_path": str}
    """
    print("📄 Generating PDF from LaTeX...")

    latex_code = state["latex_code"]  # FIXED: correct key name
    output_pdf = state.get("output_path")  # FIXED: get from state

    with tempfile.TemporaryDirectory() as tmpdir:
        # FIXED: Correct indentation
        tex_file = os.path.join(tmpdir, "resume.tex")

        # Save LaTeX code to .tex file
        with open(tex_file, "w", encoding="utf-8") as f:
            f.write(latex_code)

        try:
            # Run pdflatex
            result = subprocess.run(
                ["pdflatex", "-interaction=nonstopmode", tex_file],
                check=True,
                cwd=tmpdir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=30
            )

            # Move the generated PDF to the desired location
            generated_pdf = os.path.join(tmpdir, "resume.pdf")

            if os.path.exists(generated_pdf):
                # Ensure output directory exists
                os.makedirs(os.path.dirname(os.path.abspath(output_pdf)), exist_ok=True)
                os.replace(generated_pdf, output_pdf)
                print(f"✅ PDF generated successfully: {output_pdf}")
                return {"output_pdf_path": output_pdf}
            else:
                raise FileNotFoundError("PDF was not generated")

        except subprocess.CalledProcessError as e:
            print("❌ Error compiling LaTeX!")
            print("STDOUT:", e.stdout.decode())
            print("STDERR:", e.stderr.decode())
            raise
        except subprocess.TimeoutExpired:
            print("❌ LaTeX compilation timed out")
            raise
        except Exception as e:
            print(f"❌ Unexpected error in generate_pdf: {e}")
            raise


# =============================================================================
# WORKFLOW SETUP
# =============================================================================

def create_workflow() -> StateGraph:
    """Create and configure the resume processing workflow"""

    graph = StateGraph(ResumeState)

    # Add nodes
    graph.add_node("match_jd", match_jd)
    graph.add_node("rewrite_resume", rewrite_resume)
    graph.add_node("rewrite_latex", rewrite_latex)
    graph.add_node("generate_pdf", generate_pdf)

    # Define edges
    graph.add_edge(START, "match_jd")
    graph.add_edge("match_jd", "rewrite_resume")
    graph.add_edge("rewrite_resume", "rewrite_latex")
    graph.add_edge("rewrite_latex", "generate_pdf")
    graph.add_edge("generate_pdf", END)

    return graph