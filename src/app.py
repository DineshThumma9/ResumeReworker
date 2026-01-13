import pymupdf
import streamlit as st
from main import analyze_resume_workflow
from schema import ResumeState

st.title('Resume ReWriter WorkFlow')


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

exclude =  dict()
for sec in ['Professional Summary','Education', 'Experience', 'Technical Skills', 'Projects', 'Coursework', 'Achievements', 'Hackathons and Certificates']:
    exclude[sec] = False
exclude_sections = st.multiselect(
    'Select sections to exclude from the rewritten resume',
    ['Professional Summary','Education', 'Experience', 'Technical Skills', 'Projects', 'Coursework', 'Achievements', 'Hackathons and Certificates']
)
for ex in exclude_sections:
    exclude[ex] = True




if st.button('Generate ReWritten Resume'):
    # Validate inputs
    if not jd.strip():
        st.error("Please enter a job description")
        st.stop()
    
    if not resume or resume_content == "placeholder":
        st.error("Please upload a resume PDF file")
        st.stop()
    
    if not tone.strip():
        st.error("Please select or enter a tone")
        st.stop()
    
    # Check for API key
    import os
    from dotenv import load_dotenv
    load_dotenv()
    
    if not os.getenv("GEMINI_API_KEY"):
        st.error("GEMINI_API_KEY not found in environment variables. Please check your .env file.")
        st.stop()
    
    try:
        with st.spinner('Analyzing resume and generating rewritten version...'):
            state = ResumeState(
                jd=jd,
                resume=resume_content,
                tone=tone,
                exclude_sections=exclude
            )
            workflow = analyze_resume_workflow()
            resume_workflow = workflow.compile()
            response_state = resume_workflow.invoke(state)
            
            st.success("ReWritten Resume Generated Successfully!")
                
    except Exception as e:
        st.error(f"❌ An error occurred: {str(e)}")
        st.error("Please check your inputs and try again. Make sure your API keys are properly configured.")
