import { useRef, useEffect } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import remarkBreaks from "remark-breaks";
import { type StreamLine } from "../../hooks/useResumeAnalysis";
import {
  Loader2,
  CheckCircle2,
  AlertCircle,
  Sparkles,
  FileText,
  AlertTriangle,
  Lightbulb,
  Target,
} from "lucide-react";

// Beautiful, custom markdown typography aligned with design theme
const Markdown = ({
  children,
  variant = "normal",
}: {
  children: string;
  variant?: "normal" | "tight";
}) => (
  <ReactMarkdown
    remarkPlugins={[remarkGfm, remarkBreaks]}
    components={{
      p: ({ children }) => (
        <p
          className={`${variant === "tight" ? "mb-1 text-sm sm:text-[15px]" : "mb-4 text-[15px] sm:text-base"} leading-[1.6] text-foreground/80 dark:text-foreground/80 last:mb-0`}
        >
          {children}
        </p>
      ),
      h1: ({ children }) => (
        <h1 className="text-xl font-bold mt-6 mb-3 text-foreground tracking-tight">
          {children}
        </h1>
      ),
      h2: ({ children }) => (
        <h2 className="text-lg font-semibold mt-5 mb-2.5 text-foreground tracking-tight">
          {children}
        </h2>
      ),
      h3: ({ children }) => (
        <h3 className="text-base font-semibold mt-4 mb-2 text-foreground tracking-tight">
          {children}
        </h3>
      ),
      h4: ({ children }) => (
        <h4 className="text-sm font-semibold mt-3 mb-1 text-foreground">
          {children}
        </h4>
      ),
      ul: ({ children }) => (
        <ul className="list-disc pl-5 mb-3 space-y-1 text-sm sm:text-[15px] text-foreground/85">
          {children}
        </ul>
      ),
      ol: ({ children }) => (
        <ol className="list-decimal pl-5 mb-3 space-y-1 text-sm sm:text-[15px] text-foreground/85">
          {children}
        </ol>
      ),
      li: ({ children }) => (
        <li className="leading-relaxed pl-1">{children}</li>
      ),
      strong: ({ children }) => (
        <span className="font-medium text-foreground/95">{children}</span>
      ),
      blockquote: ({ children }) => (
        <blockquote className="border-l-4 border-primary/20 pl-4 py-1 italic my-4 text-foreground/60 dark:text-foreground/45">
          {children}
        </blockquote>
      ),
      code: ({ className, children }) => {
        const isBlock = className && className.includes("language-");
        if (isBlock) {
          return (
            <pre className="bg-muted p-4 rounded-lg overflow-x-auto text-[0.85em] font-mono border border-border/60 my-4">
              <code className={className}>{children}</code>
            </pre>
          );
        }
        return (
          <code className="font-medium text-[0.9em] px-1.5 py-0.5 rounded bg-muted/65 text-foreground/90 border border-border/40 font-sans">
            {children}
          </code>
        );
      },
    }}
  >
    {children}
  </ReactMarkdown>
);

interface ProgressStreamProps {
  logs: StreamLine[];
  running: boolean;
  onReset?: () => void;
}

export function ProgressStream({
  logs,
  running,
  onReset,
}: ProgressStreamProps) {
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollIntoView({ behavior: "smooth", block: "end" });
    }
  }, [logs]);

  if (logs.length === 0 && !running) return null;

  const analysisLog = [...logs].reverse().find((l) => l.analysis !== undefined);
  const analysis = analysisLog?.analysis;

  return (
    <div className="w-full max-w-full flex flex-col gap-6 animate-in fade-in duration-300 mt-4 pb-24 px-4 sm:px-6 lg:px-8">
      {/* Top Header */}
      <div className="flex items-center justify-between border-b border-border/40 pb-5 w-full">
        <div className="flex items-center gap-3">
          <h3 className="font-heading text-3xl sm:text-4xl font-semibold text-foreground tracking-tight">
            Analysis Report
          </h3>
          {running ? (
            <span className="flex items-center gap-2 text-xs text-primary font-medium px-3 py-1 bg-primary/10 rounded-full animate-pulse">
              <Loader2 size={13} className="animate-spin" />
              Analyzing
            </span>
          ) : logs.some((l) => l.type === "error") ? (
            <span className="flex items-center gap-2 text-xs text-destructive font-medium px-3 py-1 bg-destructive/10 rounded-full">
              <AlertCircle size={13} />
              Failed
            </span>
          ) : logs.some((l) => l.type === "success") ? (
            <span className="flex items-center gap-2 text-xs text-emerald-600 dark:text-emerald-500 font-medium px-3 py-1 bg-emerald-500/10 rounded-full">
              <CheckCircle2 size={13} />
              Complete
            </span>
          ) : null}
        </div>

        {!running && onReset && (
          <button
            onClick={onReset}
            className="flex items-center gap-2 bg-transparent text-foreground border border-border/60 rounded-lg px-4 py-2 text-xs font-semibold tracking-wider hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors cursor-pointer"
          >
            Start Over
          </button>
        )}
      </div>

      {/* Main Analysis Body */}
      {analysis ? (
        <div className="flex flex-col gap-6 animate-in slide-in-from-bottom-4 duration-500">
          {/* Score & Dashboard Summary Card Grid (Full Width on top) */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {/* ATS Score Card */}
            {analysis.score !== undefined && (
              <div className="flex flex-col justify-between p-6 bg-card border border-border rounded-2xl shadow-xs">
                <span className="text-xs font-bold text-muted-foreground uppercase tracking-widest">
                  ATS Match Score
                </span>
                <div className="mt-4 flex items-baseline gap-2">
                  <span className="font-heading text-5xl sm:text-6xl font-bold text-foreground">
                    {analysis.score}
                  </span>
                  <span className="text-lg text-muted-foreground">/ 100</span>
                </div>
                <div className="mt-3">
                  <span
                    className={`inline-flex items-center justify-center px-3 py-1 rounded-full font-bold uppercase tracking-wider text-[10px] ${
                      analysis.score >= 75
                        ? "bg-emerald-500/10 text-emerald-600 dark:text-emerald-400"
                        : analysis.score >= 50
                          ? "bg-amber-500/10 text-amber-600 dark:text-amber-400"
                          : "bg-destructive/10 text-destructive"
                    }`}
                  >
                    {analysis.score >= 75
                      ? "Excellent Fit"
                      : analysis.score >= 50
                        ? "Moderate Fit"
                        : "Weak Fit"}
                  </span>
                </div>
              </div>
            )}

            {/* Urgency & Status Card */}
            <div className="flex flex-col justify-between p-6 bg-card border border-border rounded-2xl shadow-xs">
              <span className="text-xs font-bold text-muted-foreground uppercase tracking-widest">
                Priority Assessment
              </span>
              <div className="mt-4 flex items-center gap-2">
                <Target className="w-5 h-5 text-primary shrink-0" />
                <span className="font-medium text-foreground text-[15px] leading-tight">
                  {analysis.urgency || "Standard Priority"}
                </span>
              </div>
              <div className="mt-3">
                <span className="text-xs text-muted-foreground">
                  {analysis.urgency
                    ? "Requires timely attention"
                    : "No deadline constraints identified"}
                </span>
              </div>
            </div>

            {/* Assessment Quick Stats Card */}
            <div className="flex flex-col justify-between p-6 bg-card border border-border rounded-2xl shadow-xs">
              <span className="text-xs font-bold text-muted-foreground uppercase tracking-widest">
                Quick Analysis Stats
              </span>
              <div className="mt-4 space-y-2">
                <div className="flex justify-between items-center text-xs">
                  <span className="text-muted-foreground">
                    Missing Keywords:
                  </span>
                  <span className="font-bold text-primary px-1.5 py-0.5 rounded-md bg-primary/10">
                    {analysis.missing_keywords?.length || 0}
                  </span>
                </div>
                <div className="flex justify-between items-center text-xs">
                  <span className="text-muted-foreground">Critical Gaps:</span>
                  <span className="font-bold text-red-500 px-1.5 py-0.5 rounded-md bg-red-500/10">
                    {analysis.negative_points?.length || 0}
                  </span>
                </div>
                <div className="flex justify-between items-center text-xs">
                  <span className="text-muted-foreground">
                    Suggested Actions:
                  </span>
                  <span className="font-bold text-amber-500 px-1.5 py-0.5 rounded-md bg-amber-500/10">
                    {analysis.potential_improvements?.length || 0}
                  </span>
                </div>
              </div>
            </div>
          </div>

          {/* Widescreen 3-Column Dashboard Layout */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 items-start w-full">
            {/* Column 1: Executive Summaries */}
            <div className="flex flex-col gap-6 w-full">
              {(analysis.resume_quality || analysis.match_explanation) && (
                <div className="p-6 bg-card border border-border rounded-2xl shadow-xs">
                  <div className="flex items-center gap-3 border-b border-border/60 pb-4 mb-4">
                    <div className="p-2 bg-primary/10 rounded-lg text-primary">
                      <FileText size={20} />
                    </div>
                    <h3 className="font-heading text-2xl font-semibold text-foreground tracking-tight">
                      Executive Summary
                    </h3>
                  </div>

                  <div className="space-y-6">
                    {analysis.resume_quality && (
                      <div>
                        <h4 className="text-sm font-semibold uppercase tracking-wider text-muted-foreground mb-2">
                          Resume Quality & Structure
                        </h4>
                        <Markdown>{analysis.resume_quality}</Markdown>
                      </div>
                    )}

                    {analysis.resume_quality && analysis.match_explanation && (
                      <hr className="border-border/40" />
                    )}

                    {analysis.match_explanation && (
                      <div>
                        <h4 className="text-sm font-semibold uppercase tracking-wider text-muted-foreground mb-2">
                          JD Alignment Analysis
                        </h4>
                        <Markdown>{analysis.match_explanation}</Markdown>
                      </div>
                    )}
                  </div>
                </div>
              )}
            </div>

            {/* Column 2: Critical Gaps */}
            <div className="flex flex-col gap-6 w-full">
              {analysis.negative_points &&
                analysis.negative_points.length > 0 && (
                  <div className="p-6 bg-red-500/5 dark:bg-red-500/10 border border-red-500/10 dark:border-red-900/20 rounded-2xl shadow-xs animate-in slide-in-from-bottom-4 duration-500 delay-100">
                    <div className="flex items-center gap-3 mb-4 text-red-600 dark:text-red-400">
                      <AlertTriangle size={20} />
                      <h3 className="font-heading text-2xl font-semibold tracking-tight">
                        Critical Gaps
                      </h3>
                    </div>
                    <ul className="space-y-3">
                      {analysis.negative_points.map((pt, idx) => {
                        const content = pt.replace(/^[\-\*\•]\s*/, "");
                        return (
                          <li
                            key={idx}
                            className="flex items-start gap-3 text-sm sm:text-[15px] text-foreground/80 leading-relaxed"
                          >
                            <span className="w-1.5 h-1.5 rounded-full bg-red-500 shrink-0 mt-2" />
                            <div className="flex-1 min-w-0">
                              <Markdown variant="tight">{content}</Markdown>
                            </div>
                          </li>
                        );
                      })}
                    </ul>
                  </div>
                )}
            </div>

            {/* Column 3: Keywords & Suggested Actions */}
            <div className="flex flex-col gap-6 w-full">
              {/* Missing Keywords Card */}
              {analysis.missing_keywords &&
                analysis.missing_keywords.length > 0 && (
                  <div className="p-6 bg-card border border-border rounded-2xl shadow-xs animate-in slide-in-from-bottom-4 duration-500 delay-150">
                    <div className="flex items-center gap-3 border-b border-border/60 pb-4 mb-4">
                      <div className="p-2 bg-primary/10 rounded-lg text-primary">
                        <Sparkles size={20} />
                      </div>
                      <h3 className="font-heading text-2xl font-semibold text-foreground tracking-tight">
                        Missing Keywords
                      </h3>
                    </div>
                    <p className="text-xs text-muted-foreground mb-4">
                      ATS systems scan for these terms. Integrate them naturally
                      into your experience bullets:
                    </p>
                    <div className="flex flex-wrap gap-1.5">
                      {analysis.missing_keywords.map((kw, idx) => (
                        <span
                          key={idx}
                          className="text-xs font-semibold bg-primary/5 text-primary border border-primary/20 dark:bg-primary/10 dark:text-primary-foreground/90 px-2.5 py-1 rounded-full transition-colors hover:bg-primary/10"
                        >
                          {kw}
                        </span>
                      ))}
                    </div>
                  </div>
                )}

              {/* Suggested Actions Card */}
              {analysis.potential_improvements &&
                analysis.potential_improvements.length > 0 && (
                  <div className="p-6 bg-amber-500/5 dark:bg-amber-500/10 border border-amber-500/10 dark:border-amber-900/20 rounded-2xl shadow-xs animate-in slide-in-from-bottom-4 duration-500 delay-200">
                    <div className="flex items-center gap-3 mb-4 text-amber-600 dark:text-amber-400">
                      <Lightbulb size={20} />
                      <h3 className="font-heading text-2xl font-semibold tracking-tight">
                        Suggested Actions
                      </h3>
                    </div>
                    <ul className="space-y-3">
                      {analysis.potential_improvements.map((pt, idx) => {
                        const content = pt.replace(/^[\-\*\•]\s*/, "");
                        return (
                          <li
                            key={idx}
                            className="flex items-start gap-3 text-sm sm:text-[15px] text-foreground/80 leading-relaxed"
                          >
                            <span className="w-1.5 h-1.5 rounded-full bg-amber-500 shrink-0 mt-2" />
                            <div className="flex-1 min-w-0">
                              <Markdown variant="tight">{content}</Markdown>
                            </div>
                          </li>
                        );
                      })}
                    </ul>
                  </div>
                )}
            </div>
          </div>
        </div>
      ) : (
        /* The sleek step-by-step vertical timeline while processing */
        <div className="w-full max-w-xl mx-auto py-8 px-4">
          <div className="relative border-l border-border/80 pl-8 ml-4 space-y-8">
            {logs.map((log, i) => {
              const isProgress = log.type === "progress";
              const isError = log.type === "error";
              const isSuccess = log.type === "success";

              return (
                <div
                  key={i}
                  className="relative flex flex-col gap-1.5 animate-in fade-in slide-in-from-left-4 duration-300"
                >
                  {/* Timeline dot / icon */}
                  <div className="absolute -left-[17px] top-0 flex items-center justify-center w-8 h-8 rounded-full bg-background border border-border shadow-xs z-10 animate-in zoom-in duration-300">
                    {isProgress ? (
                      <div className="relative flex items-center justify-center w-5 h-5">
                        <span className="absolute inline-flex h-full w-full rounded-full bg-primary/20 animate-ping" />
                        <Loader2
                          size={14}
                          className="animate-spin text-primary relative"
                        />
                      </div>
                    ) : isError ? (
                      <AlertCircle size={16} className="text-destructive" />
                    ) : (
                      <CheckCircle2 size={16} className="text-emerald-500" />
                    )}
                  </div>

                  {/* Step content */}
                  <span
                    className={`text-sm sm:text-base font-semibold leading-none ${
                      isError
                        ? "text-destructive"
                        : isSuccess
                          ? "text-foreground"
                          : "text-foreground animate-pulse"
                    }`}
                  >
                    {log.text}
                  </span>

                  {isProgress && (
                    <span className="text-xs text-muted-foreground animate-pulse">
                      Analyzing content, please wait...
                    </span>
                  )}
                  {isSuccess && (
                    <span className="text-xs text-emerald-600 dark:text-emerald-500">
                      Step completed successfully.
                    </span>
                  )}
                </div>
              );
            })}
          </div>
        </div>
      )}

      <div ref={scrollRef} />
    </div>
  );
}
