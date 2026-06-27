import { FileText, Maximize2, Loader2, Download } from "lucide-react";
import { Button } from "../ui/button";

interface PdfPreviewPanelProps {
  pdfUrl: string | null;
  isCompiling: boolean;
}

export function PdfPreviewPanel({ pdfUrl, isCompiling }: PdfPreviewPanelProps) {
  return (
    <div className="w-full h-full bg-[#525659] flex flex-col relative">
      {/* Chrome-like PDF Toolbar */}
      <div className="h-12 bg-[#323639] flex items-center justify-between px-4 shrink-0 shadow-md z-10">
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2 text-zinc-300 bg-zinc-800/50 px-3 py-1.5 rounded-md text-sm font-medium border border-zinc-700/50">
            <FileText size={16} className="text-blue-400" />
            <span className="truncate max-w-[200px]">resume.pdf</span>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <Button
            variant="ghost"
            size="icon"
            className="text-zinc-300 hover:text-white hover:bg-zinc-700 rounded-full h-8 w-8"
            onClick={() => {
              if (pdfUrl) {
                const a = document.createElement("a");
                a.href = pdfUrl;
                a.download = "resume.pdf";
                a.click();
              }
            }}
            disabled={!pdfUrl}
            title="Download PDF"
          >
            <Download size={18} />
          </Button>
          <Button
            variant="ghost"
            size="icon"
            className="text-zinc-300 hover:text-white hover:bg-zinc-700 rounded-full h-8 w-8 hidden md:flex"
            onClick={() => {
              if (pdfUrl) window.open(pdfUrl, "_blank");
            }}
            disabled={!pdfUrl}
            title="Open in new tab"
          >
            <Maximize2 size={18} />
          </Button>
        </div>
      </div>

      <div className="flex-1 relative overflow-hidden bg-[#525659]">
        {isCompiling && (
          <div className="absolute inset-0 z-20 flex flex-col items-center justify-center bg-black/40 backdrop-blur-[2px]">
            <div className="bg-zinc-900/90 border border-zinc-700 p-6 rounded-xl shadow-2xl flex flex-col items-center gap-4">
              <Loader2 className="w-8 h-8 text-blue-400 animate-spin" />
              <p className="text-zinc-200 font-medium">
                Compiling LaTeX...
              </p>
            </div>
          </div>
        )}

        {pdfUrl ? (
          <iframe
            src={`${pdfUrl}#toolbar=0&navpanes=0`}
            className="w-full h-full border-none"
            title="PDF Preview"
          />
        ) : (
          <div className="w-full h-full flex flex-col items-center justify-center text-zinc-400 gap-4">
            <div className="w-20 h-20 bg-zinc-800 rounded-2xl flex items-center justify-center border border-zinc-700 shadow-inner">
              <FileText size={32} className="text-zinc-500" />
            </div>
            <p className="text-lg font-medium">No PDF generated yet</p>
            <p className="text-sm text-zinc-500 max-w-sm text-center">
              Click "Compile PDF" in the editor toolbar to build your resume.
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
