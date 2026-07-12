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
  XCircle,
  ThumbsUp,
  RefreshCw,
  RotateCcw,
  Gauge,
  Scale,
} from "lucide-react";

// ── Markdown ──────────────────────────────────────────────────────────────────
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
        <p className={`${variant === "tight" ? "mb-1 text-sm" : "mb-3 text-sm"} leading-relaxed text-foreground/80 last:mb-0`}>
          {children}
        </p>
      ),
      h1: ({ children }) => <h1 className="text-base font-bold mt-4 mb-2 text-foreground">{children}</h1>,
      h2: ({ children }) => <h2 className="text-sm font-semibold mt-3 mb-1.5 text-foreground">{children}</h2>,
      h3: ({ children }) => <h3 className="text-sm font-semibold mt-2 mb-1 text-foreground">{children}</h3>,
      ul: ({ children }) => <ul className="list-disc pl-4 mb-2 space-y-0.5 text-sm text-foreground/80">{children}</ul>,
      ol: ({ children }) => <ol className="list-decimal pl-4 mb-2 space-y-0.5 text-sm text-foreground/80">{children}</ol>,
      li: ({ children }) => <li className="leading-relaxed">{children}</li>,
      strong: ({ children }) => <span className="font-semibold text-foreground/95">{children}</span>,
    }}
  >
    {children}
  </ReactMarkdown>
);

// ── Judge event parser ────────────────────────────────────────────────────────
function parseJudgeEvents(logs: StreamLine[]) {
  return logs
    .filter((l) => l.text?.toLowerCase().includes("judge"))
    .map((l) => {
      const approved =
        l.text.toLowerCase().includes("approved") ||
        l.text.toLowerCase().includes("proceeding to pdf") ||
        l.text.toLowerCase().includes("proceeding to latex");
      const rejected =
        l.text.toLowerCase().includes("requested changes") ||
        l.text.toLowerCase().includes("rewriting again");
      const m = l.text.match(/iteration\s+(\d+)/i);
      return { iteration: m ? parseInt(m[1]) : null, approved, rejected };
    });
}

interface ProgressStreamProps {
  logs: StreamLine[];
  running: boolean;
  onReset?: () => void;
}

export function ProgressStream({ logs, running, onReset }: ProgressStreamProps) {
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    scrollRef.current?.scrollIntoView({ behavior: "smooth", block: "end" });
  }, [logs]);

  if (logs.length === 0 && !running) return null;

  const analysisLog = [...logs].reverse().find((l) => l.analysis !== undefined);
  const analysis = analysisLog?.analysis;
  const judgeEvents = parseJudgeEvents(logs);
  const isComplete = logs.some((l) => l.type === "success");
  const isError = logs.some((l) => l.type === "error");

  // ── Processing view ──────────────────────────────────────────────────────
  if (!analysis) {
    const steps = logs.filter(
      (l) => l.type === "progress" || l.type === "success" || l.type === "error",
    );
    return (
      <div className="w-full max-w-lg mx-auto flex flex-col gap-4 mt-10 pb-24 px-4 animate-in fade-in duration-300">
        <h3 className="font-heading text-2xl font-semibold text-foreground flex items-center gap-2">
          AI is working
          {running && <Loader2 size={16} className="animate-spin text-primary" />}
        </h3>
        <div className="relative border-l-2 border-border/50 pl-7 ml-3 space-y-5">
          {steps.map((step, i) => (
            <div key={i} className="relative flex items-start gap-2 animate-in fade-in duration-300">
              <div className="absolute -left-[13px] top-0.5 w-6 h-6 rounded-full bg-background border border-border flex items-center justify-center z-10">
                {step.type === "progress" ? (
                  <Loader2 size={11} className="animate-spin text-primary" />
                ) : step.type === "error" ? (
                  <XCircle size={12} className="text-destructive" />
                ) : (
                  <CheckCircle2 size={12} className="text-emerald-500" />
                )}
              </div>
              <span className={`text-sm ${step.type === "error" ? "text-destructive" : step.type === "success" ? "text-foreground/70" : "text-foreground/50 animate-pulse"}`}>
                {step.text}
              </span>
            </div>
          ))}
        </div>
        <div ref={scrollRef} />
      </div>
    );
  }

  // Score helpers
  const score = analysis.score ?? 0;
  const isHigh = score >= 75;
  const isMid = score >= 50;
  const trackColor = isHigh ? "from-emerald-500 to-teal-400" : isMid ? "from-amber-500 to-yellow-400" : "from-red-500 to-rose-400";
  const fitLabel = isHigh ? "Excellent Fit" : isMid ? "Moderate Fit" : "Weak Fit";
  const fitCls = isHigh
    ? "text-emerald-600 dark:text-emerald-400 bg-emerald-500/10 border-emerald-500/20"
    : isMid
      ? "text-amber-600 dark:text-amber-400 bg-amber-500/10 border-amber-500/20"
      : "text-red-600 dark:text-red-400 bg-red-500/10 border-red-500/20";

  // ── Results view ─────────────────────────────────────────────────────────
  return (
    <div className="w-full flex flex-col gap-5 pb-28 px-2 animate-in fade-in duration-300">

      {/* ── Header ── */}
      <div className="flex items-center justify-between border-b border-border/40 pb-4 pt-2">
        <div className="flex items-center gap-3">
          <h3 className="font-heading text-2xl font-semibold text-foreground tracking-tight">Analysis Report</h3>
          {running ? (
            <span className="flex items-center gap-1.5 text-xs text-primary font-medium px-2.5 py-1 bg-primary/10 rounded-full animate-pulse">
              <Loader2 size={11} className="animate-spin" /> Analyzing
            </span>
          ) : isError ? (
            <span className="flex items-center gap-1.5 text-xs text-destructive font-medium px-2.5 py-1 bg-destructive/10 rounded-full">
              <AlertCircle size={11} /> Failed
            </span>
          ) : isComplete ? (
            <span className="flex items-center gap-1.5 text-xs text-emerald-600 dark:text-emerald-400 font-medium px-2.5 py-1 bg-emerald-500/10 rounded-full">
              <CheckCircle2 size={11} /> Complete
            </span>
          ) : null}
        </div>
        {!running && onReset && (
          <button
            onClick={onReset}
            className="flex items-center gap-1.5 text-xs font-semibold text-foreground/60 border border-border/60 rounded-lg px-3 py-1.5 hover:bg-muted transition-colors cursor-pointer"
          >
            <RotateCcw size={12} /> Start Over
          </button>
        )}
      </div>

      {/* ══════════════════════════════════════════════════════════════════════
          ROW 1 — ATS Score  |  AI Judge  (2 compact side-by-side cards)
      ══════════════════════════════════════════════════════════════════════ */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-5">

        {/* ATS Score */}
        {analysis.score !== undefined && (
          <div className="rounded-2xl border border-border bg-card shadow-xs p-5 flex flex-col gap-4">
            <div className="flex items-center gap-2">
              <div className="p-1.5 bg-muted rounded-md">
                <Gauge size={13} className="text-muted-foreground" />
              </div>
              <span className="text-xs font-bold uppercase tracking-widest text-muted-foreground">ATS Match Score</span>
              <span className={`ml-auto text-[11px] font-bold uppercase tracking-wider px-2.5 py-1 rounded-full border ${fitCls}`}>
                {fitLabel}
              </span>
            </div>

            <div className="flex items-baseline gap-2">
              <span className="font-heading text-6xl font-bold text-foreground tabular-nums leading-none">{score}</span>
              <span className="text-xl text-muted-foreground">/100</span>
            </div>

            {/* Bar */}
            <div className="relative h-2.5 w-full rounded-full bg-muted overflow-hidden">
              <div
                className={`absolute inset-y-0 left-0 rounded-full bg-gradient-to-r ${trackColor} transition-all duration-1000 ease-out`}
                style={{ width: `${score}%` }}
              />
            </div>
            <div className="flex justify-between text-[10px] text-muted-foreground/50 -mt-2">
              <span>0</span><span>25</span><span>50</span><span>75</span><span>100</span>
            </div>

            {analysis.urgency && (
              <p className="text-xs text-muted-foreground border-t border-border/40 pt-3 leading-relaxed">
                <span className="font-semibold text-foreground/70">Urgency: </span>{analysis.urgency}
              </p>
            )}
          </div>
        )}

        {/* AI Judge */}
        <div className="rounded-2xl border border-border bg-card shadow-xs overflow-hidden">
          <div className="flex items-center gap-2.5 px-5 py-3.5 border-b border-border/50">
            <div className="p-1.5 bg-muted rounded-md">
              <Scale size={13} className="text-muted-foreground" />
            </div>
            <h2 className="font-heading text-base font-semibold text-foreground">AI Judge</h2>
            <p className="ml-auto text-xs text-muted-foreground">Refinement iterations</p>
          </div>

          {judgeEvents.length > 0 ? (
            <div className="p-4 flex flex-col gap-2">
              {judgeEvents.map((ev, i) => (
                <div
                  key={i}
                  className={`flex items-center gap-3 rounded-xl px-4 py-2.5 border text-sm font-medium ${ev.approved
                      ? "bg-emerald-500/5 border-emerald-500/15 text-emerald-700 dark:text-emerald-400"
                      : ev.rejected
                        ? "bg-red-500/5 border-red-500/15 text-red-700 dark:text-red-400"
                        : "bg-muted border-border/50 text-muted-foreground"
                    }`}
                >
                  {ev.approved
                    ? <ThumbsUp size={14} className="shrink-0" />
                    : <RefreshCw size={14} className="shrink-0" />
                  }
                  <span>{ev.iteration !== null ? `Iteration ${ev.iteration}` : "Round"}</span>
                  <span className={`ml-auto text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded-full ${ev.approved
                      ? "bg-emerald-500/15 text-emerald-600 dark:text-emerald-400"
                      : ev.rejected
                        ? "bg-red-500/15 text-red-600 dark:text-red-400"
                        : "bg-muted-foreground/10 text-muted-foreground"
                    }`}>
                    {ev.approved ? "Approved ✓" : ev.rejected ? "Revised ↺" : "Pending"}
                  </span>
                </div>
              ))}
            </div>
          ) : (
            <div className="p-5 flex flex-col items-center justify-center gap-2 text-center min-h-[100px]">
              {running ? (
                <>
                  <Loader2 size={18} className="animate-spin text-muted-foreground/50" />
                  <p className="text-xs text-muted-foreground">Judge evaluation in progress…</p>
                </>
              ) : (
                <p className="text-xs text-muted-foreground">No judge iterations recorded.</p>
              )}
            </div>
          )}
        </div>
      </div>

      {/* ══════════════════════════════════════════════════════════════════════
          ROW 2 — Executive Summary  (full width)
      ══════════════════════════════════════════════════════════════════════ */}
      {(analysis.resume_quality || analysis.match_explanation) && (
        <div className="rounded-2xl border border-border bg-card shadow-xs overflow-hidden animate-in slide-in-from-bottom-3 duration-500">
          <div className="flex items-center gap-2.5 px-6 py-4 border-b border-border/50">
            <div className="p-1.5 bg-primary/10 rounded-md text-primary">
              <FileText size={14} />
            </div>
            <h2 className="font-heading text-lg font-semibold text-foreground">Executive Summary</h2>
          </div>

          {/* Two-column inside for quality + alignment — each taking half */}
          <div className="grid grid-cols-1 md:grid-cols-2 divide-y md:divide-y-0 md:divide-x divide-border/40">
            {analysis.resume_quality && (
              <div className="p-6">
                <p className="text-[11px] font-bold uppercase tracking-widest text-muted-foreground mb-3">
                  Resume Quality &amp; Structure
                </p>
                <Markdown>{analysis.resume_quality}</Markdown>
              </div>
            )}
            {analysis.match_explanation && (
              <div className="p-6">
                <p className="text-[11px] font-bold uppercase tracking-widest text-muted-foreground mb-3">
                  JD Alignment Analysis
                </p>
                <Markdown>{analysis.match_explanation}</Markdown>
              </div>
            )}
          </div>
        </div>
      )}

      {/* ══════════════════════════════════════════════════════════════════════
          ROW 3 — Critical Gaps  |  Missing Keywords  (2 compact columns)
      ══════════════════════════════════════════════════════════════════════ */}
      {((analysis.negative_points?.length ?? 0) > 0 ||
        (analysis.missing_keywords?.length ?? 0) > 0) && (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-5 animate-in slide-in-from-bottom-3 duration-500 delay-75">

            {/* Critical Gaps */}
            {analysis.negative_points && analysis.negative_points.length > 0 && (
              <div className="rounded-2xl border border-red-500/15 bg-red-500/5 dark:bg-red-500/10 shadow-xs overflow-hidden">
                <div className="flex items-center gap-2.5 px-5 py-3.5 border-b border-red-500/10">
                  <AlertTriangle size={14} className="text-red-500 shrink-0" />
                  <h2 className="font-heading text-base font-semibold text-red-600 dark:text-red-400">Critical Gaps</h2>
                  <span className="ml-auto text-[11px] font-bold text-red-500 bg-red-500/15 px-2 py-0.5 rounded-full">
                    {analysis.negative_points.length}
                  </span>
                </div>
                <ul className="p-5 space-y-3">
                  {analysis.negative_points.map((pt, idx) => (
                    <li key={idx} className="flex items-start gap-3 text-sm text-foreground/80 leading-relaxed">
                      <span className="mt-[6px] w-1.5 h-1.5 rounded-full bg-red-500 shrink-0" />
                      <div className="flex-1">
                        <Markdown variant="tight">{pt.replace(/^[-*•]\s*/, "")}</Markdown>
                      </div>
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {/* Missing Keywords */}
            {analysis.missing_keywords && analysis.missing_keywords.length > 0 && (
              <div className="rounded-2xl border border-border bg-card shadow-xs overflow-hidden">
                <div className="flex items-center gap-2.5 px-5 py-3.5 border-b border-border/50">
                  <div className="p-1.5 bg-primary/10 rounded-md text-primary">
                    <Sparkles size={13} />
                  </div>
                  <h2 className="font-heading text-base font-semibold text-foreground">Missing Keywords</h2>
                  <span className="ml-auto text-[11px] font-bold text-primary bg-primary/10 px-2 py-0.5 rounded-full">
                    {analysis.missing_keywords.length}
                  </span>
                </div>
                <div className="p-5">
                  <p className="text-xs text-muted-foreground mb-3 leading-relaxed">
                    Integrate these naturally into your bullets to improve ATS ranking:
                  </p>
                  <div className="flex flex-wrap gap-1.5">
                    {analysis.missing_keywords.map((kw, idx) => (
                      <span
                        key={idx}
                        className="text-xs font-semibold bg-primary/5 text-primary border border-primary/20 px-2.5 py-1 rounded-full hover:bg-primary/10 transition-colors cursor-default"
                      >
                        {kw}
                      </span>
                    ))}
                  </div>
                </div>
              </div>
            )}
          </div>
        )}

      {/* ══════════════════════════════════════════════════════════════════════
          ROW 4 — Suggested Improvements  (full width)
      ══════════════════════════════════════════════════════════════════════ */}
      {analysis.potential_improvements && analysis.potential_improvements.length > 0 && (
        <div className="rounded-2xl border border-amber-500/15 bg-amber-500/5 dark:bg-amber-500/10 shadow-xs overflow-hidden animate-in slide-in-from-bottom-3 duration-500 delay-150">
          <div className="flex items-center gap-2.5 px-6 py-4 border-b border-amber-500/10">
            <Lightbulb size={15} className="text-amber-500 shrink-0" />
            <h2 className="font-heading text-lg font-semibold text-amber-600 dark:text-amber-400">
              Suggested Improvements
            </h2>
            <span className="ml-auto text-[11px] font-bold text-amber-500 bg-amber-500/15 px-2 py-0.5 rounded-full">
              {analysis.potential_improvements.length}
            </span>
          </div>
          {/* Use CSS columns to prevent weird vertical gaps between items of different heights */}
          <ul className="p-6 columns-1 md:columns-2 gap-x-10 space-y-4">
            {analysis.potential_improvements.map((pt, idx) => (
              <li key={idx} className="flex items-start gap-3 text-sm text-foreground/80 leading-relaxed break-inside-avoid">
                <span className="mt-[6px] w-1.5 h-1.5 rounded-full bg-amber-500 shrink-0" />
                <div className="flex-1">
                  <Markdown variant="tight">{pt.replace(/^[-*•]\s*/, "")}</Markdown>
                </div>
              </li>
            ))}
          </ul>
        </div>
      )}

      <div ref={scrollRef} />
    </div>
  );
}
