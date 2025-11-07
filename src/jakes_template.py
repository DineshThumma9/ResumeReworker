jakes_template_reference = r"""

%-------------------------
% Resume in Latex
% Author : Jake Gutierrez
% Based off of: https://github.com/sb2nov/resume
% License : MIT
%------------------------

\documentclass[letterpaper,11pt]{article}

\usepackage{latexsym}
\usepackage[empty]{fullpage}
\usepackage{titlesec}
\usepackage{marvosym}
\usepackage[usenames,dvipsnames]{color}
\usepackage{verbatim}
\usepackage{enumitem}
\usepackage[hidelinks]{hyperref}
\usepackage{fancyhdr}
\usepackage[english]{babel}
\usepackage{tabularx}
\usepackage{fontawesome5}
\usepackage{multicol}
\setlength{\multicolsep}{-3.0pt}
\setlength{\columnsep}{-1pt}
\input{glyphtounicode}

%----------FONT OPTIONS----------
%sans-serif
%\usepackage[sfdefault]{FiraSans}
%\usepackage[sfdefault]{roboto}
% \usepackage[sfdefault]{noto-sans}
% \usepackage[default]{sourcesanspro}

% serif
% \usepackage{CormorantGaramond}
% \usepackage{charter}

\pagestyle{fancy}
\fancyhf{} % clear all header and footer fields
\fancyfoot{}
\renewcommand{\headrulewidth}{0pt}
\renewcommand{\footrulewidth}{0pt}

% Adjust margins
\addtolength{\oddsidemargin}{-0.6in}
\addtolength{\evensidemargin}{-0.5in}
\addtolength{\textwidth}{1.19in}
\addtolength{\topmargin}{-.7in}
\addtolength{\textheight}{1.4in}

\urlstyle{same}

\raggedbottom
\raggedright
\setlength{\tabcolsep}{0in}

% Sections formatting
\titleformat{\section}{
  \vspace{-4pt}\scshape\raggedright\large\bfseries
}{}{0em}{}[\color{black}\titlerule \vspace{-5pt}]

% Ensure that generate pdf is machine readable/ATS parsable
\pdfgentounicode=1

%-------------------------
% Custom commands
\newcommand{\resumeItem}[1]{
  \item\small{
    {#1 \vspace{-2pt}}
  }
}

\newcommand{\classesList}[4]{
    \item\small{
        {#1 #2 #3 #4 \vspace{-2pt}}
  }
}

\newcommand{\resumeSubheading}[4]{
  \vspace{-2pt}\item
    \begin{tabular*}{1.0\textwidth}[t]{l@{\extracolsep{\fill}}r}
      \textbf{#1} & \textbf{\small #2} \\
      \textit{\small#3} & \textit{\small #4} \\
    \end{tabular*}\vspace{-7pt}
}

\newcommand{\resumeSubSubheading}[2]{
    \item
    \begin{tabular*}{0.97\textwidth}{l@{\extracolsep{\fill}}r}
      \textit{\small#1} & \textit{\small #2} \\
    \end{tabular*}\vspace{-7pt}
}

\newcommand{\resumeProjectHeading}[2]{
    \item
    \begin{tabular*}{1.001\textwidth}{l@{\extracolsep{\fill}}r}
      \small#1 & \textbf{\small #2}\\
    \end{tabular*}\vspace{-7pt}
}

\newcommand{\resumeSubItem}[1]{\resumeItem{#1}\vspace{-4pt}}

\renewcommand\labelitemi{$\vcenter{\hbox{\tiny$\bullet$}}$}
\renewcommand\labelitemii{$\vcenter{\hbox{\tiny$\bullet$}}$}

\newcommand{\resumeSubHeadingListStart}{\begin{itemize}[leftmargin=0.0in, label={}]}
\newcommand{\resumeSubHeadingListEnd}{\end{itemize}}
\newcommand{\resumeItemListStart}{\begin{itemize}}
\newcommand{\resumeItemListEnd}{\end{itemize}\vspace{-5pt}}

%-------------------------------------------
%%%%%%  RESUME STARTS HERE  %%%%%%%%%%%%%%%%%%%%%%%%%%%%

\begin{document}

 {Headings}

%-----------PROFESSIONAL SUMMARY-----------
\section{Professional Summary}
    \resumeSubHeadingListStart
      \resumeItem{Third-year AI \& Data Science student with experience building full-stack applications and AI solutions with a strong foundation in computer science fundamentals and software engineering best practices. Passionate about learning, building reliable systems, and contributing in collaborative environments.}
    \resumeSubHeadingListEnd

%-----------EDUCATION-----------
\section{Education}
  \resumeSubHeadingListStart
    \resumeSubheading
      {CVR College of Engineering}{2023 -- 2027}
      {B.Tech in Artificial Intelligence and Data Science}{7.6/10}
    \resumeSubheading
      {Narayana Junior College}{}
      {Intermediate(MPC)}{}
  \resumeSubHeadingListEnd

%-----------PROGRAMMING SKILLS-----------
\section{Technical Skills}
 \begin{itemize}[leftmargin=0.15in, label={}]
    \small{\item{
     \textbf{Languages}{: Python, Java, TypeScript, Kotlin} \\
     \textbf{Backend Frameworks}{: FastAPI, Spring Boot} \\
     \textbf{Frontend}{: React,Tailwind, CSS, HTML, ShadCN} \\
     \textbf{Database}{: SQL(Postgres,Oracle), NoSQL(MongoDB, Redis, Neo4j)} \\
     \textbf{Developer \& DevOps Tools}{: Git, Docker, Postman, Linux/Unix Environment, Nginx} \\
     \textbf{Gen AI}{: LlamaIndex, LangChain, ChromaDB,spaCy}
    }}
 \end{itemize}

%-----------PROJECTS-----------
\section{Projects}
    \resumeSubHeadingListStart
      \resumeProjectHeading
          {\textbf{CentralGPT} $|$ \emph{FastAPI, React, TypeScript, Redis, Neon, ChromaDB, LlamaIndex}}{\href{https://github.com/DineshThumma9/centralGPT}{\underline{Frontend}} $|$ \href{https://github.com/DineshThumma9/centralGPT-backend}{\underline{Backend}} $|$ \href{https://central-gpt.vercel.app}{\underline{Demo}}}
          \resumeItemListStart
            \resumeItem{Built CentralGPT to integrate OpenAI, Mistral, and Groq APIs with real-time streaming, allowing users to access multiple AI models in one interface.}
            \resumeItem{Implemented specialized RAG pipelines using Jina AI embeddings for code and BAAI embeddings for documents to optimize retrieval accuracy across different content types.}
            \resumeItem{Developed GitHub integration for direct file pinning and source citation functionality to provide transparent, referenced responses from both code repositories and document uploads.}
            \resumeItem{Deployed production system on Azure VM with Nginx reverse proxy and integrated Datadog monitoring for observability, tracking performance metrics and system availability.}
          \resumeItemListEnd

      \resumeProjectHeading
          {\textbf{DevConnect} $|$ \emph{Spring Boot, Neo4j, MongoDB Atlas}}{\href{https://github.com/DineshThumma9/devconnect-backend}{\underline{Repository}}}
          \resumeItemListStart
            \resumeItem{Built backend infrastructure for a developer collaboration platform using Spring Boot with RESTful APIs and authentication.}
            \resumeItem{Designed graph database schema in Neo4j to model relationships between developers, skills, and projects for efficient recommendation queries.}
            \resumeItem{Integrated Azure Blob Storage for media asset management and documented APIs using Swagger for clear interface specification.}
          \resumeItemListEnd
    \resumeSubHeadingListEnd

%------RELEVANT COURSEWORK-------
\section{Relevant Coursework}
    %\resumeSubHeadingListStart
        \begin{multicols}{4}
            \begin{itemize}[itemsep=-5pt, parsep=3pt]
                \item\small Data Structures
                \item Machine Learning
                \item Algorithms Analysis
                \item Database Systems
                \item Artificial Intelligence
                \item Computer Networks
                \item Software Engineering
                \item Web Development
            \end{itemize}
        \end{multicols}
        \vspace*{2.0\multicolsep}
    %\resumeSubHeadingListEnd

%-----------HACKATHONS & CERTIFICATIONS-----------
\section{Hackathons \& Certifications}
    \resumeSubHeadingListStart
        \resumeItem{\href{https://forage-uploads-prod.s3.amazonaws.com/completion-certificates/ifobHAoMjQs9s6bKS/gMTdCXwDdLYoXZ3wG_ifobHAoMjQs9s6bKS_hEkGwzEevW2EAj9fy_1754207033372_completion_certificate.pdf}{\underline{\textbf{Tata Group Data Analytics Job Simulation on Forage}}} -- August 2025}
        \resumeItem{\href{https://unstop.com/certificate-preview/963caedd-48a6-49a7-9e50-ae7c16877ae5?utm_campaign=site-emails}{\underline{\textbf{Adobe India Hackathon}}} -- Participant (August 2025)}
        \resumeItem{\href{https://certificate.hack2skill.com/user/aidayideasubmission/2025H2S06AID-I07282}{\underline{\textbf{Google Agentic-AI Day}}} -- Participant (August 2025)}
    \resumeSubHeadingListEnd
\end{document}


"""