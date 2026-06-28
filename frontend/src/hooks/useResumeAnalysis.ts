import { useState, useEffect } from "react";
import useSWR from "swr";
import { type AnalyzeEvent, type Template } from "../apis/api";
import { analyzeResume, resumeApi } from "../apis/resumes";
import { templateApi } from "../apis/templates";
import { getApiModels, getCurrentModel, modelSelection } from "../apis/setup";
import type { ResumeAnalysis } from "../schemas";
import { useResumeStore } from "../store/resumeStore";

export type StreamLine = {
  type: "progress" | "success" | "error";
  text: string;
  analysis?: ResumeAnalysis;
};

export function useResumeAnalysis() {
  const { resumeId, pdfUrl, setResumeState, latexCode } = useResumeStore();
  const [lines, setLines] = useState<StreamLine[]>([]);
  const [running, setRunning] = useState(false);
  const [isCompiling, setIsCompiling] = useState(false);
  const [templates, setTemplates] = useState<Template[]>([]);
  const [compileError, setCompileError] = useState<string | null>(null);
  const [apiError, setApiError] = useState<string | null>(null);

  const [provider, setProvider] = useState("");
  const [model, setModel] = useState("");
  const [availableModels, setAvailableModels] = useState<Record<string, string[]>>({});

  const { data: modelsData } = useSWR<Record<string, string[]>>("/setup/api-models", () => getApiModels(), {
    dedupingInterval: 24 * 60 * 60 * 1000,
    revalidateOnFocus: false,
  });

  const { data: currentModelData } = useSWR<{provider: string; model: string}>("/setup/current-model", () => getCurrentModel(), {
    dedupingInterval: 24 * 60 * 60 * 1000,
    revalidateOnFocus: false,
  });

  useEffect(() => {
    if (modelsData && currentModelData) {
      setAvailableModels(modelsData);
      if (currentModelData.provider && currentModelData.model) {
        setProvider(currentModelData.provider);
        setModel(currentModelData.model);
      } else {
        const firstProvider = Object.keys(modelsData)[0];
        if (firstProvider) {
          setProvider(firstProvider);
          const firstModel = modelsData[firstProvider][0] || "";
          setModel(firstModel);
          if (firstModel && firstProvider) {
            modelSelection(firstModel, firstProvider).catch((err) => {
              console.error(err);
              setApiError(err instanceof Error ? err.message : String(err));
            });
          }
        }
      }
    }
  }, [modelsData, currentModelData]);

  useEffect(() => {

    templateApi
      .list()
      .then((tpls) => {
        setTemplates(tpls);
        if (tpls.length > 0) setResumeState({ templateId: String(tpls[0].id) });
      })
      .catch(() => setResumeState({ templateId: "jake" }));
  }, []);

  const handleProviderChange = (p: string) => {
    if (!p) return;
    setProvider(p);
    const m = availableModels[p]?.[0] || "";
    setModel(m);
    if (m) {
      modelSelection(m, p).catch((err) => {
        console.error(err);
        setApiError(err instanceof Error ? err.message : String(err));
      });
    }
  };

  const handleModelChange = (m: string) => {
    if (!m || !provider) return;
    setModel(m);
    modelSelection(m, provider).catch((err) => {
      console.error(err);
      setApiError(err instanceof Error ? err.message : String(err));
    });
  };

  const addLine = (line: StreamLine) => {
    setLines((prev) => [...prev, line]);
  };

  const clearLines = () => setLines([]);

  const submitAnalysis = (fd: FormData, onSuccess: () => void) => {
    setLines([]);
    setRunning(true);
    setLines([
      {
        type: "progress",
        text: "Analyzing job description and extracting key requirements...",
      },
    ]);

    analyzeResume(fd, (ev: AnalyzeEvent) => {
      if (ev.event === "progress") {
        if (ev.step === "match_jd") {
          setLines((prev) => {
            const n = [...prev];
            const idx = n.findIndex(l => l.text.includes("Analyzing") || l.type === "progress");
            if (idx >= 0) {
              n[idx] = {
                type: "success",
                text: "JD analysis complete.",
                analysis: ev.analysis,
              };
            } else {
              n.push({
                type: "success",
                text: "JD analysis complete.",
                analysis: ev.analysis,
              });
            }
            return [
              ...n,
              {
                type: "progress",
                text: "AI is rewriting your resume to match the JD...",
              },
            ];
          });
        } else if (ev.step === "rewrite_resume") {
          setLines((prev) => {
            const n = [...prev];
            const lastIdx = n.map(l => l.type).lastIndexOf("progress");
            if (lastIdx >= 0) {
              n[lastIdx] = {
                ...n[lastIdx],
                type: "success",
                text: "Resume rewritten successfully.",
              };
            } else {
              n.push({
                type: "success",
                text: "Resume rewritten successfully.",
              });
            }
            return [
              ...n,
              { type: "progress", text: "Compiling LaTeX document..." },
            ];
          });
        } else {
          addLine({
            type: "progress",
            text: ev.message,
            analysis: ev.analysis,
          });
        }
      }
      if (ev.event === "complete") {
        setRunning(false);
        const latex = ev.latexCode ?? "";
        const compileErr = ev.error;
        const isError = !!compileErr || latex.startsWith("Error:");
        
        setResumeState({
          latexCode: latex || "% No LaTeX was generated.",
          pdfUrl: isError ? null : (ev.pdfUrl || pdfUrl),
          resumeId: ev.resumeId || resumeId,
        });

        if (compileErr) {
          setCompileError(compileErr);
        }

        setLines((prev) => {
          const n = [...prev];
          const last = n.length - 1;
          if (last >= 0 && n[last].type === "progress")
            n[last] = {
              ...n[last],
              type: isError ? "error" : "success",
              text: isError ? "LaTeX compilation failed." : "LaTeX compilation successful.",
            };
          return [
            ...n,
            {
              type: isError ? "error" : "success",
              text: isError ? (compileErr || latex) : "Done! Resume generated.",
            },
          ];
        });
        onSuccess();
      }
      if (ev.event === "error") {
        addLine({ type: "error", text: ev.message });
        setRunning(false);
      }
    }).catch((err) => {
      console.error("Analysis failed:", err);
      addLine({ type: "error", text: err.message || String(err) });
      setRunning(false);
    });
  };

  const handleCompile = async () => {
    try {
      setIsCompiling(true);
      setCompileError(null);
      const res = await resumeApi.compile(latexCode, resumeId);
      setResumeState({ pdfUrl: res.pdfUrl });
    } catch (e: unknown) {
      setCompileError(e instanceof Error ? e.message : String(e));
    } finally {
      setIsCompiling(false);
    }
  };

  return {
    lines,
    clearLines,
    running,
    isCompiling,
    templates,
    provider,
    handleProviderChange,
    model,
    handleModelChange,
    availableModels,
    submitAnalysis,
    handleCompile,
    compileError,
    setCompileError,
    apiError,
    setApiError
  };
}
