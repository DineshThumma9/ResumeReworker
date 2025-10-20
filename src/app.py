import pymupdf
import streamlit as st
from pyarrow import output_stream
from main import create_workflow,analyze_resume_workflow
from main import analyze_resume_workflow
from schema import ResumeState
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import BaseModel, Field
from typing import List, Optional
import streamlit as st
from st_circular_progress import CircularProgress


st.title('Resume Review And ReWriter WorkFlow')


jd = st.text_area('Enter your Job Description')
resume = st.file_uploader('Upload your resume')

resume_content = "placeholder"
if resume:

    resume_bytes = resume.read()
    pdf_doc = pymupdf.open(stream=resume_bytes,filetype="pdf")
    resume_content = "".join([pg.get_text() for pg in pdf_doc])



def iterate_nested_dict(d, parent_key=""):
    for key, value in d.items():
        full_key = f"{parent_key}.{key}" if parent_key else key
        
        if isinstance(value, dict):
            # Recursively go deeper
            yield from iterate_nested_dict(value, full_key)
        else:
            # Base case — print or yield the final key-value pair
            yield full_key, value





if st.button('Generate ReWritten Resume'):
    state = ResumeState(
        jd=jd,
        resume=resume_content
    )
    workflow = analyze_resume_workflow()
    resume_workflow = workflow.compile()
    response_state = resume_workflow.invoke(state)
    