import useSWR from "swr";
import { Upload, Loader2, Image as ImageIcon } from "lucide-react";
import { templateApi } from "../apis/templates";
import type { Template } from "../schemas";
import { Button } from "../components/ui/button";

import { useNavigate } from "react-router-dom";
import { useResumeStore } from "../store/resumeStore";
export function TemplatesView() {
  const navigate = useNavigate();
  const setResumeState = useResumeStore((s) => s.setResumeState);
  const { data: templates = [], isLoading } = useSWR<Template[]>(
    "templates",
    () => templateApi.list(),
  );

  return (
    <div className="px-6 py-10 flex flex-col gap-6 overflow-y-auto h-full w-full">
      <div className="flex items-end justify-between">
        <div>
          <h1 className="font-['EB_Garamond'] text-[36px] font-semibold text-foreground tracking-tight">
            My Templates
          </h1>
          <p className="text-sm text-muted-foreground mt-1">
            Built-in and custom LaTeX templates for your resumes.
          </p>
        </div>
        <Button className="flex items-center gap-2 text-sm font-semibold shadow-sm">
          <Upload size={15} />
          Upload .tex
        </Button>
      </div>

      {isLoading ? (
        <div className="flex flex-col items-center justify-center gap-4 py-24 text-center text-muted-foreground">
          <Loader2 size={32} className="animate-spin" />
          <p className="font-medium">Loading templates...</p>
        </div>
      ) : templates.length === 0 ? (
        <div className="flex flex-col items-center justify-center gap-4 py-24 text-center">
          <div className="w-16 h-16 rounded-2xl bg-muted flex items-center justify-center">
            <ImageIcon
              size={32}
              strokeWidth={1}
              className="text-muted-foreground"
            />
          </div>
          <div>
            <p className="font-semibold text-foreground">No templates yet</p>
            <p className="text-sm text-muted-foreground mt-1">
              Upload a custom template to get started.
            </p>
          </div>
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {templates.map((t) => (
            <div
              key={t.id}
              onClick={() => {
                setResumeState({
                  latexCode: t.tex_source || "",
                  pdfUrl: t.preview_url || null,
                  templateId: String(t.id),
                  label: t.name,
                });
                navigate("/analyze", { state: { tab: "editor" } });
              }}
              className="border border-border bg-card rounded-xl p-5 flex flex-col gap-2 hover:border-primary/40 hover:shadow-md transition-all cursor-pointer group"
            >
              {/* Full-page preview — A4 aspect ratio (1:1.414), full image visible */}
              <div
                className="w-full rounded-lg bg-muted overflow-hidden border border-border relative mb-2"
                style={{ aspectRatio: "1 / 1.414" }}
              >
                {t.preview_url ? (
                  <img
                    src={t.preview_url}
                    alt={t.name}
                    className="w-full h-full object-contain transition-transform duration-300 group-hover:scale-[1.02]"
                  />
                ) : (
                  <div className="w-full h-full flex items-center justify-center">
                    <ImageIcon
                      size={36}
                      strokeWidth={1}
                      className="text-muted-foreground opacity-30"
                    />
                  </div>
                )}
              </div>
              <div className="flex items-center justify-between">
                <span className="font-semibold text-sm text-foreground">
                  {t.name}
                </span>
                <span
                  className={`text-[10px] font-bold px-2 py-0.5 rounded-full ${
                    t.is_builtin
                      ? "bg-primary/10 text-primary"
                      : "bg-secondary text-secondary-foreground"
                  }`}
                >
                  {t.is_builtin ? "Built-in" : "Custom"}
                </span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
