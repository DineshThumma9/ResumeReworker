# Resume Reworker 📄✨

An AI-powered resume optimization tool that analyzes your resume against job descriptions and generates professionally formatted, ATS-friendly PDF resumes.

## 🎯 The Idea

Upload your resume and a job description, and let AI:
1. **Analyze** how well your resume matches the job requirements
2. **Provide feedback** on what's missing and what needs improvement
3. **Rewrite** your resume content to better align with the job description
4. **Generate** a professional PDF using Jake's Resume Template

## ✨ Features

- **Resume Analysis**: Get a match score (0-100), missing keywords, negative points, and improvement suggestions
- **AI-Powered Rewriting**: Automatically restructure and optimize your resume content
- **PDF Generation**: Create clean, one-page PDFs using Jake's popular LaTeX template
- **Interactive UI**: Simple Streamlit interface for easy interaction
- **Workflow Management**: LangGraph orchestrates the analysis → rewrite → PDF generation pipeline

## 🏗️ Architecture

```
User Input (Resume + JD)
         ↓
    Streamlit UI
         ↓
   LangGraph Workflow
         ↓
  Analysis (Gemini)
         ↓
  Rewrite (Gemini)
         ↓
  PyLaTeX Generator
         ↓
    PDF Output
```

**Sequential Workflow Steps:**
1. User uploads resume and job description via Streamlit
2. LangGraph orchestrates the sequential workflow
3. **Step 1**: Gemini AI analyzes the resume against the JD
4. **Step 2**: Gemini AI rewrites resume content using analysis results
5. **Step 3**: PyLaTeX generates the final PDF with proper formatting

## 🛠️ Tech Stack

- **Frontend**: Streamlit (Interactive web interface)
- **AI Model**: Google Gemini (Analysis and content generation)
- **Workflow**: LangGraph (State management and orchestration)
- **PDF Generation**: PyLaTeX (LaTeX template to PDF)
- **Data Validation**: Pydantic (Schema validation)

## 📁 Project Structure

```
.
├── .env                      # Environment variables (API keys)
├── requirements.txt          # Python dependencies
└── src/
    ├── __init__.py
    ├── app.py               # Streamlit UI
    ├── jakes_template.py    # PyLaTeX resume generator
    ├── main.py              # LangGraph workflow
    ├── prompts.py           # AI prompts for analysis/rewriting
    ├── res.py               # Helper functions/utilities
    └── schema.py            # Pydantic models (ResumeAnalysis, RewriteResume, etc.)
```

## 🚀 Setup

### Prerequisites

1. **Python 3.8+**
2. **LaTeX Distribution** (for PDF generation):
   ```bash
   # Ubuntu/Debian
   sudo apt-get install texlive-latex-extra texlive-fonts-recommended
   
   # macOS
   brew install --cask mactex
   
   # Windows
   # Download and install MiKTeX: https://miktex.org/download
   ```

### Installation

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd resume-reworker
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   
   Create a `.env` file in the root directory:
   ```env
   GEMINI_API_KEY=your_gemini_api_key_here
   ```
   
   Get your Gemini API key from: https://makersuite.google.com/app/apikey

4. **Run the application**
   ```bash
   streamlit run src/app.py
   ```

5. **Access the app**
   
   Open your browser and go to: `http://localhost:8501`

## 📝 Usage

1. Open the Streamlit interface
2. Upload your current resume (text or PDF)
3. Paste the job description
4. Click "Analyze & Rewrite"
5. Review the analysis feedback
6. Download your optimized resume PDF

## 🔧 Configuration

### Adjusting the Workflow

Edit `src/main.py` to modify the LangGraph workflow steps or add custom logic.

### Customizing Prompts

Modify `src/prompts.py` to change how the AI analyzes or rewrites resumes.

### Template Modifications

Edit `src/jakes_template.py` to adjust PDF formatting, spacing, or styling.

## 📦 Dependencies

Key packages in `requirements.txt`:
- `streamlit` - Web interface
- `langgraph` - Workflow orchestration
- `google-generativeai` - Gemini AI integration
- `pylatex` - LaTeX document generation
- `pydantic` - Data validation
- `python-dotenv` - Environment variable management

## 🐛 Troubleshooting

**LaTeX Errors:**
- Ensure LaTeX is properly installed: `pdflatex --version`
- Install missing packages: `tlmgr install <package-name>`

**API Errors:**
- Verify your `.env` file has the correct `GEMINI_API_KEY`
- Check API quota limits

**PDF Not Generating:**
- Check console for LaTeX compilation errors
- Ensure output directory has write permissions



## 🤝 Contributing

Contributions are welcome! Please open an issue or submit a pull request.
