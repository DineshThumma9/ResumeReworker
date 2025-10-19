import pymupdf
import streamlit as st
from pyarrow import output_stream

from main import create_workflow
from schema import ResumeState


st.title('Resume Review And ReWriter WorkFlow')


jd = st.text_area('Enter your Job Description')
resume = st.file_uploader('Upload your resume')

resume_content = "placeholder"
if resume:

    resume_bytes = resume.read()
    pdf_doc = pymupdf.open(stream=resume_bytes,filetype="pdf")
    resume_content = "".join([pg.get_text() for pg in pdf_doc])


if st.button('Generate ReWritten Resume'):
    state = ResumeState(
        jd=jd,
        resume=resume_content,
        output_path="./output"
    )
    workflow = create_workflow()
    resume_workflow = workflow.compile()
    resume_workflow.invoke(state)



st.markdown(resume_content)
st.markdown(jd)


