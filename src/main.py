from langchain_groq import ChatGroq
import os
import requests
import streamlit as st
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, SystemMessage
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

MODEL = "qwen/qwen3-32b"

def iterate_nested_dict(d, parent_key=""):
    for key, value in d.items():
        full_key = f"{parent_key}.{key}" if parent_key else key
        
        if isinstance(value, dict):   
            yield from iterate_nested_dict(value, full_key)
        else:
            yield full_key, value



def match_jd(state:ResumeState):
    jd = state['jd']
    resume = state['resume']
    
    st.markdown("### 🔍 Starting Resume Analysis...")
    
    messages = [
        SystemMessage(content=resume_analysis_prompt),
        HumanMessage(content=f"Job Description:\n{jd}\n\nCandidate Resume:\n{resume}"),
    ]

    try:
        llm = ChatGroq(model=MODEL, temperature=0,api_key=os.getenv("GROQ_API_KEY"))  # ty:ignore[unknown-argument]
        structured_llm = llm.with_structured_output(ResumeAnalysis)
        
        st.info("📡 Sending request to AI model...")
        response = structured_llm.invoke(messages)
        
        if response is None:
            st.error("❌ Failed to get response from AI model - response is None")
            return {**state, "analysis": None}
        
        # Handle both dict and BaseModel responses
        if hasattr(response, 'model_dump'):
            analysis = response.model_dump()
        else:
            analysis = response
            
        st.success("✅ AI analysis completed successfully!")
        
    except Exception as e:
        st.error(f"❌ Error during analysis: {str(e)}")
        st.error(f"Error type: {type(e).__name__}")
        return {**state, "analysis": None}
    
    st.markdown("### Analysis of Job Description and Resume")
    st.markdown(f"Peercentage Match Scpre: {analysis['score']}%")
    my_circular_progress = CircularProgress(value=analysis['score'], label="Match Score")
    my_circular_progress.st_circular_progress()
    
    st.markdown("### Explaination")
    st.write(analysis['match_explanation'])
    
    st.markdown("### Missing Keywords")
    for kw in analysis['missing_keywords']:
        st.write(f"- {kw}")
        
    st.markdown("### Negative Points")
    for np in analysis['negative_points']:
        st.write(f"- {np}")
        
    st.markdown("### Potential Improvements")
    for improvement in analysis['potential_improvements']:  
        st.write(f"- {improvement}")
        
    st.markdown("### Urgency")
    st.write(analysis['urgency'] if analysis['urgency'] else "No urgency")
    
    st.markdown("### Resume Quality")
    st.write(analysis['resume_quality'] if analysis['resume_quality'] else "No information on resume quality")

    return {
        **state,
        "analysis": response
    }

    


def rewrite_resume(state:ResumeState):
    resume = state['resume']
    jd = state['jd']
    tone = state['tone']
    exclude_sections = [sec for sec,sec_val in state['exclude_sections'].items() if sec_val] 

    st.markdown("### ✍️ Starting Resume Rewriting...")
    
    if state['analysis'] is None:
        st.error("❌ Cannot rewrite resume: Analysis step failed")
        return {**state, "changes_content": None}
    
    try:
        # Handle both dict and BaseModel responses
        if hasattr(state['analysis'], 'model_dump'):
            analysis = state['analysis'].model_dump()
        else:
            analysis = state['analysis']
        
        llm = ChatGroq(model=MODEL, temperature=0,api_key=os.getenv("GROQ_API_KEY"))  # ty:ignore[unknown-argument]
        structured_llm = llm.with_structured_output(RewriteResume)
        messages = [
            SystemMessage(content=rewrite_content_prompt),
            HumanMessage(content=f"Job Description:\n{jd}\n\nCandidate Resume:\n{resume}\n\nAnalysis Report:\n{analysis}tone:{tone}\nDon't generate content for Exclude Sections:{exclude_sections}\n"),
        ]
        
        st.info("📡 Sending rewrite request to AI model...")
        response = structured_llm.invoke(messages)
        
        if response is None:
            st.error("❌ Failed to get rewrite response from AI model - response is None")
            return {**state, "changes_content": None}
        
        st.success("✅ Resume rewriting completed successfully!")
        
        return {
            **state,
            "changes_content": response
        }
        
    except Exception as e:
        st.error(f"❌ Error during resume rewriting: {str(e)}")
        st.error(f"Error type: {type(e).__name__}")
        return {**state, "changes_content": None}




def latex_to_pdf(latex_string: str,filename:str) -> bytes:
    """
    Send LaTeX string to CloudConvert using proper import/upload,
    wait for PDF, download it, return PDF bytes.
    """

    try:
        st.info("🔧 Creating CloudConvert job...")
        job = cloudconvert.Job.create(payload={
            "tasks": {
                "upload-my-file": {
                    "operation": "import/upload"
                },
                "convert-to-pdf": {
                    "operation": "convert",
                    "input": "upload-my-file",
                    "input_format": "tex",
                    "output_format": "pdf",
                    "engine": "texlive",
                    "engine_version": "2016"  
                },
                "export-file": {
                    "operation": "export/url",
                    "input": "convert-to-pdf"
                }
            }
        })

        st.info("📤 Uploading LaTeX file...")
        upload_task_id = job["tasks"][0]["id"]
        upload_task = cloudconvert.Task.find(id=upload_task_id)

        with open("temp_resume.tex", "w", encoding="utf-8") as f:
            f.write(latex_string)

        cloudconvert.Task.upload(
            file_name="temp_resume.tex",
            task=upload_task
        )

        st.info("⏳ Converting LaTeX to PDF...")
        job = cloudconvert.Job.wait(id=job["id"])

        # Find the export task
        export_task = None
        for task in job["tasks"]:
            if task.get("operation") == "export/url" and task.get("status") == "finished":
                export_task = task
                break
        
        if export_task is None:
            # Look for failed tasks to provide better error messages
            failed_tasks = [task for task in job["tasks"] if task.get("status") == "error"]
            if failed_tasks:
                error_msg = f"LaTeX conversion failed: {failed_tasks[0].get('message', 'Unknown error')}"
                st.error(f"❌ {error_msg}")
                raise Exception(error_msg)
            else:
                error_msg = "No export task found or conversion incomplete"
                st.error(f"❌ {error_msg}")
                raise Exception(error_msg)

        if not export_task.get("result") or not export_task["result"].get("files"):
            error_msg = "No files found in export task result"
            st.error(f"❌ {error_msg}")
            raise Exception(error_msg)
        
        file_info = export_task["result"]["files"][0]
        download_url = file_info["url"]
        
        st.info("⬇️ Downloading PDF...")
        try:
            response = requests.get(download_url, timeout=30)
            response.raise_for_status()
            pdf_bytes = response.content

        except requests.exceptions.RequestException as e:
            st.warning("⚠️ Primary download failed, trying alternative method...")
            try:
                pdf_bytes = cloudconvert.download(
                    filename=file_info["filename"],
                    url=file_info["url"]
                )

            except Exception as sdk_e:
                error_msg = f"Both download methods failed. HTTP: {str(e)}, SDK: {str(sdk_e)}"
                st.error(f"❌ {error_msg}")
                raise Exception(error_msg)

        if not pdf_bytes or len(pdf_bytes) < 100:
            error_msg = f"Downloaded PDF is too small: {len(pdf_bytes) if pdf_bytes else 0} bytes"
            st.error(f"❌ {error_msg}")
            if pdf_bytes:
                st.error(f"Downloaded content preview: {pdf_bytes[:50]}")
            raise Exception("Downloaded PDF is empty or too small")
        
        if not pdf_bytes.startswith(b'%PDF'):
            error_msg = "Downloaded file is not a valid PDF"
            st.error(f"❌ {error_msg}")
            raise Exception(error_msg)
        
        if not pdf_bytes.rstrip().endswith(b'%%EOF'):
            error_msg = "Downloaded PDF is incomplete or missing EOF marker"
            st.error(f"❌ {error_msg}")
            raise Exception(error_msg)
        
        st.success("✅ PDF downloaded successfully!")
        return pdf_bytes

    except Exception as e:
        error_msg = f"PDF generation failed: {str(e)}"
        st.error(f"❌ {error_msg}")
        # Re-raise with more context
        raise Exception(error_msg)


def rewrite_latex(state: ResumeState):
    suggesting_changes = state["changes_content"]
    exclude_sections = state["exclude_sections"]
    
    st.markdown("### 📄 Generating LaTeX Resume...")
    
    if suggesting_changes is None:
        st.error("❌ Cannot generate LaTeX: Resume rewriting step failed")
        return {**state, "latex_code": "Error: No resume content to convert"}

    try:
        st.info("📝 Creating resume document from schema...")
        doc = create_resume_from_schema(resume_content=suggesting_changes,exclude_sections=exclude_sections)
        latex_code = doc.dumps()
        
        st.success("✅ LaTeX code generated successfully!")
        st.markdown("### Generated LaTeX Code")
        st.code(latex_code, language="latex")

        try:
            st.info("🔄 Converting LaTeX to PDF...")
            filename = f"{suggesting_changes.details.name.replace(' ', '_')}_resume.pdf"
            pdf_bytes = latex_to_pdf(latex_code, filename)
            
            if not pdf_bytes or len(pdf_bytes) < 100:
                st.error("❌ Generated PDF is empty or corrupted")
                return {**state, "latex_code": latex_code}
                
            st.success("✅ Resume PDF generated successfully!")
            
            st.download_button(
                label="📄 Download Resume PDF",
                data=pdf_bytes,
                file_name=filename,
                mime="application/pdf"
            )

        except Exception as pdf_error:
            st.error(f"❌ PDF generation failed: {str(pdf_error)}")
            st.error(f"❌ PDF Error type: {type(pdf_error).__name__}")
            st.warning("⚠️ LaTeX code was generated successfully, but PDF conversion failed.")
            
            # Check if it's an API key issue
            if "api" in str(pdf_error).lower() or "auth" in str(pdf_error).lower():
                st.error("🔑 This looks like a CloudConvert API key issue. Please check your API key in the .env file.")
            # Check if it's a network issue
            elif "network" in str(pdf_error).lower() or "connection" in str(pdf_error).lower():
                st.error("🌐 This looks like a network connectivity issue. Please check your internet connection.")
            # Check if it's a LaTeX compilation issue
            elif "tex" in str(pdf_error).lower() or "latex" in str(pdf_error).lower():
                st.error("📝 This looks like a LaTeX compilation issue. The generated LaTeX code might have syntax errors.")
                st.info("💡 You can still copy the LaTeX code above and compile it manually.")
            
            # Show the full error for debugging
            st.expander("🔧 Full Error Details (for debugging)").write(str(pdf_error))

        return {**state, "latex_code": latex_code}

    except Exception as e:
        st.error(f"❌ Error creating resume: {str(e)}")
        st.error(f"Error type: {type(e).__name__}")
        return {**state, "latex_code": f"Error: {str(e)}"}





def analyze_resume_workflow():
    graph = StateGraph(ResumeState)
    graph.add_node("match_jd", match_jd)
    graph.add_node("rewrite_resume", rewrite_resume)
    graph.add_node("rewrite_latex", rewrite_latex)
    graph.add_edge(START,"match_jd")
    graph.add_edge("match_jd","rewrite_resume")
    graph.add_edge("rewrite_resume","rewrite_latex")
    graph.add_edge("rewrite_latex",END)
    return graph









