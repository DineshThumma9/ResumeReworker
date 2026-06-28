import { useRef, useEffect } from "react";
import { type StreamLine } from "../../hooks/useResumeAnalysis";
import { Loader2, CheckCircle2, AlertCircle } from "lucide-react";

interface ProgressStreamProps {
  logs: StreamLine[];
  running: boolean;
  onReset?: () => void;
}

export function ProgressStream({ logs, running, onReset }: ProgressStreamProps) {
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [logs]);

  if (logs.length === 0 && !running) return null;

  // Find if we have any analysis data inside the logs
  const analysisLog = logs.find((l) => l.analysis !== undefined);
  const analysis = analysisLog?.analysis;

  return (
    <div className="w-full max-w-5xl flex flex-col gap-6 animate-in fade-in duration-300 mt-4 pb-10">
      {/* Header Row */}
      <div className="flex items-center justify-between px-2 w-full">
        <div className="flex items-center gap-3">
          <h3 className="font-['EB_Garamond'] text-[24px] font-semibold text-foreground">
            Analysis Progress
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
            className="flex items-center gap-1.5 bg-transparent text-foreground font-['EB_Garamond'] text-[13px] font-medium tracking-wider uppercase border border-border rounded-md px-4 py-2 cursor-pointer hover:bg-muted/40 transition-colors"
          >
            Back to Form
          </button>
        )}
      </div>

      {/* AI MATCH PROFILE CARD */}
      {analysis && (
        <div className="w-full bg-card p-6 rounded-xl border border-border shadow-sm flex flex-col gap-6 animate-in fade-in duration-300">
          <div className="flex items-center justify-between border-b border-border pb-4">
            <div className="flex flex-col">
              <span className="font-['EB_Garamond'] text-2xl font-semibold text-foreground">AI Match Profile</span>
              <span className="text-[11px] text-muted-foreground">Resume vs Job Description Review</span>
            </div>
            {analysis.score !== undefined && (
              <div className="flex items-center gap-2.5 bg-primary/5 px-4 py-2 rounded-lg border border-primary/10">
                <span className="text-[10px] text-muted-foreground uppercase tracking-widest font-semibold">Match Score:</span>
                <span className="font-['EB_Garamond'] text-3xl font-bold text-primary">{analysis.score}%</span>
              </div>
            )}
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            {/* Left Column: General stats and keywords */}
            <div className="flex flex-col gap-5">
              {analysis.resume_quality && (
                <div>
                  <h4 className="text-[11px] font-bold uppercase tracking-wider text-muted-foreground mb-1.5">Resume Quality</h4>
                  <p className="text-sm font-semibold text-foreground">{analysis.resume_quality}</p>
                </div>
              )}
              {analysis.match_explanation && (
                <div>
                  <h4 className="text-[11px] font-bold uppercase tracking-wider text-muted-foreground mb-1.5">Explanation</h4>
                  <p className="text-xs text-muted-foreground leading-relaxed whitespace-pre-wrap">{analysis.match_explanation}</p>
                </div>
              )}
              {analysis.missing_keywords && analysis.missing_keywords.length > 0 && (
                <div>
                  <h4 className="text-[11px] font-bold uppercase tracking-wider text-muted-foreground mb-2">Missing Keywords</h4>
                  <div className="flex flex-wrap gap-1.5">
                    {analysis.missing_keywords.map((kw) => (
                      <span key={kw} className="text-[10px] font-mono bg-red-500/10 dark:bg-red-500/20 text-red-600 dark:text-red-400 px-2 py-0.5 rounded border border-red-500/20">
                        {kw}
                      </span>
                    ))}
                  </div>
                </div>
              )}
            </div>

            {/* Right Column: Improvements and Red Flags */}
            <div className="flex flex-col gap-5">
              {analysis.potential_improvements && analysis.potential_improvements.length > 0 && (
                <div>
                  <h4 className="text-[11px] font-bold uppercase tracking-wider text-muted-foreground mb-2">Suggested Improvements</h4>
                  <ul className="list-disc list-inside text-xs text-muted-foreground flex flex-col gap-2 pl-1">
                    {analysis.potential_improvements.map((imp, idx) => (
                      <li key={idx} className="leading-relaxed list-item list-outside ml-4">{imp}</li>
                    ))}
                  </ul>
                </div>
              )}
              {analysis.negative_points && analysis.negative_points.length > 0 && (
                <div>
                  <h4 className="text-[11px] font-bold uppercase tracking-wider text-muted-foreground mb-2">Gaps / Red Flags</h4>
                  <ul className="list-disc list-inside text-xs text-muted-foreground flex flex-col gap-2 pl-1">
                    {analysis.negative_points.map((pt, idx) => (
                      <li key={idx} className="leading-relaxed text-red-500/80 dark:text-red-400/80 list-item list-outside ml-4">{pt}</li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Solid, Bordered Console Box */}
      <div className="flex flex-col gap-2 w-full">
        <span className="text-[11px] font-bold uppercase tracking-wider text-muted-foreground px-2">Console Output</span>
        <div
          ref={scrollRef}
          className="min-h-[220px] w-full overflow-y-auto bg-zinc-950 dark:bg-zinc-950/80 rounded-xl border border-border shadow-lg p-5 font-mono text-xs leading-relaxed"
        >
          {logs.map((log, i) => (
            <div
              key={i}
              className={`py-1.5 border-b border-zinc-900 last:border-0 ${
                log.type === "error"
                  ? "text-red-400 font-medium"
                  : log.type === "success"
                  ? "text-green-400 font-medium"
                  : "text-zinc-300"
              }`}
            >
              {log.text}
            </div>
          ))}
          {running && (
            <div className="py-3 text-zinc-500 flex items-center gap-2 animate-pulse">
              <span className="text-xs italic">Awaiting backend response</span>
              <div className="flex gap-1">
                <div className="w-1.5 h-1.5 bg-primary rounded-full animate-bounce" />
                <div className="w-1.5 h-1.5 bg-primary rounded-full animate-bounce [animation-delay:0.2s]" />
                <div className="w-1.5 h-1.5 bg-primary rounded-full animate-bounce [animation-delay:0.4s]" />
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
