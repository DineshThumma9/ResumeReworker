import { Sparkles } from "lucide-react";
import { Label } from "../ui/label";
import { Input } from "../ui/input";
import { Textarea } from "../ui/textarea";
import { Button } from "../ui/button";
import { PdfUploadZone } from "../PdfUploadZone";
import { type Template } from "../../apis/api";
import { useResumeStore } from "../../store/resumeStore";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "../ui/select";

const TONES = [
  "Professional",
  "Creative",
  "Technical",
  "Concise",
  "Enthusiastic",
];

interface AnalysisFormProps {
  running: boolean;
  templates: Template[];
  provider: string;
  model: string;
  availableModels: Record<string, string[]>;
  onProviderChange: (p: string) => void;
  onModelChange: (m: string) => void;
  onSubmit: (fd: FormData) => void;
}

export function AnalysisForm({
  running,
  templates,
  provider,
  model,
  availableModels,
  onProviderChange,
  onModelChange,
  onSubmit,
}: AnalysisFormProps) {
  const { label, templateId, setResumeState, jd, tone, file } =
    useResumeStore();

  const canSubmit = jd.trim().length > 0;

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!canSubmit) return;

    const fd = new FormData();
    fd.append("jd", jd);
    fd.append("label", label);
    fd.append("tone", tone);
    fd.append("template_id", templateId || "");
    fd.append("provider", provider);
    fd.append("model", model);
    if (file) {
      fd.append("resume_file", file);
    }
    fd.append("exclude_sections", "{}");

    onSubmit(fd);
  };

  return (
    <div className="w-full max-w-5xl mx-auto flex flex-col gap-10 animate-in fade-in slide-in-from-bottom-4 duration-500 mt-4 pb-12">
      {/* Header removed as requested */}

      <form
        onSubmit={handleSubmit}
        className="flex flex-col gap-8 bg-card p-8 md:p-10 rounded-2xl shadow-md"
      >
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          <div className="flex flex-col gap-3">
            <Label className="text-sm font-semibold text-foreground">
              Resume Label{" "}
              <span className="text-muted-foreground font-normal text-xs">
                (optional — auto-generated if blank)
              </span>
            </Label>
            <Input
              placeholder="e.g. Software_Engineer_Google"
              value={label}
              onChange={(e) => setResumeState({ label: e.target.value })}
              className="bg-background h-11 text-base"
            />
          </div>
          <div className="flex flex-col gap-3">
            <Label className="text-sm font-semibold text-foreground">
              Resume PDF <span className="text-destructive">*</span>
            </Label>
            <PdfUploadZone
              file={file}
              onFile={(f) => setResumeState({ file: f })}
            />
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          <div className="flex flex-col gap-3">
            <Label className="text-sm font-semibold text-foreground">
              Tone
            </Label>
            <Select
              value={tone}
              onValueChange={(val) => setResumeState({ tone: val })}
            >
              <SelectTrigger className="flex h-11! w-full rounded-md border border-input bg-background px-4! py-3! text-base shadow-sm text-foreground">
                <SelectValue placeholder="Select tone" />
              </SelectTrigger>
              <SelectContent side="bottom">
                {TONES.map((t) => (
                  <SelectItem key={t} value={t}>
                    {t}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
          <div className="flex flex-col gap-3">
            <Label className="text-sm font-semibold text-foreground">
              Template
            </Label>
            <Select
              value={templateId}
              onValueChange={(val) => setResumeState({ templateId: val })}
            >
              <SelectTrigger className="flex h-11! w-full rounded-md border border-input bg-background px-4! py-3! text-base shadow-sm text-foreground">
                <SelectValue placeholder="Select template" />
              </SelectTrigger>
              <SelectContent side="bottom">
                {templates.map((t) => (
                  <SelectItem key={t.id} value={String(t.id)}>
                    {t.name}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          <div className="flex flex-col gap-3">
            <Label className="text-sm font-semibold text-foreground">
              Provider
            </Label>
            <Select
              value={provider}
              onValueChange={(val) => onProviderChange(val)}
            >
              <SelectTrigger className="flex h-11! w-full rounded-md border border-input bg-background px-4! py-3! text-base shadow-sm text-foreground">
                <SelectValue placeholder="Select provider" />
              </SelectTrigger>
              <SelectContent side="bottom">
                {Object.keys(availableModels).map((p) => (
                  <SelectItem key={p} value={p}>
                    {p}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
          <div className="flex flex-col gap-3">
            <Label className="text-sm font-semibold text-foreground">
              Model
            </Label>
            <Select value={model} onValueChange={(val) => onModelChange(val)}>
              <SelectTrigger className="flex h-11! w-full rounded-md border border-input bg-background px-4! py-3! text-base shadow-sm text-foreground">
                <SelectValue placeholder="Select model" />
              </SelectTrigger>
              <SelectContent side="bottom">
                {(availableModels[provider] || []).map((m) => (
                  <SelectItem key={m} value={m}>
                    {m}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
        </div>

        <div className="flex flex-col gap-3">
          <div className="flex items-center justify-between">
            <Label className="text-sm font-semibold text-foreground">
              Job Description <span className="text-destructive">*</span>
            </Label>
            <span className="text-xs text-muted-foreground bg-muted px-2 py-1 rounded-md">
              {jd.length} characters
            </span>
          </div>
          <Textarea
            className="min-h-[220px] resize-y bg-background font-mono text-base leading-relaxed p-4"
            placeholder="Paste the full job description here..."
            value={jd}
            onChange={(e) => setResumeState({ jd: e.target.value })}
          />
        </div>

        <Button
          type="submit"
          disabled={!canSubmit || running}
          className="mt-4 flex items-center justify-center gap-2 py-7 text-lg font-semibold shadow-lg transition-transform active:scale-[0.98]"
          size="lg"
        >
          <Sparkles size={22} className={running ? "animate-pulse" : ""} />
          {running ? "Processing..." : "Analyze & Rewrite Resume"}
        </Button>
      </form>
    </div>
  );
}
