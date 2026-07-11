import { useRef, useEffect } from "react";
import ReactMarkdown from "react-markdown";
import { type StreamLine } from "../../hooks/useResumeAnalysis";
import {
  Loader2,
  CheckCircle2,
  AlertCircle,
  Sparkles,
  ChevronRight,
  Ban,
  PlusCircle,
  Bookmark,
  Compass,
} from "lucide-react";

// Markdown parser component for long text paragraphs
function MarkdownText({
  text,
  className = "",
}: {
  text: string;
  className?: string;
}) {
  if (!text) return null;
  return (
    <div
      className={`space-y-4 text-[16px] leading-relaxed text-foreground ${className}`}
    >
      <ReactMarkdown
        components={{
          p: ({ children }) => (
            <p className="text-[16px] leading-relaxed text-foreground">
              {children}
            </p>
          ),
          h3: ({ children }) => (
            <h3 className="text-[19px] font-bold text-foreground mt-6 mb-3">
              {children}
            </h3>
          ),
          h4: ({ children }) => (
            <h4 className="text-[17px] font-bold text-foreground mt-5 mb-2">
              {children}
            </h4>
          ),
          ul: ({ children }) => (
            <ul className="space-y-2 list-none pl-3">{children}</ul>
          ),
          li: ({ children }) => (
            <li className="flex gap-2.5 text-[16px] leading-relaxed text-foreground">
              <span className="text-primary font-bold mt-0.5 select-none">
                •
              </span>
              <span className="flex-1">{children}</span>
            </li>
          ),
          strong: ({ children }) => (
            <strong className="font-semibold text-foreground">
              {children}
            </strong>
          ),
        }}
      >
        {text}
      </ReactMarkdown>
    </div>
  );
}

// Markdown parser component for list elements
function MarkdownItem({
  text,
  markerClass = "text-primary",
}: {
  text: string;
  markerClass?: string;
}) {
  if (!text) return null;
  const trimmed = text.trim();
  const isBullet =
    trimmed.startsWith("- ") ||
    trimmed.startsWith("* ") ||
    trimmed.startsWith("• ");
  const content = isBullet ? trimmed.slice(2).trim() : trimmed;

  if (!isBullet) {
    return (
      <div className="text-[16px] text-foreground leading-relaxed mt-4 first:mt-0 font-medium">
        <ReactMarkdown
          components={{
            p: ({ children }) => <>{children}</>,
            strong: ({ children }) => (
              <strong className="font-semibold text-foreground">
                {children}
              </strong>
            ),
          }}
        >
          {content}
        </ReactMarkdown>
      </div>
    );
  }

  return (
    <div className="flex gap-2.5 text-[16px] text-foreground leading-relaxed pl-3 mt-2">
      <span className={`${markerClass} mt-1 font-bold select-none`}>•</span>
      <span className="flex-1">
        <ReactMarkdown
          components={{
            p: ({ children }) => <>{children}</>,
            strong: ({ children }) => (
              <strong className="font-semibold text-foreground">
                {children}
              </strong>
            ),
          }}
        >
          {content}
        </ReactMarkdown>
      </span>
    </div>
  );
}

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

  // Find the latest log item that contains the accumulated analysis data
  const analysisLog = [...logs].reverse().find((l) => l.analysis !== undefined);
  const analysis = analysisLog?.analysis;

  return (
    <div className="w-full max-w-4xl mx-auto flex flex-col gap-8 animate-in fade-in duration-300 mt-6 pb-16 px-4">
      {/* Top Header */}
      <div className="flex items-center justify-between border-b border-border/60 pb-5 w-full">
        <div className="flex items-center gap-3">
          <h3 className="font-['EB_Garamond'] text-3xl font-semibold text-foreground tracking-tight">
            Workflow Progress
          </h3>
          {running ? (
            <span className="flex items-center gap-2 text-xs text-primary font-medium px-3 py-1 bg-primary/10 rounded-full animate-pulse">
              <Loader2 size={13} className="animate-spin" />
              Processing
            </span>
          ) : logs.some((l) => l.type === "error") ? (
            <span className="flex items-center gap-2 text-xs text-destructive font-medium px-3 py-1 bg-destructive/10 rounded-full">
              <AlertCircle size={13} />
              Failed
            </span>
          ) : logs.some((l) => l.type === "success") ? (
            <span className="flex items-center gap-2 text-xs text-green-600 dark:text-green-500 font-medium px-3 py-1 bg-green-500/10 rounded-full">
              <CheckCircle2 size={13} />
              Complete
            </span>
          ) : null}
        </div>

        {!running && onReset && (
          <button
            onClick={onReset}
            className="flex items-center gap-2 bg-transparent text-foreground border border-border rounded-lg px-5 py-2 text-xs font-semibold tracking-wider uppercase hover:bg-muted/40 transition-all cursor-pointer shadow-sm"
          >
            Back to Setup
          </button>
        )}
      </div>

      {/* Main Spacious Timeline Flow */}
      <div className="flex flex-col gap-8">
        {logs.map((log, i) => {
          const isProgress = log.type === "progress";
          const isError = log.type === "error";
          const isSuccess = log.type === "success";

          return (
            <div
              key={i}
              className="flex flex-col gap-4 animate-in fade-in duration-200"
            >
              {/* Event Step Row */}
              <div className="flex items-start gap-4">
                <div className="mt-1">
                  {isProgress ? (
                    <div className="w-5 h-5 flex items-center justify-center rounded-full bg-primary/10 text-primary">
                      <Loader2 size={13} className="animate-spin" />
                    </div>
                  ) : isError ? (
                    <div className="w-5 h-5 flex items-center justify-center rounded-full bg-destructive/10 text-destructive">
                      <AlertCircle size={13} />
                    </div>
                  ) : (
                    <div className="w-5 h-5 flex items-center justify-center rounded-full bg-green-500/10 text-green-500">
                      <CheckCircle2 size={13} />
                    </div>
                  )}
                </div>

                <div className="flex flex-col gap-1.5">
                  <span
                    className={`text-[17px] font-semibold leading-normal ${isError ? "text-destructive" : isSuccess ? "text-green-600 dark:text-green-400" : "text-foreground"}`}
                  >
                    {log.text}
                  </span>
                </div>
              </div>

              {/* Streamed analysis details displayed directly in-line below the "JD Analysis" step */}
              {log.text.includes("JD analysis") && analysis && (
                <div className="ml-9 pl-6 border-l-2 border-border/60 flex flex-col gap-8 py-4 my-3 max-w-5xl animate-in slide-in-from-top-4 duration-300">
                  {/* Score & Match */}
                  {analysis.score !== undefined && (
                    <div className="flex flex-wrap items-center gap-6 bg-card/60 border border-border/80 p-6 rounded-2xl shadow-xs">
                      <div className="flex items-center gap-3">
                        <Sparkles
                          className="text-amber-500 animate-pulse"
                          size={24}
                        />
                        <span className="font-['EB_Garamond'] text-4xl font-bold text-foreground">
                          {analysis.score}%
                        </span>
                        <span className="text-xs text-muted-foreground font-semibold uppercase tracking-wider">
                          Match score
                        </span>
                      </div>
                      <div className="h-8 w-[1px] bg-border" />
                      <div className="flex items-center gap-2 text-xs">
                        <span className="text-muted-foreground uppercase tracking-wider font-bold">
                          Fit status:
                        </span>
                        <span
                          className={`px-3 py-1 rounded-full font-bold uppercase tracking-wider text-[10px] ${
                            analysis.score !== undefined && analysis.score >= 75
                              ? "bg-green-500/10 text-green-600 dark:text-green-400"
                              : analysis.score !== undefined &&
                                  analysis.score >= 50
                                ? "bg-amber-500/10 text-amber-600 dark:text-amber-400"
                                : "bg-destructive/10 text-destructive"
                          }`}
                        >
                          {analysis.score !== undefined && analysis.score >= 75
                            ? "Strong match"
                            : analysis.score !== undefined &&
                                analysis.score >= 50
                              ? "Moderate match"
                              : "Weak / Misaligned"}
                        </span>
                      </div>
                      {analysis.urgency && (
                        <>
                          <div className="h-8 w-[1px] bg-border" />
                          <div className="flex items-center gap-1.5 text-xs text-muted-foreground font-semibold">
                            <Compass size={14} className="text-primary" />
                            <span>Deadline: {analysis.urgency}</span>
                          </div>
                        </>
                      )}
                    </div>
                  )}

                  {/* Quality summary */}
                  {analysis.resume_quality && (
                    <div className="flex flex-col gap-3">
                      <div className="flex items-center gap-2.5 text-[13px] font-bold uppercase tracking-widest text-foreground/80">
                        <Bookmark size={14} className="text-primary" />
                        <span>Resume quality</span>
                      </div>
                      <div className="pl-1">
                        <MarkdownText text={analysis.resume_quality} />
                      </div>
                    </div>
                  )}

                  {/* Detailed explanation */}
                  {analysis.match_explanation && (
                    <div className="flex flex-col gap-3">
                      <div className="flex items-center gap-2.5 text-[13px] font-bold uppercase tracking-widest text-foreground/80">
                        <ChevronRight size={14} className="text-primary" />
                        <span>Analysis breakdown</span>
                      </div>
                      <div className="pl-1">
                        <MarkdownText text={analysis.match_explanation} />
                      </div>
                    </div>
                  )}

                  {/* Missing Keywords */}
                  {analysis.missing_keywords &&
                    analysis.missing_keywords.length > 0 && (
                      <div className="flex flex-col gap-3">
                        <div className="flex items-center gap-2.5 text-[13px] font-bold uppercase tracking-widest text-foreground/80">
                          <PlusCircle size={14} className="text-primary" />
                          <span>Recommended keywords to add</span>
                        </div>
                        <div className="flex flex-wrap gap-2 pl-1">
                          {analysis.missing_keywords.map((kw, idx) => (
                            <span
                              key={idx}
                              className="text-xs font-semibold bg-secondary text-secondary-foreground border border-border px-3 py-1.5 rounded-lg shadow-2xs hover:bg-muted transition-colors"
                            >
                              {kw}
                            </span>
                          ))}
                        </div>
                      </div>
                    )}

                  {/* Red flags */}
                  {analysis.negative_points &&
                    analysis.negative_points.length > 0 && (
                      <div className="flex flex-col gap-3">
                        <div className="flex items-center gap-2.5 text-[13px] font-bold uppercase tracking-widest text-foreground/80">
                          <Ban size={14} className="text-destructive" />
                          <span>Identified Gaps & Flags</span>
                        </div>
                        <div className="flex flex-col gap-2 pl-1">
                          {analysis.negative_points.map((pt, idx) => (
                            <MarkdownItem
                              key={idx}
                              text={pt}
                              markerClass="text-destructive"
                            />
                          ))}
                        </div>
                      </div>
                    )}

                  {/* Suggested improvements */}
                  {analysis.potential_improvements &&
                    analysis.potential_improvements.length > 0 && (
                      <div className="flex flex-col gap-3">
                        <div className="flex items-center gap-2.5 text-[13px] font-bold uppercase tracking-widest text-foreground/80">
                          <Sparkles size={14} className="text-amber-500" />
                          <span>Suggested actions</span>
                        </div>
                        <div className="flex flex-col gap-2 pl-1">
                          {analysis.potential_improvements.map((imp, idx) => (
                            <MarkdownItem
                              key={idx}
                              text={imp}
                              markerClass="text-amber-500"
                            />
                          ))}
                        </div>
                      </div>
                    )}
                </div>
              )}
            </div>
          );
        })}

        {running &&
          logs.length > 0 &&
          !logs[logs.length - 1].text.includes("JD analysis") && (
            <div className="flex items-zinc-500 animate-pulse text-xs italic gap-3 ml-9 pl-4">
              <span>Awaiting next backend workflow step</span>
              <div className="flex gap-1">
                <div className="w-1.5 h-1.5 bg-primary rounded-full animate-bounce" />
                <div className="w-1.5 h-1.5 bg-primary rounded-full animate-bounce [animation-delay:0.2s]" />
                <div className="w-1.5 h-1.5 bg-primary rounded-full animate-bounce [animation-delay:0.4s]" />
              </div>
            </div>
          )}
      </div>

      {/* Anchor for auto-scroll */}
      <div ref={scrollRef} />
    </div>
  );
}
