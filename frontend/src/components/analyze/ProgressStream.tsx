import { useRef, useEffect } from "react";
import { type StreamLine } from "../../hooks/useResumeAnalysis";
import { Loader2, CheckCircle2, AlertCircle } from "lucide-react";

interface ProgressStreamProps {
  logs: StreamLine[];
  running: boolean;
}

export function ProgressStream({ logs, running }: ProgressStreamProps) {
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [logs]);

  if (logs.length === 0 && !running) return null;

  return (
    <div className="w-full max-w-5xl flex flex-col gap-4 animate-in fade-in duration-300">
      <div className="flex items-center gap-3 px-2">
        <h3 className="text-xl font-bold text-foreground">Analysis Progress</h3>
        {running ? (
          <span className="flex items-center gap-2 text-sm text-primary font-medium px-3 py-1 bg-primary/10 rounded-full">
            <Loader2 size={14} className="animate-spin" />
            Processing
          </span>
        ) : logs.some((l) => l.type === "error") ? (
          <span className="flex items-center gap-2 text-sm text-destructive font-medium px-3 py-1 bg-destructive/10 rounded-full">
            <AlertCircle size={14} />
            Failed
          </span>
        ) : logs.some((l) => l.type === "success") ? (
          <span className="flex items-center gap-2 text-sm text-green-600 dark:text-green-500 font-medium px-3 py-1 bg-green-500/10 rounded-full">
            <CheckCircle2 size={14} />
            Complete
          </span>
        ) : null}
      </div>

      <div
        ref={scrollRef}
        className="h-[300px] w-full overflow-y-auto bg-[#0a0a0a] rounded-xl border border-border shadow-inner p-4 font-mono text-sm leading-relaxed"
      >
        {logs.map((log, i) => (
          <div
            key={i}
            className={`py-1 ${
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
          <div className="py-2 text-zinc-500 flex items-center gap-2 animate-pulse">
            <div className="w-2 h-2 bg-primary rounded-full" />
            <div className="w-2 h-2 bg-primary rounded-full animation-delay-150" />
            <div className="w-2 h-2 bg-primary rounded-full animation-delay-300" />
          </div>
        )}
      </div>
    </div>
  );
}
