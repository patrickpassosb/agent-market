"use client";

type AgentFeedItem = {
  id: string;
  title: string;
  detail: string;
  time: string;
};

type AgentFeedProps = {
  items: AgentFeedItem[];
};

export default function AgentFeed({ items }: AgentFeedProps) {
  return (
    <section className="flex h-full flex-col gap-4">
      <div>
        <p className="text-xs uppercase tracking-[0.3em] text-violet-200/70">
          Agent Feed
        </p>
        <h2 className="text-2xl font-semibold text-white">Recent Actions</h2>
      </div>
      <div className="flex flex-1 flex-col gap-3 rounded-2xl border border-white/10 bg-white/5 p-4 shadow-[0_0_50px_-30px_rgba(167,139,250,0.7)]">
        {items.length === 0 ? (
          <div className="flex flex-1 items-center justify-center text-sm text-white/50">
            Waiting for agent updates.
          </div>
        ) : (
          items.map((item) => (
            <div
              key={item.id}
              className="flex items-start justify-between gap-4 border-b border-white/5 pb-3 last:border-b-0 last:pb-0"
            >
              <div>
                <p className="text-sm font-semibold text-white">{item.title}</p>
                <p className="text-xs text-white/60">{item.detail}</p>
              </div>
              <span className="text-xs text-white/40">{item.time}</span>
            </div>
          ))
        )}
      </div>
    </section>
  );
}
