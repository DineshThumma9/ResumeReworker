import { useState } from "react";
import { useLocation, Link } from "react-router-dom";
import { ChevronLeft } from "lucide-react";
import Editor from "@monaco-editor/react";
import { useResumeStore } from "../store/resumeStore";
import { useResumeAnalysis } from "../hooks/useResumeAnalysis";
import { AnalysisForm } from "../components/analyze/AnalysisForm";
import { EditorToolbar } from "../components/analyze/EditorToolbar";
import { PdfPreviewPanel } from "../components/analyze/PdfPreviewPanel";
import { Tabs, TabsList, TabsTrigger, TabsContent } from "../components/ui/tabs";

export function AnalyzeView() {
  const { latexCode, setResumeState, pdfUrl } = useResumeStore();

  const {
    running,
    isCompiling,
    provider,
    handleProviderChange: setProvider,
    model,
    handleModelChange: setModel,
    availableModels,
    submitAnalysis: handleAnalysisSubmit,
    handleCompile,
    templates
  } = useResumeAnalysis();

  const location = useLocation();
  const [activeTab, setActiveTab] = useState<string>(
    (location.state as any)?.tab || "analysis"
  );

  const handleDownloadPdf = () => {
    if (pdfUrl) {
      const a = document.createElement("a");
      a.href = pdfUrl;
      a.download = "resume.pdf";
      a.click();
    }
  };

  const handleDownloadTex = () => {
    if (latexCode) {
      const blob = new Blob([latexCode], { type: "text/plain" });
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = "resume.tex";
      a.click();
      URL.revokeObjectURL(url);
    }
  };

  return (
    <div className="flex flex-1 w-full bg-background overflow-hidden font-sans h-full">
      {/* LEFT PANEL: Tabs (Analysis, Editor) */}
      <div className={activeTab === "editor" ? "w-1/2 flex flex-col bg-background" : "w-full flex flex-col bg-background"}>
        <Tabs value={activeTab} onValueChange={setActiveTab} className="flex flex-col h-full">
          <div className="flex items-center justify-between p-2 bg-background">
            <div className="flex items-center gap-2">
              <Link
                to="/"
                className="p-1.5 hover:bg-muted rounded-md transition-colors"
                title="Back to Dashboard"
              >
                <ChevronLeft size={18} />
              </Link>
              <TabsList className="bg-transparent p-0 gap-4">
                <TabsTrigger value="analysis" className="rounded-none border-b-2 border-transparent data-[state=active]:border-primary data-[state=active]:bg-transparent data-[state=active]:shadow-none px-0">Analysis</TabsTrigger>
                <TabsTrigger value="editor" className="rounded-none border-b-2 border-transparent data-[state=active]:border-primary data-[state=active]:bg-transparent data-[state=active]:shadow-none px-0">Editor</TabsTrigger>
              </TabsList>
            </div>
            
            {activeTab === "editor" && (
              <EditorToolbar
                onCompile={handleCompile}
                onDownloadPdf={handleDownloadPdf}
                onDownloadTex={handleDownloadTex}
                activeTab="editor"
                onTabChange={() => {}} // Disabled as we use main tabs
                isCompiling={isCompiling}
                hasPdf={!!pdfUrl}
              />
            )}
          </div>

          <TabsContent value="analysis" className="flex-1 overflow-y-auto min-h-0 p-4 m-0">
            <AnalysisForm
              running={running}
              templates={templates}
              provider={provider}
              model={model}
              availableModels={availableModels}
              onProviderChange={setProvider}
              onModelChange={setModel}
              onSubmit={(fd) => {
                handleAnalysisSubmit(fd, () => {});
              }}
            />
          </TabsContent>

          <TabsContent value="editor" className="flex-1 m-0 bg-[#1e1e1e]">
            <Editor
              height="100%"
              language="latex"
              theme="vs-dark"
              value={latexCode}
              onChange={(v) => setResumeState({ latexCode: v || "" })}
              options={{
                minimap: { enabled: false },
                fontSize: 14,
                wordWrap: "on",
                lineNumbers: "on",
                folding: true,
                scrollBeyondLastLine: false,
                smoothScrolling: true,
                padding: { top: 16 },
              }}
            />
          </TabsContent>
        </Tabs>
      </div>

      {/* RIGHT PANEL: PDF Preview */}
      {activeTab === "editor" && (
        <div className="w-1/2 flex flex-col h-full bg-[#525659]">
          <PdfPreviewPanel pdfUrl={pdfUrl} isCompiling={isCompiling} />
        </div>
      )}
    </div>
  );
}
