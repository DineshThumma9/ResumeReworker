import os

import requests
import streamlit as st
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.constants import START, END
from langgraph.graph import StateGraph
from st_circular_progress import CircularProgress

from prompts import resume_analysis_prompt, rewrite_content_prompt
from res import create_resume_from_schema
from schema import ResumeAnalysis, RewriteResume, ResumeState
import cloudconvert
import requests
import os




load_dotenv()
cloudconvert.default()

def iterate_nested_dict(d, parent_key=""):
    for key, value in d.items():
        full_key = f"{parent_key}.{key}" if parent_key else key
        
        if isinstance(value, dict):
            # Recursively go deeper
            yield from iterate_nested_dict(value, full_key)
        else:
            # Base case — print or yield the final key-value pair
            yield full_key, value



def match_jd(state:ResumeState):

    jd = state['jd']
    resume = state['resume']



    
    messages = [
        SystemMessage(content=resume_analysis_prompt),
        HumanMessage(content=f"Job Description:\n{jd}\n\nCandidate Resume:\n{resume}"),
    ]

    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0,api_key=os.getenv("GEMINI_API_KEY"))
    llm = llm.with_structured_output(ResumeAnalysis)
    response = llm.invoke(messages)
    analysis = response.model_dump()
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
    for pi in analysis['potential_improvements']:
        st.write(f"- {pi}")
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
    analysis = state['analysis'].model_dump()
    
    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0,api_key=os.getenv("GEMINI_API_KEY"))
    llm = llm.with_structured_output(RewriteResume)
    messages = [
        SystemMessage(content=rewrite_content_prompt),
        HumanMessage(content=f"Job Description:\n{jd}\n\nCandidate Resume:\n{resume}\n\nAnalysis Report:\n{analysis}"),

    ]
    response = llm.invoke(messages)
    

    
    
    
    return {
        **state,
        "changes_content": response
    }



def latex_to_pdf(latex_string: str) -> bytes:
    """
    Takes LaTeX code as a string,
    sends it to CloudConvert,
    waits for conversion,
    downloads the PDF,
    returns PDF bytes.
    """

    # 1) Create cloudconvert job
    job = cloudconvert.Job.create(payload={
        "tasks": {
            "upload-latex": {
                "operation": "import/raw"
            },
            "convert-to-pdf": {
                "operation": "convert",
                "input": "upload-latex",
                "input_format": "tex",
                "output_format": "pdf"
            },
            "export-pdf": {
                "operation": "export/url",
                "input": "convert-to-pdf"
            }
        }
    })

    # 2) Upload .tex data
    upload_task = cloudconvert.Job.tasks.get(job["tasks"]["upload-latex"]["id"])
    upload_url = upload_task["result"]["form"]["url"]

    files = {"file": ("resume.tex", latex_string)}
    requests.post(upload_url, files=files)

    # 3) Wait for conversion to finish
    job = cloudconvert.Job.wait(job["id"])

    # 4) Get PDF download URL
    export_task = job["tasks"]["export-pdf"]
    file_url = export_task["result"]["files"][0]["url"]

    # 5) Download PDF bytes
    pdf_bytes = requests.get(file_url).content

    return pdf_bytes  # <---- EASY TO USE ANYWHERE




def rewrite_latex(state: ResumeState):
    suggesting_changes = state["changes_content"]

    try:
        # 1) Create LaTeX document using PyLaTeX
        doc = create_resume_from_schema(resume_content=suggesting_changes)
        latex_code = doc.dumps()

        # 2) Convert LaTeX to PDF using CloudConvert
        try:
            st.info("Generating PDF via CloudConvert… please wait")

            pdf_bytes = latex_to_pdf(latex_code)

            st.success("✅ Resume PDF generated successfully!")

            # 3) Streamlit download button
            filename = f"{suggesting_changes.details.name.replace(' ', '_')}_resume.pdf"

            st.download_button(
                label="Download Resume PDF",
                data=pdf_bytes,
                file_name=filename,
                mime="application/pdf"
            )

        except Exception as e:
            st.error(f"PDF generation failed: {str(e)}")
            st.stop()

        # 4) Show LaTeX code to user
        st.markdown("### Generated LaTeX Code")
        st.code(latex_code, language="latex")

        return {**state, "latex_code": latex_code}

    except Exception as e:
        st.error(f"Error creating resume: {str(e)}")
        return {**state, "latex_code": f"Error: {str(e)}"}






# def get_pdf(content:str):
#     job = cloudconvert.Job.create(payload={
#         "tasks": {
#             "import-my-file": {
#                 "operation": "import/raw",
#                 "file": "resume.tex"
#             },
#             "convert": {
#                 "operation": "convert",
#                 "input": "import-my-file",
#                 "output_format": "pdf"
#             },
#             "export-my-file": {
#                 "operation": "export/url",
#                 "input": "convert"
#             }
#         }
#     })
#
#     result = job["tasks"]["export-my-file"]["result"]["files"][0]
#     pdf_url = result["url"]
#
#     # Download the PDF
#     pdf_data = requests.get(pdf_url).content
#     open("resume.pdf", "wb").write(pdf_data)




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
    














