import os
import requests
import streamlit as st
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from typing import Any
from langgraph.constants import START, END
from langgraph.graph import StateGraph
from st_circular_progress import CircularProgress
from prompts import resume_analysis_prompt, rewrite_content_prompt
from res import create_resume_from_schema
from schema import ResumeAnalysis, RewriteResume, ResumeState
import cloudconvert

load_dotenv()
cloudconvert.configure(api_key=os.getenv("CLOUDCONVERT_API_KEY"))


def iterate_nested_dict(d, parent_key=""):
    for key, value in d.items():
        full_key = f"{parent_key}.{key}" if parent_key else key
        if isinstance(value, dict):
            yield from iterate_nested_dict(value, full_key)
        else:
            yield full_key, value



def match_jd(state: ResumeState):
    jd = state['jd']
    resume = state['resume']
    
    messages = [
        SystemMessage(content=resume_analysis_prompt),
        HumanMessage(content=f"Job Description:\n{jd}\n\nCandidate Resume:\n{resume}"),
    ]

    try:
        llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0, api_key=os.getenv("GEMINI_API_KEY"))
        structured_llm = llm.with_structured_output(ResumeAnalysis)
        response = structured_llm.invoke(messages)
        
        if response is None:
            st.error("AI analysis failed")
            return {**state, "analysis": None}
            
        analysis = response.model_dump()
        
    except Exception:
        st.error("Analysis failed")
        return {**state, "analysis": None}
    
    st.markdown("### Analysis of Job Description and Resume")
    st.markdown(f"Match Score: {analysis['score']}%")
    CircularProgress(value=analysis['score'], label="Match Score").st_circular_progress()
    
    st.markdown("### Explanation")
    st.write(analysis['match_explanation'])
    
    st.markdown("### Missing Keywords")
    for kw in analysis['missing_keywords']:
        st.write(f"- {kw}")
        
    st.markdown("### Negative Points")
    for np in analysis['negative_points']:
        st.write(f"- {np}")
        
    st.markdown("### Potential Improvements")
    for pi in analysis['potential_improvements']:
        st.write(f"- {pi}")
        
    st.markdown("### Urgency")
    st.write(analysis['urgency'] if analysis['urgency'] else "No urgency")
    
    st.markdown("### Resume Quality")
    st.write(analysis['resume_quality'] if analysis['resume_quality'] else "No information")

    return {**state, "analysis": response}


def rewrite_resume(state: ResumeState):
    resume = state['resume']
    jd = state['jd']
    
    if state['analysis'] is None:
        st.error("Analysis required for rewrite")
        return {**state, "changes_content": None}
    
    try:
        analysis = state['analysis'].model_dump()
        
        llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0, api_key=os.getenv("GEMINI_API_KEY"))
        structured_llm = llm.with_structured_output(RewriteResume)
        messages = [
            SystemMessage(content=rewrite_content_prompt),
            HumanMessage(content=f"Job Description:\n{jd}\n\nCandidate Resume:\n{resume}\n\nAnalysis Report:\n{analysis}"),
        ]
        response = structured_llm.invoke(messages)
        
        if response is None:
            st.error("Resume rewrite failed")
            return {**state, "changes_content": None}
        
        return {**state, "changes_content": response}
        
    except Exception:
        st.error("Rewrite failed")
        return {**state, "changes_content": None}




def latex_to_pdf(latex_string: str,filename:str) -> bytes:
    """
    Send LaTeX string to CloudConvert using proper import/upload,
    wait for PDF, download it, return PDF bytes.
    """

    job = cloudconvert.Job.create(payload={
        "tasks": {
            "upload-my-file": {"operation": "import/upload"},
            "convert-to-pdf": {
                "operation": "convert",
                "input": "upload-my-file", 
                "input_format": "tex",
                "output_format": "pdf",
                "engine": "texlive",
                "engine_version": "2022"
            },
            "export-file": {"operation": "export/url", "input": "convert-to-pdf"}
        }
    })

    upload_task_id = job["tasks"][0]["id"]
    upload_task = cloudconvert.Task.find(id=upload_task_id)

    with open("temp_resume.tex", "w", encoding="utf-8") as f:
        f.write(latex_string)

    cloudconvert.Task.upload(file_name="temp_resume.tex", task=upload_task)
    job = cloudconvert.Job.wait(id=job["id"])


    
   
    export_task = None
    for task in job["tasks"]:
        if task.get("operation") == "export/url" and task.get("status") == "finished":
            export_task = task
            break
    
  
    file_info = export_task["result"]["files"][0]
    download_url = file_info["url"]
    
    try:
        # Try direct HTTP request first
        response = requests.get(download_url, timeout=30)
        response.raise_for_status()
        pdf_bytes = response.content

    except requests.exceptions.RequestException as e:

        try:
            # Fallback to CloudConvert SDK
            pdf_bytes = cloudconvert.download(
                filename=file_info["filename"],
                url=file_info["url"]
            )

        except Exception as sdk_e:
            st.error(f"Both download methods failed. HTTP: {str(e)}, SDK: {str(sdk_e)}")
            raise Exception(f"Failed to download PDF: HTTP failed ({str(e)}), SDK failed ({str(sdk_e)})")

    # Validate PDF bytes
    if not pdf_bytes or len(pdf_bytes) < 100:
        st.error(f"Downloaded PDF is too small: {len(pdf_bytes) if pdf_bytes else 0} bytes")
        if pdf_bytes:
            st.error(f"Downloaded content: {pdf_bytes[:50]}")  # Show first 50 bytes for debugging
        raise Exception("Downloaded PDF is empty or too small")
    
    # Check PDF header
    if not pdf_bytes.startswith(b'%PDF'):
        raise Exception("Downloaded file is not a valid PDF")
    
    # Check PDF footer for completeness
    if not pdf_bytes.rstrip().endswith(b'%%EOF'):
        raise Exception("Downloaded PDF is incomplete or missing EOF marker")
    
    return pdf_bytes


def rewrite_latex(state: ResumeState):
    suggesting_changes = state["changes_content"]
    
    if suggesting_changes is None:
        st.error("Rewrite required for LaTeX generation")
        return {**state, "latex_code": "Error: No content"}

    try:
        doc = create_resume_from_schema(resume_content=suggesting_changes)
        latex_code = doc.dumps()
        
        st.markdown("### Generated LaTeX Code")
        st.code(latex_code, language="latex")

        try:
            filename = f"{suggesting_changes.details.name.replace(' ', '_')}_resume.pdf"
            pdf_bytes = latex_to_pdf(latex_code, filename)
            
            if not pdf_bytes or len(pdf_bytes) < 100:
                st.error("PDF generation failed")
                return {**state, "latex_code": latex_code}
                
            st.success("✅ PDF generated successfully!")
            
            st.download_button(
                label="📄 Download Resume PDF",
                data=pdf_bytes,
                file_name=filename,
                mime="application/pdf"
            )

        except Exception:
            st.error("PDF generation failed")

        return {**state, "latex_code": latex_code}

    except Exception:
        st.error("LaTeX generation failed")
        return {**state, "latex_code": "Error"}





def analyze_resume_workflow():
    graph = StateGraph(ResumeState)
    graph.add_node("match_jd", match_jd)
    graph.add_node("rewrite_resume", rewrite_resume)
    graph.add_node("rewrite_latex", rewrite_latex)
    graph.add_edge(START, "match_jd")
    graph.add_edge("match_jd", "rewrite_resume")
    graph.add_edge("rewrite_resume", "rewrite_latex")
    graph.add_edge("rewrite_latex", END)
    return graph