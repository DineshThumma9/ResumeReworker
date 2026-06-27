import { Download, Edit3, Code, TerminalSquare } from "lucide-react";
import { Button } from "../ui/button";

interface EditorToolbarProps {
  onCompile: () => void;
  onDownloadPdf: () => void;
  onDownloadTex: () => void;
  activeTab: "editor" | "logs";
  onTabChange: (tab: "editor" | "logs") => void;
  isCompiling: boolean;
  hasPdf: boolean;
}

export function EditorToolbar({
  onCompile,
  onDownloadPdf,
  onDownloadTex,
  activeTab,
  onTabChange,
  isCompiling,
  hasPdf,
}: EditorToolbarProps) {
  return (
    <div className="flex items-center justify-between p-2 border-b border-border bg-muted/30">
      <div className="flex items-center gap-1">
        <Button
          variant={activeTab === "editor" ? "secondary" : "ghost"}
          size="sm"
          className="gap-2 font-medium"
          onClick={() => onTabChange("editor")}
        >
          <Code size={16} />
          LaTeX Editor
        </Button>
        <Button
          variant={activeTab === "logs" ? "secondary" : "ghost"}
          size="sm"
          className="gap-2 font-medium"
          onClick={() => onTabChange("logs")}
        >
          <TerminalSquare size={16} />
          Build Logs
        </Button>
      </div>

      <div className="flex items-center gap-2">
        <Button
          variant="outline"
          size="sm"
          className="gap-2"
          onClick={onDownloadTex}
        >
          <Download size={16} />
          .tex
        </Button>
        <Button
          variant="outline"
          size="sm"
          className="gap-2"
          onClick={onDownloadPdf}
          disabled={!hasPdf}
        >
          <Download size={16} />
          PDF
        </Button>
        <Button
          variant="default"
          size="sm"
          className="gap-2"
          onClick={onCompile}
          disabled={isCompiling}
        >
          <Edit3 size={16} />
          {isCompiling ? "Compiling..." : "Compile PDF"}
        </Button>
      </div>
    </div>
  );
}
