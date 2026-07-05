import base64
import logging
import subprocess

import cloudconvert
from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.constants import END, START
from langgraph.graph import StateGraph

from core.config import settings
from schemas.schema import ResumeAnalysis, ResumeState, RewriteResume
from services.renderer import render_resume_template, render_resume_template_from_string
from utils.prompts import resume_analysis_prompt, rewrite_content_prompt, extract_details_prompt

logger = logging.getLogger(__name__)


class ResumeWorkflowService:
    def __init__(self, cloudconvert_api_key: str | None = None):
        api_key = cloudconvert_api_key or settings.cloudconvert_api_key
        if api_key:
            cloudconvert.configure(api_key=api_key)
        self.graph = self._build_graph()

    def _build_graph(self):
        graph = StateGraph(ResumeState)
        graph.add_node("match_jd", self.match_jd)
        graph.add_node("rewrite_resume", self.rewrite_resume)
        graph.add_node("rewrite_latex", self.rewrite_latex)
        graph.add_edge(START, "match_jd")
        graph.add_edge("match_jd", "rewrite_resume")
        graph.add_edge("rewrite_resume", "rewrite_latex")
        graph.add_edge("rewrite_latex", END)
        return graph.compile()

    def iterate_nested_dict(self, d, parent_key=""):
        for key, value in d.items():
            full_key = f"{parent_key}.{key}" if parent_key else key
            if isinstance(value, dict):
                yield from self.iterate_nested_dict(value, full_key)
            else:
                yield full_key, value

    async def match_jd(self, state: ResumeState):
        jd = state["jd"]  # type: ignore
        resume = state["resume"]  # type: ignore

        messages = [
            SystemMessage(content=resume_analysis_prompt),
            HumanMessage(
                content=f"Job Description:\n{jd}\n\nCandidate Resume:\n{resume}"
            ),
        ]

        try:
            provider = state["provider"]  # type: ignore
            provider_keys = {
                "openai": settings.openai_api_key,
                "anthropic": settings.anthropic_api_key,
                "google_genai": settings.google_api_key,
                "groq": settings.groq_api_key,
                "mistralai": settings.mistral_api_key,
                "openrouter": settings.openrouter_api_key,
                "huggingface": settings.huggingface_api_key,
            }
            api_key = state.get("api_key") or provider_keys.get(provider)
            llm_kwargs = {}
            if api_key:
                llm_kwargs["api_key"] = api_key
            llm = init_chat_model(state["model"], model_provider=provider, **llm_kwargs)  # type: ignore
            structured_llm = llm.with_structured_output(ResumeAnalysis)

            response = await structured_llm.ainvoke(messages)

            if response is None:
                return {**state, "analysis": None}

            analysis = response.model_dump()
        except Exception as e:
            logger.exception(f"Error in match_jd node: {e}")
            return {**state, "analysis": None}

        return {**state, "analysis": analysis}

    async def _get_llm(self, state: "ResumeState"):
        """Helper: build the LLM instance from state config."""
        provider = state["provider"]  # type: ignore
        provider_keys = {
            "openai": settings.openai_api_key,
            "anthropic": settings.anthropic_api_key,
            "google_genai": settings.google_api_key,
            "groq": settings.groq_api_key,
            "mistralai": settings.mistral_api_key,
            "openrouter": settings.openrouter_api_key,
            "huggingface": settings.huggingface_api_key,
        }
        api_key = state.get("api_key") or provider_keys.get(provider)
        llm_kwargs = {}
        if api_key:
            llm_kwargs["api_key"] = api_key
        return init_chat_model(state["model"], model_provider=provider, **llm_kwargs)  # type: ignore

    async def rewrite_resume(self, state: "ResumeState"):
        resume = state["resume"]  # type: ignore
        jd = state["jd"]  # type: ignore
        tone = state["tone"]  # type: ignore
        exclude_sections = [
            sec for sec, sec_val in state.get("exclude_sections", {}).items() if sec_val
        ]

        if state.get("analysis") is None:
            return {**state, "changes_content": None}

        try:
            analysis = state["analysis"]  # type: ignore
            if not isinstance(analysis, dict):
                analysis = analysis.model_dump()  # type: ignore

            llm = await self._get_llm(state)

            # ── Call 1: Extract personal details + links only ────────────────
            # Small, focused schema → models handle it reliably every time
            details_obj = None
            try:
                from schemas.schema import Details
                details_llm = llm.with_structured_output(Details)
                details_messages = [
                    SystemMessage(content=extract_details_prompt),
                    HumanMessage(
                        content=f"Resume text:\n{resume}"
                    ),
                ]
                details_obj = await details_llm.ainvoke(details_messages)
            except Exception as details_err:
                logger.warning(f"Details extraction failed (will rely on validator fallback): {details_err}")

            # ── Call 2: Rewrite full content ─────────────────────────────────
            structured_llm = llm.with_structured_output(RewriteResume)

            # If Call 1 succeeded, tell the model the links are already known
            details_hint = ""
            if details_obj:
                details_hint = (
                    f"\n\n[PRE-EXTRACTED CONTACT INFO — copy these exactly into profile_links, do not change]\n"
                    f"Name: {details_obj.name}\n"
                    f"Links: {details_obj.profile_links}\n"
                )

            messages = [
                SystemMessage(content=rewrite_content_prompt),
                HumanMessage(
                    content=(
                        f"Job Description:\n{jd}\n\n"
                        f"Candidate Resume:\n{resume}"
                        f"{details_hint}\n\n"
                        f"Analysis Report:\n{analysis}\n"
                        f"Tone: {tone}\n"
                        f"Exclude Sections: {exclude_sections}\n"
                    )
                ),
            ]

            response = await structured_llm.ainvoke(messages)

            if response is None:
                return {**state, "changes_content": None}

            # If the response has empty profile_links but Call 1 gave us links, merge them
            if details_obj and not response.details.profile_links:
                response.details.profile_links = details_obj.profile_links

            return {**state, "changes_content": response}
        except Exception as e:
            logger.exception(f"Error in rewrite_resume node: {e}")
            return {**state, "changes_content": None}

    # =========================================================================
    # OPTIONAL LOCAL COMPILATION ENGINES (Commented out)
    # =========================================================================
    #
    # 1. LOCAL DOCKER-BASED COMPILATION (Requires Docker)
    # To use: Build the image with: `docker build -t latex-compiler -f Dockerfile.latex .`
    #
    # async def latex_to_pdf_local_docker(self, latex_string: str) -> bytes:
    #     import subprocess
    #     try:
    #         process = subprocess.Popen(
    #             ["docker", "run", "-i", "--rm", "latex-compiler"],
    #             stdin=subprocess.PIPE,
    #             stdout=subprocess.PIPE,
    #             stderr=subprocess.PIPE
    #         )
    #         pdf_bytes, stderr = process.communicate(input=latex_string.encode('utf-8'))
    #         if process.returncode != 0:
    #             raise Exception(f"Docker compilation error: {stderr.decode('utf-8', errors='ignore')}")
    #         return pdf_bytes
    #     except Exception as e:
    #         raise Exception(f"Local Docker compilation failed: {e}")
    #
    # 2. LOCAL HOST-BASED COMPILATION (Requires local TeX Live/pdfTeX installed)
    # To use: Swap `latex_to_pdf` logic to run this function.
    #
    # async def latex_to_pdf_local_host(self, latex_string: str) -> bytes:
    #     import tempfile
    #     import os
    #     import subprocess
    #     with tempfile.TemporaryDirectory() as tmpdir:
    #         tex_path = os.path.join(tmpdir, "resume.tex")
    #         with open(tex_path, "w", encoding="utf-8") as f:
    #             f.write(latex_string)
    #
    #         # Run pdflatex command locally
    #         result = subprocess.run(
    #             ["pdflatex", "-interaction=nonstopmode", "-output-directory", tmpdir, tex_path],
    #             capture_output=True
    #         )
    #
    #         pdf_path = os.path.join(tmpdir, "resume.pdf")
    #         if not os.path.exists(pdf_path):
    #             raise Exception(f"Local compilation failed: {result.stderr.decode('utf-8', errors='ignore')}")
    #
    #         with open(pdf_path, "rb") as f:
    #             return f.read()

    # COMMENTED OUT CLOUDCONVERT COMPILATION ENGINE
    # async def latex_to_pdf_cloudconvert(self, latex_string: str, filename: str) -> bytes:
    #     try:
    #         job = cloudconvert.Job.create(payload={
    #             "tasks": {
    #                 "upload-my-file": {
    #                     "operation": "import/upload"
    #                 },
    #                 "convert-to-pdf": {
    #                     "operation": "convert",
    #                     "input": "upload-my-file",
    #                     "input_format": "tex",
    #                     "output_format": "pdf",
    #                     "engine": "texlive"
    #                 },
    #                 "export-file": {
    #                     "operation": "export/url",
    #                     "input": "convert-to-pdf"
    #                 }
    #             }
    #         })
    #
    #         upload_task_id = job["tasks"][0]["id"]
    #         upload_task = cloudconvert.Task.find(id=upload_task_id)
    #
    #         with open("temp_resume.tex", "w", encoding="utf-8") as f:
    #             f.write(latex_string)
    #
    #         cloudconvert.Task.upload(
    #             file_name="temp_resume.tex",
    #             task=upload_task
    #         )
    #
    #         job = cloudconvert.Job.wait(id=job["id"])
    #
    #         export_task = None
    #         for task in job.get("tasks", []):
    #             if task.get("operation") == "export/url" and task.get("status") == "finished":
    #                 export_task = task
    #                 break
    #
    #         if export_task is None:
    #             failed_tasks = [task for task in job.get("tasks", []) if task.get("status") == "error"]
    #             if failed_tasks:
    #                 error_msg = f"LaTeX conversion failed: {failed_tasks[0].get('message', 'Unknown error')}"
    #                 raise Exception(error_msg)
    #             else:
    #                 error_msg = "No export task found or conversion incomplete"
    #                 raise Exception(error_msg)
    #
    #         if not export_task.get("result") or not export_task["result"].get("files"):
    #             error_msg = "No files found in export task result"
    #             raise Exception(error_msg)
    #
    #         file_info = export_task["result"]["files"][0]
    #         download_url = file_info["url"]
    #
    #         try:
    #             import httpx
    #             client = httpx.AsyncClient()
    #             response = await client.get(download_url, timeout=30)
    #             response.raise_for_status()
    #             pdf_bytes = response.content
    #         except requests.exceptions.RequestException as e:
    #             try:
    #                 pdf_bytes = cloudconvert.download(
    #                     filename=file_info["filename"],
    #                     url=file_info["url"]
    #                 )
    #             except Exception as sdk_e:
    #                 error_msg = f"Both download methods failed. HTTP: {str(e)}, SDK: {str(sdk_e)}"
    #                 raise Exception(error_msg)
    #
    #         if not pdf_bytes or len(pdf_bytes) < 100:
    #             raise Exception("Downloaded PDF is empty or too small")
    #
    #         if not pdf_bytes.startswith(b'%PDF'):
    #             raise Exception("Downloaded file is not a valid PDF")
    #
    #         if not pdf_bytes.rstrip().endswith(b'%%EOF'):
    #             raise Exception("Downloaded PDF is incomplete or missing EOF marker")
    #
    #         return pdf_bytes
    #
    #     except Exception as e:
    #         error_msg = f"PDF generation failed: {str(e)}"
    #         raise Exception(error_msg)

    async def latex_to_pdf(self, latex_string: str, filename: str) -> bytes:
        """
        Compile LaTeX locally using a container compiler (tries Docker first, falls back to Podman).
        """

        cmd = ["docker", "run", "-i", "--rm", "latex-compiler"]
        try:
            # Check if docker command is available
            subprocess.run(["docker", "--version"], capture_output=True, check=True)
        except Exception:
            # Fallback to podman
            cmd[0] = "podman"

        try:
            process = subprocess.Popen(
                cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            pdf_bytes, stderr = process.communicate(input=latex_string.encode("utf-8"))
            if process.returncode != 0:
                raise Exception(
                    f"Container compilation error: {stderr.decode('utf-8', errors='ignore')}"
                )
            return pdf_bytes
        except Exception as e:
            raise Exception(f"Local container compilation failed: {e}")

    async def rewrite_latex(self, state: ResumeState):
        suggesting_changes = state.get("changes_content")
        exclude_sections = state.get("exclude_sections", {})

        if suggesting_changes is None:
            return {**state, "latex_code": "Error: No resume content to convert"}

        try:
            # Convert schema to dict
            data_dict = suggesting_changes.model_dump()

            # Apply exclude_sections logic by removing keys
            if exclude_sections:
                for section in exclude_sections:
                    if section in data_dict:
                        data_dict[section] = None

            template_source = state.get("template_source")
            if template_source and template_source.strip():
                latex_code = render_resume_template_from_string(
                    template_source, data_dict
                )
            else:
                latex_code = render_resume_template("jakes1.tex", data_dict)

            try:
                filename = (
                    f"{suggesting_changes.details.name.replace(' ', '_')}_resume.pdf"
                )
                pdf_bytes = await self.latex_to_pdf(latex_code, filename)

                if not pdf_bytes or len(pdf_bytes) < 100:
                    return {**state, "latex_code": latex_code}

                pdf_base64 = base64.b64encode(pdf_bytes).decode("utf-8")
                return {
                    **state,
                    "latex_code": latex_code,
                    "pdf_base64": f"data:application/pdf;base64,{pdf_base64}",
                }

            except Exception as pdf_error:
                return {**state, "latex_code": latex_code, "error": str(pdf_error)}

        except Exception as e:
            return {
                **state,
                "latex_code": "Error: Failed to generate LaTeX template",
                "error": str(e),
            }
