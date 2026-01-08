"use client";

type TerminalFeedProps = {
  lines: string[];
  title?: string;
};

export default function TerminalFeed({ lines, title = "Live Terminal" }: TerminalFeedProps) {
  return (
    <div className="flex h-full flex-col gap-4">
      <div className="flex items-center justify-between">
        <h2 className="text-sm font-semibold uppercase tracking-[0.3em] text-white/70">
          {title}
        </h2>
        <span className="rounded-full border border-emerald-400/30 bg-emerald-400/10 px-3 py-1 text-[10px] uppercase tracking-[0.2em] text-emerald-200">
          live
        </span>
      </div>
      <div className="flex-1 overflow-hidden rounded-2xl border border-white/10 bg-slate-950/50 p-4">
        <div className="h-full overflow-y-auto pr-2 font-mono text-xs text-emerald-100/90">
          {lines.length === 0 ? (
            <p className="text-emerald-200/60">Waiting for live ticks...</p>
          ) : (
            lines.map((line, index) => (
              <p key={`${index}-${line}`} className="leading-5">
                {line}
              </p>
            ))
          )}
        </div>
      </div>
    </div>
  );
}
