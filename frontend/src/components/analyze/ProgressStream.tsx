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
  ArrowRight
} from "lucide-react";

// Beautiful, standard, cohesive typography for markdown rendering
const Markdown = ({ children }: { children: string }) => (
  <ReactMarkdown
    remarkPlugins={[remarkGfm, remarkBreaks]}
    components={{
      p: ({ children }) => (
        <p className="mb-4 text-[15px] sm:text-base leading-[1.7] text-slate-700 dark:text-slate-300 last:mb-0">
          {children}
        </p>
      ),
      h1: ({ children }) => (
        <h1 className="text-2xl font-bold mt-8 mb-4 text-slate-900 dark:text-slate-50 tracking-tight">
          {children}
        </h1>
      ),
      h2: ({ children }) => (
        <h2 className="text-xl font-semibold mt-8 mb-4 text-slate-900 dark:text-slate-50 tracking-tight">
          {children}
        </h2>
      ),
      h3: ({ children }) => (
        <h3 className="text-lg font-semibold mt-6 mb-3 text-slate-900 dark:text-slate-50 tracking-tight">
          {children}
        </h3>
      ),
      h4: ({ children }) => (
        <h4 className="text-base font-semibold mt-4 mb-2 text-slate-900 dark:text-slate-50">
          {children}
        </h4>
      ),
      ul: ({ children }) => (
        <ul className="list-disc pl-5 mb-5 space-y-2 text-[15px] sm:text-base text-slate-700 dark:text-slate-300">
          {children}
        </ul>
      ),
      ol: ({ children }) => (
        <ol className="list-decimal pl-5 mb-5 space-y-2 text-[15px] sm:text-base text-slate-700 dark:text-slate-300">
          {children}
        </ol>
      ),
      li: ({ children }) => (
        <li className="leading-[1.7] pl-1">{children}</li>
      ),
      strong: ({ children }) => (
        <strong className="font-semibold text-slate-900 dark:text-slate-100">
          {children}
        </strong>
      ),
      blockquote: ({ children }) => (
        <blockquote className="border-l-4 border-slate-300 dark:border-slate-700 pl-4 py-1 italic my-5 text-slate-600 dark:text-slate-400">
          {children}
        </blockquote>
      ),
      code: ({ children }) => (
        <code className="bg-slate-100 dark:bg-slate-800/80 px-1.5 py-0.5 rounded text-[0.9em] font-mono text-slate-800 dark:text-slate-200">
          {children}
        </code>
      ),
    }}
  >
    {children}
  </ReactMarkdown>
);

// Cohesive Section Wrapper
const Section = ({ title, icon, children }: { title: string, icon: React.ReactNode, children: React.ReactNode }) => (
  <div className="mt-10 mb-6">
    <div className="flex items-center gap-3 mb-5">
      <div className="p-2 bg-slate-100 dark:bg-slate-800 rounded-lg text-slate-600 dark:text-slate-300">
        {icon}
      </div>
      <h2 className="text-xl sm:text-2xl font-bold text-slate-900 dark:text-white tracking-tight">
        {title}
      </h2>
    </div>
    <div className="ml-1 sm:ml-2">
      {children}
    </div>
  </div>
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
    <div className="w-full max-w-3xl mx-auto flex flex-col gap-8 animate-in fade-in duration-300 mt-6 pb-24 px-4 sm:px-6">
      
      {/* Top Header */}
      <div className="flex items-center justify-between border-b border-border/40 pb-5 w-full">
        <div className="flex items-center gap-3">
          <h3 className="font-['EB_Garamond'] text-2xl sm:text-3xl font-semibold text-foreground tracking-tight">
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
            className="flex items-center gap-2 bg-transparent text-foreground border border-border/60 rounded-lg px-4 py-2 text-xs font-semibold tracking-wider hover:bg-slate-50 dark:hover:bg-slate-800 transition-colors cursor-pointer"
          >
            Start Over
          </button>
        )}
      </div>

      {/* Main Analysis Body */}
      {analysis ? (
        <div className="flex flex-col animate-in slide-in-from-bottom-4 duration-500">
          
          {/* Score Hero Card */}
          {analysis.score !== undefined && (
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-6 p-6 sm:p-8 bg-slate-50 dark:bg-slate-800/40 rounded-2xl border border-slate-200 dark:border-slate-800 mb-4">
              <div className="flex flex-col gap-1">
                <span className="text-xs font-bold text-slate-500 dark:text-slate-400 uppercase tracking-widest">
                  ATS Match Score
                </span>
                <div className="flex items-baseline gap-2">
                  <span className="font-['EB_Garamond'] text-5xl sm:text-6xl font-bold text-slate-900 dark:text-white">
                    {analysis.score}
                  </span>
                  <span className="text-xl text-slate-400">/ 100</span>
                </div>
              </div>
              
              <div className="flex flex-col gap-3">
                <span
                  className={`inline-flex items-center justify-center px-4 py-2 rounded-full font-bold uppercase tracking-wider text-xs w-fit ${
                    analysis.score >= 75
                      ? "bg-emerald-100 text-emerald-700 dark:bg-emerald-500/20 dark:text-emerald-400"
                      : analysis.score >= 50
                        ? "bg-amber-100 text-amber-700 dark:bg-amber-500/20 dark:text-amber-400"
                        : "bg-red-100 text-red-700 dark:bg-red-500/20 dark:text-red-400"
                  }`}
                >
                  {analysis.score >= 75
                    ? "Excellent Fit"
                    : analysis.score >= 50
                      ? "Moderate Fit"
                      : "Weak Fit"}
                </span>
                {analysis.urgency && (
                  <span className="text-sm font-medium text-slate-500 dark:text-slate-400 flex items-center gap-1.5">
                    <Target size={14} />
                    {analysis.urgency}
                  </span>
                )}
              </div>
            </div>
          )}

          {/* Core Sections */}
          {analysis.resume_quality && (
            <Section title="Resume Quality" icon={<FileText size={20} />}>
              <Markdown>{analysis.resume_quality}</Markdown>
            </Section>
          )}

          {analysis.match_explanation && (
            <Section title="Analysis Breakdown" icon={<ArrowRight size={20} />}>
              <Markdown>{analysis.match_explanation}</Markdown>
            </Section>
          )}

          {/* Missing Keywords Tag Cloud */}
          {analysis.missing_keywords && analysis.missing_keywords.length > 0 && (
            <Section title="Missing Keywords" icon={<Sparkles size={20} />}>
              <div className="flex flex-wrap gap-2 mt-2">
                {analysis.missing_keywords.map((kw, idx) => (
                  <span
                    key={idx}
                    className="text-sm font-medium bg-slate-100 text-slate-700 dark:bg-slate-800 dark:text-slate-300 px-3 py-1.5 rounded-lg border border-slate-200 dark:border-slate-700"
                  >
                    {kw}
                  </span>
                ))}
              </div>
            </Section>
          )}

          {/* Highlighted Warning Cards */}
          {analysis.negative_points && analysis.negative_points.length > 0 && (
            <Section title="Critical Gaps" icon={<AlertTriangle size={20} className="text-red-500" />}>
              <ul className="flex flex-col gap-3">
                {analysis.negative_points.map((pt, idx) => {
                  const content = pt.replace(/^[\-\*\•]\s*/, "");
                  return (
                    <li key={idx} className="flex items-start gap-3 p-4 rounded-xl bg-red-50 dark:bg-red-950/30 border border-red-100 dark:border-red-900/50">
                      <AlertTriangle className="w-5 h-5 text-red-500 shrink-0 mt-0.5" />
                      <div className="flex-1">
                        <Markdown>{content}</Markdown>
                      </div>
                    </li>
                  );
                })}
              </ul>
            </Section>
          )}

          {/* Highlighted Suggestion Cards */}
          {analysis.potential_improvements && analysis.potential_improvements.length > 0 && (
            <Section title="Suggested Actions" icon={<Lightbulb size={20} className="text-amber-500" />}>
              <ul className="flex flex-col gap-3">
                {analysis.potential_improvements.map((pt, idx) => {
                  const content = pt.replace(/^[\-\*\•]\s*/, "");
                  return (
                    <li key={idx} className="flex items-start gap-3 p-4 rounded-xl bg-amber-50 dark:bg-amber-950/30 border border-amber-100 dark:border-amber-900/50">
                      <Lightbulb className="w-5 h-5 text-amber-500 shrink-0 mt-0.5" />
                      <div className="flex-1">
                        <Markdown>{content}</Markdown>
                      </div>
                    </li>
                  );
                })}
              </ul>
            </Section>
          )}

        </div>
      ) : (
        /* The traditional timeline stream while loading/processing */
        <div className="flex flex-col gap-6 max-w-2xl mt-4">
          {logs.map((log, i) => {
            const isProgress = log.type === "progress";
            const isError = log.type === "error";
            const isSuccess = log.type === "success";

            return (
              <div key={i} className="flex items-start gap-4 animate-in fade-in duration-200">
                <div className="mt-0.5">
                  {isProgress ? (
                    <Loader2 size={18} className="animate-spin text-primary" />
                  ) : isError ? (
                    <AlertCircle size={18} className="text-destructive" />
                  ) : (
                    <CheckCircle2 size={18} className="text-emerald-500" />
                  )}
                </div>
                <span
                  className={`text-base font-medium ${isError ? "text-destructive" : isSuccess ? "text-emerald-600 dark:text-emerald-500" : "text-slate-700 dark:text-slate-300"}`}
                >
                  {log.text}
                </span>
              </div>
            );
          })}

          {running && logs.length > 0 && (
            <div className="flex items-center gap-2 text-sm italic text-slate-400 ml-8 animate-pulse">
              Generating insights...
            </div>
          )}
        </div>
      )}

      <div ref={scrollRef} />
    </div>
  );
}
