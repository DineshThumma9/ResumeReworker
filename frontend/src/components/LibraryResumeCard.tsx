import { FileText, Calendar, Trash2 } from "lucide-react";
import type { Resume } from "../schemas";

export function LibraryResumeCard({
  resume,
  onDelete,
}: {
  resume: Resume;
  onDelete: (id: number) => void;
}) {
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
        <div className="flex items-center gap-3">
          <div>
            <h3 className="font-semibold text-foreground truncate max-w-[200px]">
              {resume.label}
            </h3>
            <div className="flex items-center gap-1.5 text-xs text-muted-foreground mt-0.5">
              <Calendar size={12} />
              <span>
                {new Date(resume.updated_at || resume.created_at).toLocaleDateString()}
              </span>
            </div>
          </div>
        </div>
        <button
          onClick={() => onDelete(resume.id)}
          className="p-2 text-muted-foreground hover:text-destructive hover:bg-destructive/10 rounded-lg opacity-0 group-hover:opacity-100 transition-all"
          title="Delete Resume"
        >
          <Trash2 size={16} />
        </button>
      </div>

      <div className="flex gap-2 mt-2">
        {resume.pdf_url && (
          <a
            href={resume.pdf_url}
            target="_blank"
            rel="noreferrer"
            className="flex-1 inline-flex items-center justify-center px-3 py-2 text-sm font-medium rounded-lg bg-primary/10 text-primary hover:bg-primary/20 transition-colors"
          >
            View PDF
          </a>
        )}
        <button className="flex-1 inline-flex items-center justify-center px-3 py-2 text-sm font-medium rounded-lg border border-border bg-background hover:bg-muted text-foreground transition-colors">
          Edit
        </button>
      </div>
    </div>
  );
}
