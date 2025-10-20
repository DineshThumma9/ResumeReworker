

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from schema import ResumeState
from  prompts import resume_analysis_prompt,rewrite_content_prompt,rewrite_latex_prompt
from schema import ResumeAnalysis
from langgraph.graph import StateGraph
from langgraph.constants import START, END
import streamlit as st
import pymupdf
from dotenv import load_dotenv
import os
import pymupdf
import streamlit as st
from pyarrow import output_stream
from schema import ResumeState,RewriteResume,Project
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import BaseModel, Field
from typing import List, Optional
import streamlit as st
from st_circular_progress import CircularProgress
from jakes_template import jakes_template_reference


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
    content = response.model_dump()
    st.markdown("### ReWritten Resume Content")
    for key,val in iterate_nested_dict(content):
        st.markdown(f"## {key.title().replace('_',' ')}\n  {val}")
    

    
    return {
        **state,
        "changes_content": response
    } 



def rewrite_latex(state:ResumeState):
    jd = state['jd']
    initial_resume = state['resume']
    suggesting_changes = state['changes_content']
    
    
    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0,api_key=os.getenv("GEMINI_API_KEY"))
    messages = [
        SystemMessage(content=rewrite_latex_prompt.format(jakes_template=jakes_template_reference)),
        HumanMessage(content=f"Job Description:\n{jd}\n\nInitial Resume:\n{initial_resume}\n\nSuggested Changes:\n{suggesting_changes}"),
    ]
    resume_latex = llm.invoke(messages)
    st.markdown("### Generated LaTeX Code for ReWritten Resume")
    st.code(resume_latex,language="latex")
    return {
        **state,
        "latex_code": resume_latex
    }

def generate_pdf():
    pass



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
    


def create_workflow():
    pass