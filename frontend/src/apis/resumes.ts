import {
  fetchJSON,
  parse,
  ResumeSchema,
  type Resume,
  type AnalyzeEvent,
  API_URL,
} from "./api";
import { useAuthStore } from "../store/authStore";

export const resumeApi = {
  list: async (): Promise<Resume[]> => {
    const raw = await fetchJSON("/resumes");
    return parse(ResumeSchema.array(), raw.resumes);
  },
  get: async (id: number): Promise<Resume> => {
    const raw = await fetchJSON(`/resumes/${id}`);
    return parse(ResumeSchema, raw);
  },
  delete: async (id: number): Promise<void> => {
    await fetchJSON(`/resumes/${id}`, { method: "DELETE" });
  },
  compile: async (
    latexCode: string,
    resumeId?: number | null,
  ): Promise<{ pdfUrl: string }> => {
    const raw = await fetchJSON("/resumes/compile", {
      method: "POST",
      body: JSON.stringify({ latex_code: latexCode, id: resumeId }),
    });
    return { pdfUrl: raw.pdf_url || raw.pdfUrl };
  },
  create: async (
    label: string,
    latexCode: string,
    content?: any,
    pdfUrl?: string,
  ): Promise<Resume> => {
    const raw = await fetchJSON("/resumes", {
      method: "POST",
      body: JSON.stringify({
        label,
        tex_source: latexCode,
        content,
        pdf_url: pdfUrl,
      }),
    });
    return parse(ResumeSchema, raw);
  },
  update: async (
    id: number,
    label: string,
    latexCode: string,
  ): Promise<Resume> => {
    const raw = await fetchJSON(`/resumes/${id}`, {
      method: "PUT",
      body: JSON.stringify({ label, tex_source: latexCode }),
    });
    return parse(ResumeSchema, raw);
  },
  rename: async (id: number, label: string): Promise<Resume> => {
    const raw = await fetchJSON(`/resumes/${id}`, {
      method: "PUT",
      body: JSON.stringify({ label }),
    });
    return parse(ResumeSchema, raw);
  },
  render: async (id: number, templateId: string): Promise<Resume> => {
    const raw = await fetchJSON(
      `/resumes/${id}/render?template_id=${templateId}`,
      {
        method: "PUT",
      },
    );
    return parse(ResumeSchema, raw);
  },
};

export const analyzeResume = async (
  formData: FormData,
  onEvent: (event: AnalyzeEvent) => void,
) => {
  const token = useAuthStore.getState().token;
  const headers: Record<string, string> = {};
  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }

  let res: Response;
  try {
    res = await fetch(`${API_URL}/resumes/analyze`, {
      method: "POST",
      body: formData,
      headers,
    });
  } catch (err) {
    if (err instanceof TypeError) {
      throw new Error(
        "Cannot reach the server. Please check that the backend is running and try again.",
      );
    }
    throw err;
  }
  if (!res.ok) {
    let msg = res.statusText;
    try {
      const errData = await res.json();
      if (errData.detail) {
        msg =
          typeof errData.detail === "string"
            ? errData.detail
            : JSON.stringify(errData.detail);
      }
    } catch (e) {}
    // Map common HTTP status codes to user-friendly messages
    if (res.status === 401)
      msg = `Unauthorized: ${msg || "Please log in again."}`;
    else if (res.status === 402)
      msg = `Payment required: ${msg || "Check your billing settings."}`;
    else if (res.status === 429)
      msg = `Rate limit exceeded. Please wait and try again.`;
    else if (res.status === 500)
      msg = `Server error (500). Please try again later.`;
    else if (res.status === 503)
      msg = `Service unavailable. The server may be overloaded.`;
    throw new Error(msg || `Request failed with status ${res.status}`);
  }
  if (!res.body) throw new Error("No body returned");
  const reader = res.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    buffer += decoder.decode(value, { stream: true });
    const lines = buffer.split("\n");
    // Preserve the last (potentially incomplete) line in the buffer
    buffer = lines.pop() || "";

    for (const line of lines) {
      const trimmed = line.trim();
      if (trimmed.startsWith("data: ")) {
        try {
          const data = JSON.parse(trimmed.slice(6));
          onEvent(data);
        } catch (e) {
          console.error("Error parsing SSE line:", e);
        }
      }
    }
  }

  // Parse remaining content in the buffer if it exists after stream closes
  const remaining = buffer.trim();
  if (remaining.startsWith("data: ")) {
    try {
      const data = JSON.parse(remaining.slice(6));
      onEvent(data);
    } catch (e) {
      console.error("Error parsing final SSE chunk:", e);
    }
  }
};

export interface ModifyEvent {
  event: "chunk" | "error";
  text?: string;
  message?: string;
}

export const modifyResume = async (
  latexCode: string,
  instruction: string,
  provider: string,
  model: string,
  onEvent: (event: ModifyEvent) => void,
) => {
  const token = useAuthStore.getState().token;
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
  };
  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }

  let res: Response;
  try {
    res = await fetch("http://localhost:8000/api/resumes/modify", {
      method: "POST",
      headers,
      body: JSON.stringify({
        latex_code: latexCode,
        instruction,
        provider,
        model,
      }),
    });
  } catch (err) {
    if (err instanceof TypeError) {
      throw new Error(
        "Cannot reach the server. Please check that the backend is running and try again.",
      );
    }
    throw err;
  }

  if (!res.ok) {
    let msg = res.statusText;
    try {
      const errData = await res.json();
      if (errData.detail) {
        msg =
          typeof errData.detail === "string"
            ? errData.detail
            : JSON.stringify(errData.detail);
      }
    } catch (e) {}
    if (res.status === 401)
      msg = `Unauthorized: ${msg || "Please log in again."}`;
    else if (res.status === 402)
      msg = `Payment required: ${msg || "Check your billing settings."}`;
    else if (res.status === 429)
      msg = `Rate limit exceeded. Please wait and try again.`;
    else if (res.status === 500)
      msg = `Server error (500). Please try again later.`;
    throw new Error(msg || `Request failed with status ${res.status}`);
  }

  if (!res.body) throw new Error("No body returned");
  const reader = res.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    buffer += decoder.decode(value, { stream: true });
    const lines = buffer.split("\n");
    buffer = lines.pop() || "";

    for (const line of lines) {
      const trimmed = line.trim();
      if (trimmed.startsWith("data: ")) {
        try {
          const data = JSON.parse(trimmed.slice(6));
          onEvent(data);
        } catch (e) {
          console.error("Error parsing SSE line:", e);
        }
      }
    }
  }

  const remainingChunk = buffer.trim();
  if (remainingChunk.startsWith("data: ")) {
    try {
      const data = JSON.parse(remainingChunk.slice(6));
      onEvent(data);
    } catch (e) {
      console.error("Error parsing final SSE chunk:", e);
    }
  }
};
