import { fetchJSON, parse, ResumeSchema, type Resume, type AnalyzeEvent } from "./api";

export const resumeApi = {
  list: async (): Promise<Resume[]> => {
    const raw = await fetchJSON("/resumes");
    return parse(ResumeSchema.array(), raw);
  },
  get: async (id: number): Promise<Resume> => {
    const raw = await fetchJSON(`/resumes/${id}`);
    return parse(ResumeSchema, raw);
  },
  delete: async (id: number): Promise<void> => {
    await fetchJSON(`/resumes/${id}`, { method: "DELETE" });
  },
  compile: async (latexCode: string): Promise<{ pdfUrl: string }> => {
    const raw = await fetchJSON("/resumes/compile", {
      method: "POST",
      body: JSON.stringify({ latex_code: latexCode })
    });
    return { pdfUrl: raw.pdf_url || raw.pdfUrl };
  },
  create: async (label: string, latexCode: string): Promise<Resume> => {
    const raw = await fetchJSON("/resumes", {
      method: "POST",
      body: JSON.stringify({ label, tex_source: latexCode })
    });
    return parse(ResumeSchema, raw);
  },
  render: async (id: number, templateId: string): Promise<Resume> => {
    const raw = await fetchJSON(`/resumes/${id}/render?template_id=${templateId}`, {
      method: "PUT"
    });
    return parse(ResumeSchema, raw);
  },
};

export const analyzeResume = async (
  formData: FormData,
  onEvent: (event: AnalyzeEvent) => void
) => {
  const res = await fetch("http://localhost:8000/api/resumes/analyze", {
    method: "POST",
    body: formData,
  });
  if (!res.body) throw new Error("No body returned");
  const reader = res.body.getReader();
  const decoder = new TextDecoder();
  while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    const chunk = decoder.decode(value);
    const lines = chunk.split("\n");
    for (const line of lines) {
      if (line.trim().startsWith("data: ")) {
        try {
          const data = JSON.parse(line.trim().slice(6));
          onEvent(data);
        } catch (e) {}
      }
    }
  }
};
