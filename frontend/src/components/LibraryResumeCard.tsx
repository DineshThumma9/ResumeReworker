import { useState } from "react";
import { FileText, Calendar, Trash2, Edit2 } from "lucide-react";
import type { Resume } from "../schemas";
import { useNavigate } from "react-router-dom";
import { useResumeStore } from "../store/resumeStore";
import { resumeApi } from "../apis/resumes";
import { templateApi } from "../apis/templates";
import useSWR from "swr";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
  DialogFooter,
} from "./ui/dialog";
import { Input } from "./ui/input";
import { Button } from "./ui/button";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
} from "./ui/select";
import { Loader2 } from "lucide-react";

export function LibraryResumeCard({
  resume,
  onDelete,
  onRename,
}: {
  resume: Resume;
  onDelete: (id: number) => void;
  onRename: (id: number, label: string) => void;
}) {
  const navigate = useNavigate();
  const setResumeState = useResumeStore((s) => s.setResumeState);
  const [isRenameOpen, setIsRenameOpen] = useState(false);
  const [newLabel, setNewLabel] = useState(resume.label);
  const [isRendering, setIsRendering] = useState(false);
  const [selectedTemplateId, setSelectedTemplateId] = useState<string | null>(null);
  const [isStyleDialogOpen, setIsStyleDialogOpen] = useState(false);

  const { data: templates } = useSWR("templates", templateApi.list);

  const handleRenameSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (newLabel && newLabel.trim() && newLabel.trim() !== resume.label) {
      onRename(resume.id, newLabel.trim());
    }
    setIsRenameOpen(false);
  };

  const handleViewPdf = (e: React.MouseEvent) => {
    e.preventDefault();
    if (!resume.pdf_url) return;

    if (resume.pdf_url.startsWith("data:application/pdf;base64,")) {
      try {
        const base64Parts = resume.pdf_url.split(",");
        const base64Data = base64Parts[1];
        const byteCharacters = atob(base64Data);
        const byteNumbers = new Array(byteCharacters.length);
        for (let i = 0; i < byteCharacters.length; i++) {
          byteNumbers[i] = byteCharacters.charCodeAt(i);
        }
        const byteArray = new Uint8Array(byteNumbers);
        const blob = new Blob([byteArray], { type: "application/pdf" });
        const blobUrl = URL.createObjectURL(blob);
        window.open(blobUrl, "_blank");
      } catch (err) {
        console.error("Failed to parse base64 PDF:", err);
        window.open(resume.pdf_url, "_blank");
      }
    } else {
      window.open(resume.pdf_url, "_blank");
    }
  };

  const handleStyleConfirm = async (mode: "inplace" | "copy") => {
    if (!selectedTemplateId) return;
    try {
      setIsRendering(true);
      if (mode === "inplace") {
        await resumeApi.render(resume.id, selectedTemplateId);
      } else {
        const newResume = await resumeApi.create(resume.label + " (Copy)", resume.tex_source || "", resume.content);
        await resumeApi.render(newResume.id, selectedTemplateId);
      }
      window.location.reload();
    } catch (e) {
      console.error(e);
    } finally {
      setIsRendering(false);
      setIsStyleDialogOpen(false);
      setSelectedTemplateId(null);
    }
  };

  return (
    <div className="flex flex-col gap-4 p-5 rounded-2xl border border-border bg-card shadow-sm hover:shadow-md transition-shadow relative group">
      {/* Thumbnail */}
      <div
        className="w-full rounded-lg bg-muted overflow-hidden border border-border relative"
        style={{ aspectRatio: "1 / 1.414" }}
      >
        {resume.preview_url ? (
          <img
            src={resume.preview_url}
            alt={resume.label}
            className="w-full h-full object-contain transition-transform duration-300 group-hover:scale-[1.02]"
          />
        ) : (
          <div className="w-full h-full flex items-center justify-center text-muted-foreground opacity-30">
            <FileText size={48} strokeWidth={1} />
          </div>
        )}
      </div>

      <div className="flex items-start justify-between">
        <div className="flex items-center gap-3 min-w-0 flex-1">
          <div className="min-w-0 flex-1">
            <h3
              className="font-semibold text-foreground truncate max-w-[200px]"
              title={resume.label}
            >
              {resume.label}
            </h3>
            <div className="flex items-center gap-1.5 text-xs text-muted-foreground mt-0.5">
              <Calendar size={12} />
              <span>
                {new Date(
                  resume.updated_at || resume.created_at,
                ).toLocaleDateString()}
              </span>
            </div>
          </div>
        </div>
        <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-all ml-2 shrink-0">
          <button
            onClick={() => {
              setNewLabel(resume.label);
              setIsRenameOpen(true);
            }}
            className="p-2 text-muted-foreground hover:text-primary hover:bg-primary/10 rounded-lg transition-all"
            title="Rename Resume"
          >
            <Edit2 size={16} />
          </button>
          <button
            onClick={() => onDelete(resume.id)}
            className="p-2 text-muted-foreground hover:text-destructive hover:bg-destructive/10 rounded-lg transition-all"
            title="Delete Resume"
          >
            <Trash2 size={16} />
          </button>
        </div>
      </div>

      <div className="flex gap-2 mt-2">
        {resume.pdf_url ? (
          <button
            onClick={handleViewPdf}
            className="flex-1 inline-flex items-center justify-center px-3 py-2 text-sm font-medium rounded-lg bg-primary/10 text-primary hover:bg-primary/20 transition-colors"
          >
            View PDF
          </button>
        ) : null}
        <button
          onClick={() => {
            setResumeState({
              resumeId: resume.id,
              latexCode: resume.tex_source || "",
              pdfUrl: resume.pdf_url || null,
              templateId: resume.template_id ? String(resume.template_id) : "",
              label: resume.label,
            });
            navigate("/analyze", { state: { tab: "editor" } });
          }}
          className="flex-1 inline-flex items-center justify-center px-3 py-2 text-sm font-medium rounded-lg border border-border bg-background hover:bg-muted text-foreground transition-colors"
        >
          Edit
        </button>
        <Select
          onValueChange={(val) => {
            setSelectedTemplateId(val);
            setIsStyleDialogOpen(true);
          }}
          disabled={isRendering || !templates}
          value=""
        >
          <SelectTrigger className="flex-1 inline-flex items-center justify-center px-3 py-2 text-sm font-medium rounded-lg border border-border bg-background hover:bg-muted text-foreground transition-colors disabled:opacity-50 h-[38px]">
            {isRendering ? (
              <Loader2 className="w-4 h-4 animate-spin" />
            ) : (
              <span>Style</span>
            )}
          </SelectTrigger>
          <SelectContent>
            {templates?.map((t) => (
              <SelectItem key={t.id} value={String(t.id)}>
                {t.name}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>

      {/* STYLE DIALOG */}
      <Dialog open={isStyleDialogOpen} onOpenChange={setIsStyleDialogOpen}>
        <DialogContent className="sm:max-w-md">
          <DialogHeader>
            <DialogTitle>Change Resume Style</DialogTitle>
            <DialogDescription>
              Do you want to update this resume in-place, or create a copy with the new style?
            </DialogDescription>
          </DialogHeader>
          <DialogFooter className="flex gap-2 sm:justify-center mt-4">
            <Button
              type="button"
              variant="outline"
              disabled={isRendering}
              onClick={() => handleStyleConfirm("copy")}
            >
              Make a Copy
            </Button>
            <Button
              type="button"
              disabled={isRendering}
              onClick={() => handleStyleConfirm("inplace")}
            >
              Save In-place
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* RENAME DIALOG */}
      <Dialog open={isRenameOpen} onOpenChange={setIsRenameOpen}>
        <DialogContent className="sm:max-w-md">
          <form onSubmit={handleRenameSubmit} className="space-y-4">
            <DialogHeader>
              <DialogTitle>Rename Resume</DialogTitle>
              <DialogDescription>
                Enter a new name/label for this resume.
              </DialogDescription>
            </DialogHeader>
            <div className="py-2">
              <Input
                value={newLabel}
                onChange={(e) => setNewLabel(e.target.value)}
                placeholder="Resume name..."
                autoFocus
              />
            </div>
            <DialogFooter>
              <Button
                type="button"
                variant="ghost"
                onClick={() => setIsRenameOpen(false)}
              >
                Cancel
              </Button>
              <Button type="submit">Save</Button>
            </DialogFooter>
          </form>
        </DialogContent>
      </Dialog>
    </div>
  );
}
