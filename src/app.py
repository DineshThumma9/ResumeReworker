import pymupdf
import streamlit as st
from main import analyze_resume_workflow
from schema import ResumeState

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
            yield from iterate_nested_dict(value, full_key)
        else:
            yield full_key, value



st.write("Select Tone for ReWritten Resume:")
tone = st.selectbox('Select Tone', ['Professional', 'Confident', 'Grounded', 'Formal','Other'])
if tone == 'Other':
    tone = st.text_input('Enter your custom tone')





if st.button('Generate ReWritten Resume'):
    state = ResumeState(
        jd=jd,
        resume=resume_content,
        tone=tone,
        exclude_sections=sections
    )
    workflow = analyze_resume_workflow()
    resume_workflow = workflow.compile()
    response_state = resume_workflow.invoke(state)
    