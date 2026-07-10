import { Save, FileCode, Users, Play, Loader2, GitCompare } from "lucide-react";
import { Button } from "../ui/button";

interface EditorToolbarProps {
  onCompile: () => void;
  onDownloadPdf: () => void;
  onDownloadTex: () => void;
  onUploadTex: (e: React.ChangeEvent<HTMLInputElement>) => void;
  onSave: () => void;
  onSaveAsTemplate: () => void;
  onShareAnonymous: () => void;
  isCompiling: boolean;
  isSaving: boolean;
  hasPdf: boolean;
  hasResumeId: boolean;
  showDiff: boolean;
  onToggleDiff: () => void;
  hasDiff: boolean;
}

export function EditorToolbar({
  onCompile,
  onDownloadPdf,
  onDownloadTex,
  onUploadTex,
  onSave,
  onSaveAsTemplate,
  onShareAnonymous,
  isCompiling,
  isSaving,
  hasPdf,
  hasResumeId,
  showDiff,
  onToggleDiff,
  hasDiff,
}: EditorToolbarProps) {
  return (
    <div className="flex items-center gap-2">
      <Button
        variant="outline"
        size="sm"
        className="font-sans text-[12px] h-8 rounded-md border-border"
        onClick={onSave}
        disabled={isSaving || !hasResumeId}
      >
        {isSaving ? (
          <Loader2 size={13} className="animate-spin text-muted-foreground" />
        ) : (
          <Save size={13} />
        )}
        <span>Save</span>
      </Button>

      {hasDiff && (
        <Button
          variant={showDiff ? "default" : "outline"}
          size="sm"
          className="font-sans text-[12px] h-8 rounded-md border-border"
          onClick={onToggleDiff}
        >
          <GitCompare size={13} />
          <span>{showDiff ? "Hide Changes" : "Show Changes"}</span>
        </Button>
      )}

      <Button
        variant="outline"
        size="sm"
        className="font-sans text-[12px] h-8 rounded-md border-border"
        onClick={onSaveAsTemplate}
      >
        <FileCode size={13} />
        <span>As Template</span>
      </Button>

      <Button
        variant="outline"
        size="sm"
        className="font-sans text-[12px] h-8 rounded-md border-border"
        onClick={onShareAnonymous}
        disabled={!hasResumeId}
      >
        <Users size={13} />
        <span>Share Anonymous</span>
      </Button>

      <div className="h-4 w-px bg-border mx-1" />

      <div className="relative overflow-hidden">
        <input
          type="file"
          accept=".tex"
          onChange={onUploadTex}
          className="absolute inset-0 opacity-0 cursor-pointer w-full h-full z-10"
          title="Upload .tex file"
        />
        <Button
          variant="ghost"
          size="sm"
          className="font-sans text-[12px] h-8 text-muted-foreground hover:text-foreground px-2 pointer-events-none"
        >
          Upload .tex
        </Button>
      </div>

      <Button
        variant="ghost"
        size="sm"
        className="font-sans text-[12px] h-8 text-muted-foreground hover:text-foreground px-2"
        onClick={onDownloadTex}
      >
        Download .tex
      </Button>

      <Button
        variant="ghost"
        size="sm"
        className="font-sans text-[12px] h-8 text-muted-foreground hover:text-foreground px-2"
        onClick={onDownloadPdf}
        disabled={!hasPdf}
      >
        PDF
      </Button>

      <Button
        variant="default"
        size="sm"
        className="font-sans text-[12px] font-semibold h-8 rounded-md px-3"
        onClick={onCompile}
        disabled={isCompiling}
      >
        {isCompiling ? (
          <>
            <Loader2 size={13} className="animate-spin" />
            <span>Compiling...</span>
          </>
        ) : (
          <>
            <Play size={12} fill="currentColor" />
            <span>Compile PDF</span>
          </>
        )}
      </Button>
    </div>
  );
}
