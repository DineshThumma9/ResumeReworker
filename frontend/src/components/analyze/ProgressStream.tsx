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
  ThumbsUp,
  RefreshCw,
  RotateCcw,
  Gauge,
  Scale,
} from "lucide-react";

// ── Preprocess Markdown ────────────────────────────────────────────────────────
function preprocessMarkdown(text: string): string {
  if (!text) return "";
  return text
    .split("\n")
    .map((line) => {
      // If a line starts with 4 or more spaces and is not a code block fence, scale it to 2 spaces
      if (line.startsWith("    ") && !line.trim().startsWith("```")) {
        return "  " + line.substring(4);
      }
      return line;
    })
    .join("\n");
}

// ── Markdown ──────────────────────────────────────────────────────────────────
const Markdown = ({
  children,
  variant = "normal",
  allowBlocks = true,
}: {
  children: string;
  variant?: "normal" | "tight";
  allowBlocks?: boolean;
}) => (
  <ReactMarkdown
    remarkPlugins={[remarkGfm, remarkBreaks]}
    disallowedElements={
      allowBlocks
        ? []
        : ["ul", "ol", "li", "h1", "h2", "h3", "h4", "blockquote", "hr"]
    }
    unwrapDisallowed
    components={{
      p: ({ children }) => (
        <p
          className={`${variant === "tight" ? "mb-2.5 text-sm" : "mb-5 text-base"} leading-relaxed text-foreground/90 last:mb-0`}
        >
          {children}
        </p>
      ),
      h1: ({ children }) => (
        <h1 className="font-sans text-xl font-bold mt-7 mb-3.5 text-foreground tracking-tight">
          {children}
        </h1>
      ),
      h2: ({ children }) => (
        <h2 className="font-sans text-lg font-bold mt-6 mb-3 text-foreground">
          {children}
        </h2>
      ),
      h3: ({ children }) => (
        <h3 className="font-sans text-base font-semibold mt-5 mb-2.5 text-foreground/90">
          {children}
        </h3>
      ),
      h4: ({ children }) => (
        <h4 className="font-sans text-sm font-bold uppercase tracking-wider mt-4 mb-2 text-muted-foreground">
          {children}
        </h4>
      ),
      ul: ({ children }) => (
        <ul
          className={`list-disc pl-5 ${variant === "tight" ? "mb-3 space-y-1.5 text-sm [&_ul]:text-xs [&_ol]:text-xs" : "mb-5 space-y-2 text-base [&_ul]:text-sm [&_ol]:text-sm"} text-foreground/90 marker:text-muted-foreground/50 [&_ul]:list-[circle] [&_ul]:mt-1.5 [&_ul]:mb-0 [&_ul]:pl-5 [&_ul_ul]:list-[square] [&_ol]:mt-1.5 [&_ol]:mb-0 [&_ol]:pl-5`}
        >
          {children}
        </ul>
      ),
      ol: ({ children }) => (
        <ol
          className={`list-decimal pl-5 ${variant === "tight" ? "mb-3 space-y-1.5 text-sm [&_ul]:text-xs [&_ol]:text-xs" : "mb-5 space-y-2 text-base [&_ul]:text-sm [&_ol]:text-sm"} text-foreground/90 marker:text-muted-foreground/50 [&_ul]:list-[circle] [&_ul]:mt-1.5 [&_ul]:mb-0 [&_ul]:pl-5 [&_ol]:mt-1.5 [&_ol]:mb-0 [&_ol]:pl-5`}
        >
          {children}
        </ol>
      ),
      li: ({ children }) => <li className="leading-relaxed pl-0.5">{children}</li>,
      strong: ({ children }) => (
        <strong className="font-semibold text-foreground/95">{children}</strong>
      ),
      pre: ({ children }) => (
        <pre className="bg-muted border border-border/40 p-3 rounded-lg overflow-x-auto max-w-full my-3 font-mono text-xs whitespace-pre-wrap break-all leading-normal text-foreground/80">
          {children}
        </pre>
      ),
      code: ({ children }) => (
        <code className="bg-muted px-1.5 py-0.5 rounded-md font-mono text-xs text-foreground/90 whitespace-pre-wrap break-all">
          {children}
        </code>
      ),
    }}
  >
    {preprocessMarkdown(children)}
  </ReactMarkdown>
);

// ── Clean and split list helper ────────────────────────────────────────────────
function cleanAndSplitList(list: string[]): string[] {
  if (!list || list.length === 0) return [];
  if (list.length === 1) {
    const single = list[0];
    const parts = single.split(/\n+(?=[-•*]|\d+\.)/);
    if (parts.length > 1) {
      return parts.map((p) => p.trim()).filter(Boolean);
    }
  }
  return list;
}

// ── Judge event parser ────────────────────────────────────────────────────────
function parseJudgeEvents(logs: StreamLine[]) {
  return logs
    .filter((l) => {
      const txt = l.text?.toLowerCase() || "";
      return txt.includes("judge") || txt.includes("evaluating rewritten");
    })
    .map((l) => {
      const lower = l.text.toLowerCase();
      const approved =
        lower.includes("approved") ||
        lower.includes("proceeding to pdf") ||
        lower.includes("proceeding to latex") ||
        lower.includes("finalizing");
      const rejected =
        lower.includes("requested changes") ||
        lower.includes("rewriting again") ||
        lower.includes("rejected");
      
      const m = l.text.match(/iteration\s+(\d+)/i);
      const iteration = m ? parseInt(m[1]) : null;
      
      let message = "Evaluating...";
      if (approved) {
        message = "Approved rewrite. Proceeding to PDF generation.";
      } else if (rejected) {
        const fbMatch = l.text.match(/Feedback:\s*(.*)$/i);
        message = fbMatch ? `Changes requested: ${fbMatch[1]}` : "Changes requested. Rewriting again...";
      } else {
        message = "Evaluating rewritten resume...";
      }
      
      return { iteration, approved, rejected, message };
    });
}

// ── Log formatter ────────────────────────────────────────────────────────────
function formatLogLine(lineText: string) {
  const match = lineText.match(
    /^(\d{4}-\d{2}-\d{2}\s\d{2}:\d{2}:\d{2}(?:,\d{3})?)\s+-\s+([^-]+)\s+-\s+(INFO|ERROR|WARNING|DEBUG)\s+-\s+(.*)$/s,
  );

  let timestamp = "";
  let moduleName = "";
  let level = "";
  let content = lineText;

  if (match) {
    timestamp = match[1];
    moduleName = match[2].trim();
    level = match[3];
    content = match[4];
  }

  let textCls = "text-zinc-300 dark:text-zinc-300";
  let bgCls = "";
  let icon = "•";

  const lowerContent = content.toLowerCase();

  if (level === "ERROR" || lowerContent.includes("failed")) {
    textCls = "text-red-400 font-medium";
    icon = "✕";
  } else if (lowerContent.includes("judge approved") || lowerContent.includes("approved rewrite")) {
    textCls = "text-emerald-400 font-semibold";
    icon = "✓";
  } else if (lowerContent.includes("judge rejected") || lowerContent.includes("rejected rewrite")) {
    textCls = "text-amber-400 font-medium";
    icon = "⚠";
  } else if (lowerContent.includes("compiling latex")) {
    textCls = "text-sky-400 font-medium";
    icon = "⚙";
  } else if (content.startsWith("  -") || content.startsWith("    -")) {
    textCls = "text-zinc-400 pl-4 leading-normal";
    icon = "";
  } else if (lowerContent.includes("iteration")) {
    textCls = "text-primary/90 font-medium";
    icon = "✦";
  }

  return { timestamp, moduleName, level, content, textCls, bgCls, icon };
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
    // Dedupe consecutive identical lines (retries / re-emitted status lines
    // otherwise clutter the terminal and make it harder to scan).
    const steps = logs
      .filter((l) => l.type === "progress" || l.type === "success" || l.type === "error")
      .filter((l, idx, arr) => idx === 0 || l.text !== arr[idx - 1].text);

    return (
      <div className="w-full flex flex-col gap-6 mt-4 pb-24 px-2 animate-in fade-in duration-500 max-w-3xl mx-auto h-[75vh]">
        {/* Pulsating Icon & Title */}
        <div className="flex flex-col items-center justify-center gap-4 text-center mt-2">
          <div className="relative w-14 h-14 flex items-center justify-center">
            <div
              className="absolute inset-0 bg-primary/20 rounded-full animate-ping"
              style={{ animationDuration: "3s" }}
            />
            <div className="absolute inset-1.5 bg-primary/30 rounded-full animate-pulse" />
            <Sparkles size={24} className="text-primary relative z-10" />
          </div>
          <div className="space-y-1">
            <h3 className="font-sans text-xl font-bold text-foreground tracking-tight">
              AI Rework Pipeline
            </h3>
            <p className="text-xs text-muted-foreground max-w-sm">
              Analyzing candidate resume against JD and performing iterative self-correction loops.
            </p>
          </div>
        </div>

        {/* Indeterminate Progress Bar */}
        <div className="w-full max-w-xs mx-auto h-1 bg-muted rounded-full overflow-hidden relative">
          <div className="absolute inset-y-0 left-0 bg-primary w-1/3 rounded-full animate-[progress_2s_ease-in-out_infinite]" />
        </div>

        {/* Live-scrolling Terminal console */}
        <div className="w-full rounded-xl border border-border bg-card shadow-lg overflow-hidden flex flex-col flex-1 min-h-[300px]">
          <div className="flex items-center gap-2 px-4 py-2.5 bg-muted/40 border-b border-border/50 shrink-0">
            <div className="flex gap-1.5">
              <span className="w-2.5 h-2.5 rounded-full bg-red-500/80" />
              <span className="w-2.5 h-2.5 rounded-full bg-yellow-500/80" />
              <span className="w-2.5 h-2.5 rounded-full bg-green-500/80" />
            </div>
            <span className="font-mono text-[10px] text-muted-foreground/80 ml-3">
              pipeline_stream.sh
            </span>
            <div className="ml-auto flex items-center gap-1.5">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse" />
              <span className="font-mono text-[9px] text-emerald-600 dark:text-emerald-400 font-semibold uppercase tracking-wider">
                LIVE STREAM
              </span>
            </div>
          </div>

          <div className="flex-1 overflow-y-auto p-4 font-mono text-[11px] space-y-1.5 bg-[#09090b] dark:bg-[#0c0c0e] text-zinc-300">
            {steps.map((step, idx) => {
              const formatted = formatLogLine(step.text);
              return (
                <div
                  key={idx}
                  className={`flex items-start gap-2.5 leading-relaxed py-0.5 border-l-2 border-transparent hover:bg-zinc-900/40 px-1 rounded-xs transition-colors ${formatted.bgCls}`}
                >
                  {formatted.timestamp && (
                    <span className="text-zinc-600 dark:text-zinc-500 shrink-0 text-[10px] mt-[2px] select-none">
                      {formatted.timestamp.split(" ")[1].split(",")[0]}
                    </span>
                  )}
                  {formatted.level === "ERROR" && (
                    <span className="bg-red-500/10 text-red-500 border border-red-500/20 text-[8px] font-bold px-1 py-0.2 rounded-xs uppercase shrink-0 select-none">
                      ERR
                    </span>
                  )}
                  {formatted.icon && (
                    <span className={`shrink-0 select-none font-bold ${formatted.textCls}`}>
                      {formatted.icon}
                    </span>
                  )}
                  <span className={`flex-1 break-all whitespace-pre-wrap ${formatted.textCls}`}>
                    {formatted.content}
                  </span>
                </div>
              );
            })}
            <div ref={scrollRef} />
          </div>
        </div>

        <style
          dangerouslySetInnerHTML={{
            __html: `
          @keyframes progress {
            0% { transform: translateX(-100%); width: 20%; }
            50% { width: 40%; }
            100% { transform: translateX(300%); width: 20%; }
          }
        `,
          }}
        />
      </div>
    );
  }

  // Score helpers
  const score = analysis.score ?? 0;
  const isHigh = score >= 75;
  const isMid = score >= 50;
  const trackColor = isHigh
    ? "from-emerald-500 to-teal-400"
    : isMid
      ? "from-amber-500 to-yellow-400"
      : "from-red-500 to-rose-400";
  const fitLabel = isHigh ? "Excellent Fit" : isMid ? "Moderate Fit" : "Weak Fit";
  const fitCls = isHigh
    ? "text-emerald-600 dark:text-emerald-400 bg-emerald-500/10 border-emerald-500/20"
    : isMid
      ? "text-amber-600 dark:text-amber-400 bg-amber-500/10 border-amber-500/20"
      : "text-red-600 dark:text-red-400 bg-red-500/10 border-red-500/20";

  // ── Results view ─────────────────────────────────────────────────────────
  return (
    <div className="w-full flex flex-col gap-6 pb-28 px-2 animate-in fade-in duration-300">
      {/* ── Header ── */}
      <div className="flex items-center justify-between border-b border-border/40 pb-4 pt-2">
        <div className="flex items-center gap-3">
          <h3 className="font-heading text-2xl font-semibold text-foreground tracking-tight">
            Analysis Report
          </h3>
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

      {/* ROW 1 — ATS Score | AI Judge */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
        {analysis.score !== undefined && (
          <div className="rounded-2xl border border-border bg-card shadow-xs p-6 flex flex-col gap-5">
            <div className="flex items-center gap-2">
              <div className="p-1.5 bg-muted rounded-md">
                <Gauge size={13} className="text-muted-foreground" />
              </div>
              <span className="text-[10px] font-bold uppercase tracking-widest text-foreground/60">
                ATS Match Score
              </span>
              <span className={`ml-auto text-[11px] font-bold uppercase tracking-wider px-2.5 py-1 rounded-full border ${fitCls}`}>
                {fitLabel}
              </span>
            </div>

            <div className="flex items-baseline gap-2">
              <span className="font-heading text-6xl font-bold text-foreground tabular-nums leading-none">
                {score}
              </span>
              <span className="text-xl text-muted-foreground">/100</span>
            </div>

            <div className="relative h-2.5 w-full rounded-full bg-muted overflow-hidden">
              <div
                className={`absolute inset-y-0 left-0 rounded-full bg-gradient-to-r ${trackColor} transition-all duration-1000 ease-out`}
                style={{ width: `${score}%` }}
              />
            </div>
            <div className="flex justify-between text-[10px] text-muted-foreground/75 -mt-2.5">
              <span>0</span>
              <span>25</span>
              <span>50</span>
              <span>75</span>
              <span>100</span>
            </div>

            {analysis.urgency && (
              <p className="text-xs text-foreground/75 border-t border-border/40 pt-4 leading-relaxed">
                <strong className="font-semibold text-foreground/90">Urgency: </strong>
                {analysis.urgency}
              </p>
            )}
          </div>
        )}

        <div className="rounded-2xl border border-border bg-card shadow-xs overflow-hidden">
          <div className="flex items-center gap-2.5 px-6 py-4 border-b border-border/50">
            <div className="p-1.5 bg-muted rounded-md">
              <Scale size={13} className="text-muted-foreground" />
            </div>
            <h2 className="font-sans text-sm font-bold uppercase tracking-wider text-foreground">
              AI Judge
            </h2>
            <p className="ml-auto text-[10px] font-bold uppercase tracking-widest text-foreground/60">
              Refinement iterations
            </p>
          </div>

          {judgeEvents.length > 0 ? (
            <div className="p-6 flex flex-col gap-3">
              {judgeEvents.map((ev, i) => (
                <div
                  key={i}
                  className={`flex items-center gap-3 rounded-xl px-4 py-2.5 border text-sm font-medium ${
                    ev.approved
                      ? "bg-emerald-500/5 border-emerald-500/15 text-emerald-700 dark:text-emerald-400"
                      : ev.rejected
                        ? "bg-red-500/5 border-red-500/15 text-red-700 dark:text-red-400"
                        : "bg-muted border-border/50 text-muted-foreground"
                  }`}
                >
                  {ev.approved ? <ThumbsUp size={14} className="shrink-0" /> : <RefreshCw size={14} className="shrink-0" />}
                  <span>{ev.iteration !== null ? `Iteration ${ev.iteration}` : "Round"}</span>
                  <span
                    className={`ml-auto text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded-full ${
                      ev.approved
                        ? "bg-emerald-500/15 text-emerald-600 dark:text-emerald-400"
                        : ev.rejected
                          ? "bg-red-500/15 text-red-600 dark:text-red-400"
                          : "bg-muted-foreground/10 text-muted-foreground"
                    }`}
                  >
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

      {/* ROW 2 — Executive Summary */}
      {(analysis.resume_quality || analysis.match_explanation) && (
        <div className="rounded-2xl border border-border bg-card shadow-xs overflow-hidden animate-in slide-in-from-bottom-3 duration-500">
          <div className="flex items-center gap-2.5 px-6 py-4 border-b border-border/50">
            <div className="p-1.5 bg-primary/10 rounded-md text-primary">
              <FileText size={14} />
            </div>
            <h2 className="font-sans text-base font-bold text-foreground">Executive Summary</h2>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 divide-y md:divide-y-0 md:divide-x divide-border/40">
            {analysis.resume_quality && (
              <div className="p-6 min-w-0">
                <p className="text-[10px] font-bold uppercase tracking-widest text-foreground/60 mb-3.5">
                  Resume Quality &amp; Structure
                </p>
                <Markdown>{analysis.resume_quality}</Markdown>
              </div>
            )}
            {analysis.match_explanation && (
              <div className="p-6 min-w-0">
                <p className="text-[10px] font-bold uppercase tracking-widest text-foreground/60 mb-3.5">
                  JD Alignment Analysis
                </p>
                <Markdown>{analysis.match_explanation}</Markdown>
              </div>
            )}
          </div>
        </div>
      )}

      {/* ROW 3 — Critical Gaps | Missing Keywords */}
      {((analysis.negative_points?.length ?? 0) > 0 || (analysis.missing_keywords?.length ?? 0) > 0) && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-5 animate-in slide-in-from-bottom-3 duration-500 delay-75">
          {analysis.negative_points && analysis.negative_points.length > 0 && (
            <div className="rounded-2xl border border-red-500/15 bg-red-500/5 dark:bg-red-500/10 shadow-xs overflow-hidden">
              <div className="flex items-center gap-2.5 px-6 py-4 border-b border-red-500/10">
                <AlertTriangle size={14} className="text-red-500 shrink-0" />
                <h2 className="font-sans text-sm font-bold uppercase tracking-wider text-red-600 dark:text-red-400">
                  Critical Gaps
                </h2>
                <span className="ml-auto text-[11px] font-bold text-red-500 bg-red-500/15 px-2 py-0.5 rounded-full">
                  {analysis.negative_points.length}
                </span>
              </div>
              <ul className="p-6 space-y-4">
                {analysis.negative_points.map((pt, idx) => (
                  <li key={idx} className="flex items-start gap-3 text-sm text-foreground/90 leading-relaxed">
                    <span className="mt-[6px] w-1.5 h-1.5 rounded-full bg-red-500 shrink-0" />
                    <div className="flex-1">
                      <Markdown variant="tight" allowBlocks={false}>
                        {pt.replace(/^[-*•]\s*/, "")}
                      </Markdown>
                    </div>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {analysis.missing_keywords && analysis.missing_keywords.length > 0 && (
            <div className="rounded-2xl border border-border bg-card shadow-xs overflow-hidden">
              <div className="flex items-center gap-2.5 px-6 py-4 border-b border-border/50">
                <div className="p-1.5 bg-primary/10 rounded-md text-primary">
                  <Sparkles size={13} />
                </div>
                <h2 className="font-sans text-sm font-bold uppercase tracking-wider text-foreground">
                  Missing Keywords
                </h2>
                <span className="ml-auto text-[11px] font-bold text-primary bg-primary/10 px-2 py-0.5 rounded-full">
                  {analysis.missing_keywords.length}
                </span>
              </div>
              <div className="p-6">
                <p className="text-xs text-foreground/75 mb-3 leading-relaxed">
                  Integrate these naturally into your bullets to improve ATS ranking:
                </p>
                <div className="flex flex-wrap gap-1.5">
                  {analysis.missing_keywords.map((kw, idx) => (
                    <span
                      key={idx}
                      className="text-xs font-semibold bg-primary/5 text-primary border border-primary/20 dark:bg-primary/10 dark:text-emerald-400 dark:border-emerald-500/25 px-2.5 py-1 rounded-full hover:bg-primary/10 transition-colors cursor-default"
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

      {/* ROW 4 — Suggested Improvements */}
      {analysis.potential_improvements && analysis.potential_improvements.length > 0 && (
        <div className="rounded-2xl border border-amber-500/15 bg-amber-500/5 dark:bg-amber-500/10 shadow-xs overflow-hidden animate-in slide-in-from-bottom-3 duration-500 delay-150">
          <div className="flex items-center gap-2.5 px-6 py-4 border-b border-amber-500/10">
            <Lightbulb size={15} className="text-amber-500 shrink-0" />
            <h2 className="font-sans text-base font-bold text-amber-600 dark:text-amber-400">
              Suggested Improvements
            </h2>
          </div>
          <div className="p-6 min-w-0 max-w-none">
            <Markdown>
              {analysis.potential_improvements.join("\n\n")}
            </Markdown>
          </div>
        </div>
      )}

      <div ref={scrollRef} />
    </div>
  );
}