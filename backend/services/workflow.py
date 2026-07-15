import asyncio
import base64
import json
import logging
import re
import subprocess
from typing import Literal, Optional, cast

import cloudconvert
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.constants import END, START
from langgraph.graph import StateGraph

from core.config import settings
from schemas.schema import (
    Details,
    JudgeResume,
    ResumeAnalysis,
    ResumeState,
    RewriteResume,
)
from services.llm_service import get_llm_client
from services.renderer import render_resume_template, render_resume_template_from_string
from utils.constants import MAX_REWRITE_ITERATIONS
from utils.prompts import (
    extract_details_prompt,
    resume_analysis_prompt,
    rewrite_content_prompt,
)

logger = logging.getLogger(__name__)


class ResumeWorkflowService:
    def __init__(self, cloudconvert_api_key: str | None = None):
        api_key = cloudconvert_api_key or settings.cloudconvert_api_key
        if api_key:
            cloudconvert.configure(api_key=api_key)
        self.graph = self._build_graph()

    def _build_graph(self):
        graph = StateGraph(ResumeState)  # type: ignore
        graph.add_node("match_jd", self.match_jd)
        graph.add_node("rewrite_resume", self.rewrite_resume)
        graph.add_node("judge_resume", self.judge_rewrite)
        graph.add_node("rewrite_latex", self.rewrite_latex)
        graph.add_edge(START, "match_jd")
        graph.add_edge("match_jd", "rewrite_resume")
        graph.add_edge("rewrite_resume", "judge_resume")
        graph.add_conditional_edges(source="judge_resume", path=self.route_path)
        graph.add_edge("rewrite_latex", END)
        return graph.compile()

    def route_path(
        self, state: "ResumeState"
    ) -> Literal["rewrite_resume", "rewrite_latex"]:
        iteration = int(state.get("iteration", 1))
        judgements = state.get("judgements", [])

        # Process and log the last judgement details if available (important for UI status updates)
        judgement = judgements[-1] if judgements else None
        should_rewrite = False
        req_changes = []
        if judgement:
            if isinstance(judgement, dict):
                should_rewrite = judgement.get("should_rewrite", False)
                req_changes = judgement.get("request_changes", [])
            else:
                should_rewrite = getattr(judgement, "should_rewrite", False)
                req_changes = getattr(judgement, "request_changes", [])

            if should_rewrite:
                logger.info(
                    f"Judge rejected rewrite (iteration {iteration}). {len(req_changes)} changes requested:"
                )
                for idx, change in enumerate(req_changes):
                    change_str = str(change)
                    truncated = (
                        change_str[:150] + "..."
                        if len(change_str) > 150
                        else change_str
                    )
                    logger.info(f"  - {truncated}")
            else:
                logger.info(
                    f"Judge approved rewrite (iteration {iteration}). Proceeding to LaTeX."
                )

        if not judgements or iteration >= MAX_REWRITE_ITERATIONS:
            logger.info(
                f"Proceeding to rewrite_latex. Iteration: {iteration} (max iterations reached or no judgements)."
            )
            return "rewrite_latex"

        return "rewrite_resume" if should_rewrite else "rewrite_latex"

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
        page_count = state.get("page_count")
        pc_str = f"\nOriginal Resume Page Count: {page_count}" if page_count else ""

        from datetime import datetime

        current_date = datetime.now().strftime("%B %Y")
        messages = [
            SystemMessage(
                content=f"Current Date: {current_date}\n\n{resume_analysis_prompt}"
            ),
            HumanMessage(
                content=f"Job Description:\n{jd}\n\nCandidate Resume:\n{resume}{pc_str}"
            ),
        ]

        try:
            llm = await self._get_llm(state)  # type: ignore
            structured_llm = llm.with_structured_output(ResumeAnalysis)

            try:
                response = await self._invoke_with_retry(structured_llm, messages)
            except Exception as e:
                logger.error(f"match_jd structured output failed after retries: {e}")
                return {**state, "analysis": None}

            analysis_response = cast(ResumeAnalysis, response)
            analysis = analysis_response.model_dump()
        except Exception as e:
            logger.exception(f"Error in match_jd node: {e}")
            raise e

        return {**state, "analysis": analysis}

    async def _get_llm(self, state: "ResumeState", temperature: Optional[float] = None):
        """Helper: build the LLM instance from state config."""
        return await get_llm_client(
            provider=state.get("provider"),
            model=state.get("model"),
            api_key=state.get("api_key"),
            temperature=temperature,
        )

    async def _invoke_with_retry(self, structured_llm, messages, max_attempts=3):
        from tenacity import AsyncRetrying, stop_after_attempt, wait_exponential

        async for attempt in AsyncRetrying(
            stop=stop_after_attempt(max_attempts),
            wait=wait_exponential(multiplier=1, min=2, max=10),
            reraise=True,
        ):
            with attempt:
                result = await structured_llm.ainvoke(messages)
                if result is None:
                    raise ValueError("LLM returned None for structured output")
                return result

    async def rewrite_resume(self, state: "ResumeState"):
        iteration = int(state.get("iteration", 0)) + 1
        resume = state["resume"]  # type: ignore
        jd = state["jd"]  # type: ignore
        tone = state["tone"]  # type: ignore
        page_count = state.get("page_count")
        pc_str = f"\nOriginal Resume Page Count: {page_count}" if page_count else ""
        exclude_sections = [
            sec for sec, sec_val in state.get("exclude_sections", {}).items() if sec_val
        ]

        if state.get("analysis") is None:
            return {**state, "changes_content": None, "iteration": iteration}

        try:
            analysis = state["analysis"]  # type: ignore
            if not isinstance(analysis, dict):
                analysis_dict = analysis.model_dump()  # type: ignore
            else:
                analysis_dict = analysis

            analysis_str = json.dumps(analysis_dict, indent=2)

            llm = await self._get_llm(state)

            # ── Call 1: Extract personal details + links only ────────────────
            # Small, focused schema → models handle it reliably every time
            details_obj: Optional[Details] = None
            try:
                details_llm = llm.with_structured_output(Details)
                details_messages = [
                    SystemMessage(content=extract_details_prompt),
                    HumanMessage(content=f"Resume text:\n{resume}"),
                ]
                raw_details = await self._invoke_with_retry(
                    details_llm, details_messages
                )
                details_obj: Optional["Details"] = cast("Details", raw_details)
            except Exception as details_err:
                logger.warning(
                    f"Details extraction failed (will rely on validator fallback): {details_err}"
                )

            # Robust URL fallback extraction from the entire resume text
            import re

            if details_obj is not None and isinstance(details_obj, Details):
                for full_url in re.findall(r"https?://[^\s\"\'\>]+", resume):
                    m = re.search(r"https?://(?:www\.)?([\w\-\.]+)", full_url)
                    if m:
                        domain = m.group(1).lower()
                        if (
                            domain.endswith(".com")
                            or domain.endswith(".org")
                            or domain.endswith(".net")
                            or domain.endswith(".io")
                        ):
                            domain = domain[:-4]

                        if domain not in details_obj.profile_links:
                            details_obj.profile_links[domain] = full_url

            # ── Call 2: Rewrite full content ─────────────────────────────────
            structured_llm = llm.with_structured_output(RewriteResume)

            # If Call 1 succeeded, tell the model the links are already known
            details_hint = ""
            if details_obj is not None and isinstance(details_obj, Details):
                details_hint = (
                    f"\n\n[PRE-EXTRACTED CONTACT INFO — copy these exactly into profile_links, do not change]\n"
                    f"Name: {details_obj.name}\n"
                    f"Links: {details_obj.profile_links}\n"
                )

            judgements = state.get("judgements", [])
            judgement_hint = ""
            if judgements:
                all_requests = []
                for i, j in enumerate(judgements, 1):
                    req = (
                        j.get("request_changes", [])
                        if isinstance(j, dict)
                        else getattr(j, "request_changes", [])
                    )
                    if req:
                        changes_str = "\n- ".join(req)
                        all_requests.append(f"Iteration {i} feedback:\n- {changes_str}")

                if all_requests:
                    history_str = "\n\n".join(all_requests)
                    judgement_hint = (
                        f"\n\n[PREVIOUS FEEDBACK HISTORY TO INCORPORATE]\n"
                        f"You have been asked to revise this resume multiple times. Here is the history of requested changes:\n{history_str}\n"
                        f"Ensure you address ALL unresolved feedback from previous iterations.\n"
                    )

            from datetime import datetime

            current_date = datetime.now().strftime("%B %Y")
            messages = [
                SystemMessage(
                    content=f"Current Date: {current_date}\n\n{rewrite_content_prompt}"
                ),
                HumanMessage(
                    content=(
                        f"Job Description:\n{jd}\n\n"
                        f"Candidate Resume:\n{resume}{pc_str}"
                        f"{details_hint}\n"
                        f"{judgement_hint}\n"
                        f"Analysis Report:\n{analysis_str}\n"
                        f"Tone: {tone}\n"
                        f"Exclude Sections: {exclude_sections}\n"
                    )
                ),
            ]

            try:
                raw_response = await self._invoke_with_retry(structured_llm, messages)
                response = cast(RewriteResume, raw_response)
            except Exception as e:
                logger.error(
                    f"rewrite_resume structured output failed after retries: {e}"
                )
                return {**state, "changes_content": None, "iteration": iteration}

            # If the response has empty profile_links but Call 1 gave us links, merge them
            if (
                details_obj is not None
                and isinstance(details_obj, Details)
                and response.details is not None
                and not response.details.profile_links
            ):
                response.details.profile_links = details_obj.profile_links

            return {**state, "changes_content": response, "iteration": iteration}
        except Exception as e:
            logger.exception(f"Error in rewrite_resume node: {e}")
            raise e

    async def judge_rewrite(self, state: "ResumeState"):
        try:
            changes = state.get("changes_content")
            resume = state.get("resume")
            jd = state.get("jd")
            analysis = state.get("analysis")
            page_count = state.get("page_count")
            pc_str = f"\nOriginal Resume Page Count: {page_count}" if page_count else ""

            from utils.prompts import judge_prompt

            judgements = state.get("judgements", [])
            judgement_history = ""
            if judgements:
                all_requests = []
                for i, j in enumerate(judgements, 1):
                    req = (
                        j.get("request_changes", [])
                        if isinstance(j, dict)
                        else getattr(j, "request_changes", [])
                    )
                    if req:
                        changes_str = "\n- ".join(req)
                        all_requests.append(
                            f"Iteration {i} requested changes:\n- {changes_str}"
                        )

                if all_requests:
                    history_str = "\n\n".join(all_requests)
                    judgement_history = (
                        f"\n\n[YOUR PREVIOUS FEEDBACK HISTORY TO REWRITER]\n"
                        f"You previously evaluated earlier versions and requested the following changes:\n{history_str}\n"
                        f"Please evaluate if the rewriter has addressed your feedback in the new 'Candidate Changed Resume'.\n"
                        f"If they have adequately addressed it or properly omitted skills they shouldn't hallucinate, do not keep requesting the same changes.\n"
                    )

            # Serialize changes to JSON
            changes_str = ""
            if changes:
                if hasattr(changes, "model_dump"):
                    changes_str = json.dumps(changes.model_dump(), indent=2)
                elif isinstance(changes, dict):
                    changes_str = json.dumps(changes, indent=2)
                else:
                    changes_str = str(changes)
            else:
                changes_str = "None (No changes have been generated yet)"

            # Serialize analysis to JSON
            analysis_str = ""
            if analysis:
                if hasattr(analysis, "model_dump"):
                    analysis_str = json.dumps(analysis.model_dump(), indent=2)
                elif isinstance(analysis, dict):
                    analysis_str = json.dumps(analysis, indent=2)
                else:
                    analysis_str = str(analysis)
            else:
                analysis_str = "None"

            from datetime import datetime

            current_date = datetime.now().strftime("%B %Y")
            messages = [
                SystemMessage(
                    content=f"Current Date: {current_date}\n\n{judge_prompt}"
                ),
                HumanMessage(
                    content=(
                        f"Job Description:\n{jd}\n\n"
                        f"Candidate Resume:\n{resume}{pc_str}"
                        f"{judgement_history}"
                        f"\n\nCandidate Changed Resume:\n{changes_str}"
                        f"\n\nCandidate Analysis:\n{analysis_str}"
                        f"\n\nRewrite Score: "
                    )
                ),
            ]

            llm = await self._get_llm(state, temperature=0.0)
            structured_llm = llm.with_structured_output(JudgeResume)
            try:
                response = await self._invoke_with_retry(structured_llm, messages)
            except Exception as e:
                logger.error(
                    f"judge_rewrite structured output failed after retries: {e}"
                )
                return {**state}

            new_judgements = judgements.copy()
            new_judgements.append(response)
            return {**state, "judgements": new_judgements}
        except Exception as e:
            logger.exception(f"Error in judge_rewrite node: {e}")
            raise e

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

        # Pre-process latex_string to escape '%' inside \href{...} to prevent LaTeX comment errors
        def escape_href_percent(latex_code: str) -> str:
            def repl(match):
                url = match.group(1)
                escaped_url = re.sub(r"(?<!\\)%", r"\%", url)
                return f"\\href{{{escaped_url}}}"

            return re.sub(r"\\href\{([^{}]+)\}", repl, latex_code)

        latex_string = escape_href_percent(latex_string)

        cmd = ["docker", "run", "-i", "--rm", "latex-compiler"]
        try:
            # Check if docker command is available
            subprocess.run(["docker", "--version"], capture_output=True, check=True)
        except Exception:
            # Fallback to podman
            cmd[0] = "podman"

        try:
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            # Add a 30-second timeout to prevent compilation from hanging indefinitely
            try:
                pdf_bytes, stderr = await asyncio.wait_for(
                    process.communicate(input=latex_string.encode("utf-8")),
                    timeout=30.0,
                )
            except asyncio.TimeoutError:
                try:
                    process.kill()
                except Exception:
                    pass
                raise Exception("LaTeX compilation timed out after 30.0 seconds")

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
            import copy

            clean_data_dict = copy.deepcopy(data_dict)

            # Apply programmatic diff to inject ** and ~~ tags
            original_resume_text = state.get("resume", "")
            from utils.diff_engine import apply_diff_to_data

            diff_data_dict = apply_diff_to_data(original_resume_text, data_dict)

            # Apply exclude_sections logic by removing keys
            if exclude_sections:
                for section in exclude_sections:
                    if section in clean_data_dict:
                        clean_data_dict[section] = None
                    if section in diff_data_dict:
                        diff_data_dict[section] = None

            # Inject Job Description for project skills optimization/relevance sorting
            jd_text = state.get("jd")
            if jd_text:
                clean_data_dict["jd"] = jd_text
                diff_data_dict["jd"] = jd_text

            template_source = state.get("template_source")
            if template_source and template_source.strip():
                latex_code = render_resume_template_from_string(
                    template_source, clean_data_dict, diff=False
                )
                diff_latex_code = render_resume_template_from_string(
                    template_source, diff_data_dict, diff=True
                )
            else:
                latex_code = render_resume_template(
                    "jakes1.tex", clean_data_dict, diff=False
                )
                diff_latex_code = render_resume_template(
                    "jakes1.tex", diff_data_dict, diff=True
                )

            try:
                filename = (
                    f"{suggesting_changes.details.name.replace(' ', '_')}_resume.pdf"
                )
                # Compile clean latex_code
                logger.info("Compiling LaTeX code to clean PDF...")
                pdf_bytes = await self.latex_to_pdf(latex_code, filename)

                diff_pdf_base64_str = ""
                # Compile diff latex_code
                try:
                    diff_filename = f"{suggesting_changes.details.name.replace(' ', '_')}_resume_diff.pdf"
                    logger.info("Compiling LaTeX code to diff PDF...")

                    # Inject definitions for \added and \deleted macros if not already in preamble
                    diff_defs = (
                        "\n% Definitions for latexdiff-style tracking\n"
                        "\\usepackage[normalem]{ulem}\n"
                        "\\providecommand{\\added}[1]{{\\color{blue}#1}}\n"
                        "\\providecommand{\\deleted}[1]{{\\color{red}\\sout{#1}}}\n"
                    )
                    if "\\begin{document}" in diff_latex_code:
                        diff_latex_code = diff_latex_code.replace(
                            "\\begin{document}", f"{diff_defs}\\begin{{document}}"
                        )

                    diff_pdf_bytes = await self.latex_to_pdf(
                        diff_latex_code, diff_filename
                    )
                    if diff_pdf_bytes and len(diff_pdf_bytes) >= 100:
                        diff_pdf_base64 = base64.b64encode(diff_pdf_bytes).decode(
                            "utf-8"
                        )
                        diff_pdf_base64_str = (
                            f"data:application/pdf;base64,{diff_pdf_base64}"
                        )
                except Exception as diff_compile_err:
                    logger.error(f"Failed to compile diff resume: {diff_compile_err}")

                if not pdf_bytes or len(pdf_bytes) < 100:
                    return {
                        **state,
                        "latex_code": latex_code,
                        "diff_latex_code": diff_latex_code,
                        "diff_pdf_base64": diff_pdf_base64_str,
                    }

                pdf_base64 = base64.b64encode(pdf_bytes).decode("utf-8")
                return {
                    **state,
                    "latex_code": latex_code,
                    "diff_latex_code": diff_latex_code,
                    "pdf_base64": f"data:application/pdf;base64,{pdf_base64}",
                    "diff_pdf_base64": diff_pdf_base64_str,
                }

            except Exception as pdf_error:
                logger.error(
                    f"LaTeX Compilation PDF Error inside rewrite_latex: {pdf_error}"
                )
                return {
                    **state,
                    "latex_code": latex_code,
                    "diff_latex_code": diff_latex_code,
                    "error": str(pdf_error),
                }

        except Exception as e:
            return {
                **state,
                "latex_code": "Error: Failed to generate LaTeX template",
                "error": str(e),
            }
