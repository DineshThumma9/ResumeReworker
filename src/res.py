from pylatex import Document, NoEscape

from schema import RewriteResume


# ============= RESUME GENERATOR WITH OPTIMIZED SPACING =============

def escape_latex(text: str) -> str:
    """
    Escape special LaTeX characters in text more carefully.
    """
    if not text:
        return ""
    
    # Handle & character properly for LaTeX
    special_chars = {
        '\\': r'\textbackslash{}',
        '&': r'\&',
        '%': r'\%',
        '$': r'\$',
        '#': r'\#',
        '_': r'\_',
        '{': r'\{',
        '}': r'\}',
        '~': r'\textasciitilde{}',
        '^': r'\textasciicircum{}',
    }
    
    result = text
    # Process backslash first to avoid double escaping
    for char, escaped in special_chars.items():
        result = result.replace(char, escaped)
    
    return result


def create_resume_from_schema(
        resume_content: RewriteResume
) -> Document:
    """
    Create a one-page resume PDF using PyLaTeX with Jake's template styling.
    Fixed version with proper spacing and no content overflow.

    Args:
        resume_content: RewriteResume Pydantic model with all resume sections
        output_filename: Output PDF filename (without extension)

    Returns:
        Document: PyLaTeX Document object
    """

    # More precise margins matching Jake's template exactly
    doc = Document(
        documentclass='article',
        document_options=['letterpaper', '11pt']
    )

    # Manual margin setup to match Jake's template exactly
    doc.preamble.append(NoEscape(r'\usepackage{latexsym}'))
    doc.preamble.append(NoEscape(r'\usepackage[empty]{fullpage}'))
    doc.preamble.append(NoEscape(r'\usepackage{titlesec}'))
    doc.preamble.append(NoEscape(r'\usepackage{marvosym}'))
    doc.preamble.append(NoEscape(r'\usepackage[usenames,dvipsnames]{color}'))
    doc.preamble.append(NoEscape(r'\usepackage{verbatim}'))
    doc.preamble.append(NoEscape(r'\usepackage{enumitem}'))
    doc.preamble.append(NoEscape(r'\usepackage[hidelinks]{hyperref}'))
    doc.preamble.append(NoEscape(r'\usepackage{fancyhdr}'))
    doc.preamble.append(NoEscape(r'\usepackage[english]{babel}'))
    doc.preamble.append(NoEscape(r'\usepackage{tabularx}'))
    # Removed fontawesome dependency for better CloudConvert compatibility
    doc.preamble.append(NoEscape(r'\usepackage{multicol}'))
    doc.preamble.append(NoEscape(r'\setlength{\multicolsep}{-3.0pt}'))
    doc.preamble.append(NoEscape(r'\setlength{\columnsep}{-1pt}'))
    doc.preamble.append(NoEscape(r'\input{glyphtounicode}'))
    
    # Page style and headers
    doc.preamble.append(NoEscape(r'\pagestyle{fancy}'))
    doc.preamble.append(NoEscape(r'\fancyhf{}'))
    doc.preamble.append(NoEscape(r'\fancyfoot{}'))
    doc.preamble.append(NoEscape(r'\renewcommand{\headrulewidth}{0pt}'))
    doc.preamble.append(NoEscape(r'\renewcommand{\footrulewidth}{0pt}'))
    
    # Margins exactly like Jake's template
    doc.preamble.append(NoEscape(r'\addtolength{\oddsidemargin}{-0.6in}'))
    doc.preamble.append(NoEscape(r'\addtolength{\evensidemargin}{-0.5in}'))
    doc.preamble.append(NoEscape(r'\addtolength{\textwidth}{1.19in}'))
    doc.preamble.append(NoEscape(r'\addtolength{\topmargin}{-.7in}'))
    doc.preamble.append(NoEscape(r'\addtolength{\textheight}{1.4in}'))
    
    # Other settings
    doc.preamble.append(NoEscape(r'\urlstyle{same}'))
    doc.preamble.append(NoEscape(r'\raggedbottom'))
    doc.preamble.append(NoEscape(r'\raggedright'))
    doc.preamble.append(NoEscape(r'\setlength{\tabcolsep}{0in}'))

    # Section formatting matching Jake's template exactly
    doc.preamble.append(NoEscape(r'''
\titleformat{\section}{
  \vspace{-4pt}\scshape\raggedright\large\bfseries
}{}{0em}{}[\color{black}\titlerule \vspace{-5pt}]
'''))

    # Custom commands matching Jake's template exactly
    doc.preamble.append(NoEscape(r'\pdfgentounicode=1'))
    doc.preamble.append(NoEscape(r'''
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
'''))

    # Header - simplified to match Jake's template exactly
    doc.append(NoEscape(r'\begin{center}'))
    doc.append(NoEscape(r'{\Huge \scshape ' + escape_latex(resume_content.details.name) + r'} \\ \vspace{1pt}'))
    
    # Contact info - extract different types properly
    contact_parts = []
    
    # Add phone if available
    if resume_content.details.contact:
        contact_parts.append(escape_latex(resume_content.details.contact))

    # Add email if available
    if resume_content.details.email:
        contact_parts.append(r'\href{mailto:' + escape_latex(resume_content.details.email) + r'}{\underline{' + escape_latex(resume_content.details.email) + r'}}')

    if resume_content.details.github:
        contact_parts.append(r'\href{' + resume_content.details.github + r'}{\underline{GitHub}}')  
        
    if resume_content.details.leetcode:
        contact_parts.append(r'\href{' + resume_content.details.leetcode + r'}{\underline{LeetCode}}')  
        
    if resume_content.details.linkedin:
        contact_parts.append(r'\href{' + resume_content.details.linkedin + r'}{\underline{LinkedIn}}')  
    if resume_content.details.location:
        contact_parts.append(escape_latex(resume_content.details.location)) 
    if resume_content.details.codechef:
        contact_parts.append(r'\href{' + resume_content.details.codechef + r'}{\underline{CodeChef}}')
    if resume_content.details.portfolio:
        contact_parts.append(r'\href{' + resume_content.details.portfolio + r'}{\underline{Portfolio}}')
    
    
    if contact_parts:
        doc.append(NoEscape(' $|$ '.join(contact_parts)))
    doc.append(NoEscape(r'\end{center}'))  # Aggressive space reduction

    # ============= PROFESSIONAL SUMMARY =============
    if resume_content.details.profile_summary:
        doc.append(NoEscape(r'\section{Professional Summary}'))
        doc.append(NoEscape(r'\resumeSubHeadingListStart'))
        doc.append(NoEscape(r'\resumeItem{' + escape_latex(resume_content.details.profile_summary) + r'}'))
        doc.append(NoEscape(r'\resumeSubHeadingListEnd'))

    # ============= EDUCATION =============
    if resume_content.education:
        doc.append(NoEscape(r'\section{Education}'))
        doc.append(NoEscape(r'\resumeSubHeadingListStart')) 
        for edu in resume_content.education:
            year_str = edu.year if edu.year else ''
            gpa_str = edu.gpa if edu.gpa else ''
            doc.append(NoEscape(
                r'\resumeSubheading{' + escape_latex(edu.institution) + r'}{' +
                escape_latex(year_str) + r'}{' +
                escape_latex(edu.course) + r'}{' +
                escape_latex(gpa_str) + r'}'
            ))
        doc.append(NoEscape(r'\resumeSubHeadingListEnd'))

    # ============= TECHNICAL SKILLS =============
    if resume_content.technical_skills:
        doc.append(NoEscape(r'\section{Technical Skills}'))
        doc.append(NoEscape(r'\begin{itemize}[leftmargin=0.15in, label={}]'))
        doc.append(NoEscape(r'\small{\item{'))

        for i, skill_obj in enumerate(resume_content.technical_skills):
            skill_list = ', '.join([escape_latex(s) for s in skill_obj.skill_set])
            end_char = r' \\' if i < len(resume_content.technical_skills) - 1 else ''
            doc.append(NoEscape(
                r'\textbf{' + escape_latex(skill_obj.skill) + r'}{: ' + skill_list + r'}' + end_char
            ))

        doc.append(NoEscape(r'}}'))
        doc.append(NoEscape(r'\end{itemize}'))

    # ============= PROJECTS =============
    if resume_content.projects:
        doc.append(NoEscape(r'\section{Projects}'))
        doc.append(NoEscape(r'\resumeSubHeadingListStart'))

        for project in resume_content.projects:
            # Tech stack formatting
            tech_stack = ', '.join([escape_latex(t) for t in project.technologies])
            
            # Check for project links
            links = []
            if hasattr(project, 'frontend_link') and project.frontend_link:
                links.append(r'\href{' + project.frontend_link + r'}{\underline{Frontend}}')
            if hasattr(project, 'backend_link') and project.backend_link:
                links.append(r'\href{' + project.backend_link + r'}{\underline{Backend}}')
            if hasattr(project, 'demo_link') and project.demo_link:
                links.append(r'\href{' + project.demo_link + r'}{\underline{Demo}}')
            
            links_str = ' $|$ '.join(links) if links else ''
            
            # Project heading exactly like Jake's template
            doc.append(NoEscape(
                r'\resumeProjectHeading{\textbf{' + escape_latex(project.name) + 
                r'} $|$ \emph{' + tech_stack + r'}}{' + links_str + r'}'
            ))

            # Project highlights
            if project.highlights:
                doc.append(NoEscape(r'\resumeItemListStart'))
                for highlight in project.highlights:
                    doc.append(NoEscape(r'\resumeItem{' + escape_latex(highlight.strip()) + r'}'))
                doc.append(NoEscape(r'\resumeItemListEnd'))

        doc.append(NoEscape(r'\resumeSubHeadingListEnd'))

    # ============= RELEVANT COURSEWORK =============
    if resume_content.coursework:
        doc.append(NoEscape(r'\section{Relevant Coursework}'))
        doc.append(NoEscape(r'\begin{multicols}{4}'))
        doc.append(NoEscape(r'\begin{itemize}[itemsep=-5pt, parsep=3pt]'))  # Adjusted spacing to match Jake's template

        for course in resume_content.coursework:
            doc.append(NoEscape(r'\item\small ' + escape_latex(course)))

        doc.append(NoEscape(r'\end{itemize}'))
        doc.append(NoEscape(r'\end{multicols}'))
        doc.append(NoEscape(r'\vspace*{2.0\multicolsep}'))  # Proper spacing after coursework section
     
     
    if resume_content.achivements:
        doc.append(NoEscape(r'\section{Achievements}'))
        doc.append(NoEscape(r'\begin{itemize}[itemsep=-5pt, parsep=3pt]'))  # Adjusted spacing to match Jake's template

        for achievement in resume_content.achivements:
            doc.append(NoEscape(r'\item\small ' + escape_latex(achievement)))

        doc.append(NoEscape(r'\end{itemize}'))
        doc.append(NoEscape(r'\vspace*{2.0\multicolsep}'))  # Proper spacing after achievements section
        
    
    # ============= HACKATHONS & CERTIFICATIONS =============
    if resume_content.hackathons_and_certificates:
        doc.append(NoEscape(r'\section{Hackathons \& Certifications}'))
        doc.append(NoEscape(r'\resumeSubHeadingListStart'))
        
        for cert in resume_content.hackathons_and_certificates:
            # Look for URL pattern to make it a hyperlink
            if 'http' in cert:
                # Split the text into URL and description
                parts = cert.split(' -- ')
                if len(parts) == 2:
                    title, date_info = parts
                    # Find URL in the text
                    url_start = title.find('http')
                    if url_start != -1:
                        url = title[url_start:].split(')')[0].strip()
                        text = title[:url_start].strip()
                        doc.append(NoEscape(
                            r'\resumeItem{\href{' + url + r'}{\underline{\textbf{' + 
                            escape_latex(text) + r'}}} -- ' + escape_latex(date_info) + r'}'
                        ))
                    else:
                        doc.append(NoEscape(r'\resumeItem{' + escape_latex(cert) + r'}'))
                else:
                    doc.append(NoEscape(r'\resumeItem{' + escape_latex(cert) + r'}'))
            else:
                doc.append(NoEscape(r'\resumeItem{' + escape_latex(cert) + r'}'))
            
        doc.append(NoEscape(r'\resumeSubHeadingListEnd'))

    return doc

