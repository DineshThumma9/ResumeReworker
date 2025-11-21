import os

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

load_dotenv()


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



def rewrite_latex(state:ResumeState):
    suggesting_changes = state['changes_content']
    
    try:
        doc = create_resume_from_schema(
            resume_content=suggesting_changes,
            output_filename=f"{suggesting_changes.details.name.replace(' ','_')}_output"
        )
        
        # Generate both PDF and tex files
        try:
            pdf_filename = f"{suggesting_changes.details.name.replace(' ','_')}_output"
            doc.generate_pdf(pdf_filename, clean_tex=False, compiler='pdflatex')
            st.success("✅ Resume PDF generated successfully!")
            
            # Create download button for PDF - use the same filename that was generated
            pdf_file_path = f"{pdf_filename}.pdf"
            with open(pdf_file_path, "rb") as pdf_file:
                st.download_button(
                    label="Download Resume PDF",
                    data=pdf_file,
                    file_name=f"{suggesting_changes.details.name.replace(' ','_')}_resume.pdf",
                    mime="application/pdf"
                )
        except Exception as e:
            st.error(f"Error generating PDF: {str(e)}")
            st.warning("Make sure you have LaTeX (MiKTeX) installed on your system.")
        
        # Get the LaTeX source code
        latex_source = doc.dumps()  # Get the LaTeX source code as string
        
        st.markdown("### Generated LaTeX Code")
        st.code(latex_source, language="latex")
        
        return {
            **state,
            "latex_code": latex_source
        }
        
    except Exception as e:
        st.error(f"Error creating resume: {str(e)}")
        return {
            **state,
            "latex_code": f"Error: {str(e)}"
        }





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
    














