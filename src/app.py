import pymupdf
import streamlit as st



st.title('Resume Review And ReWriter WorkFlow')


jd = st.text_area('Enter your Job Description')
resume = st.file_uploader('Upload your resume')

resume_content = "placeholder"
if resume:

    resume_bytes = resume.read()
    pdf_doc = pymupdf.open(stream=resume_bytes,filetype="pdf")
    resume_content = "".join([pg.get_text() for pg in pdf_doc])


if resume_content and jd:
    inital_state = {
        "jd":jd,
        "resume_content":resume_content
    }
st.markdown(resume_content)
st.markdown(jd)


