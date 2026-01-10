"use client";

import { NewspaperIcon, SparklesIcon } from "@heroicons/react/24/outline";

type NewsItem = {
    headline: string;
    body: string;
    tick: number;
};

export default function SentimentFeed({ latestNews }: { latestNews: NewsItem | null }) {
    return (
        <section className="flex flex-col gap-6">
            <div className="flex items-center gap-3">
                <div className="rounded-xl bg-accent/10 p-2 text-accent">
                    <NewspaperIcon className="h-5 w-5" />
                </div>
                <div>
                    <p className="text-xs uppercase tracking-[0.3em] text-accent/70">
                        Insights Feed
                    </p>
                    <h2 className="font-display text-2xl font-semibold text-white">Market Intelligence</h2>
                </div>
            </div>

            <div className="flex flex-col gap-4">
                {latestNews ? (
                    <div className="glass-card relative overflow-hidden border-accent/20 bg-accent/5 transition-all hover:bg-accent/10">
                        <div className="absolute -right-4 -top-4 text-accent/10">
                            <SparklesIcon className="h-24 w-24" />
                        </div>
                        <div className="relative">
                            <div className="mb-3 inline-flex rounded-full bg-accent/20 px-2 py-0.5 text-[10px] font-bold uppercase tracking-wider text-accent border border-accent/30">
                                Tick #{latestNews.tick} • AI Analysis
                            </div>
                            <h3 className="mb-2 font-display text-lg font-bold leading-tight text-white decoration-accent/30 underline-offset-4 hover:underline">
                                {latestNews.headline}
                            </h3>
                            <p className="text-sm leading-relaxed text-white/60">
                                {latestNews.body}
                            </p>
                        </div>
                    </div>
                ) : (
                    <div className="flex flex-col items-center justify-center rounded-3xl border border-dashed border-white/10 py-12 text-center">
                        <SparklesIcon className="mb-4 h-10 w-10 text-white/10" />
                        <p className="max-w-[150px] text-xs font-medium text-white/30 uppercase tracking-widest">
                            Analyzing Market Dynamics...
                        </p>
                    </div>
                )}

                {/* Placeholder news items for visual richness */}
                <div className="glass-card opacity-40 grayscale pointer-events-none">
                    <div className="mb-2 inline-flex rounded-full bg-white/5 px-2 py-0.5 text-[10px] font-bold uppercase tracking-wider text-white/40">
                        Historical Data
                    </div>
                    <h3 className="mb-1 text-sm font-bold text-white/80">Volatility Spike Detected in Tech Sector</h3>
                    <p className="text-xs text-white/40 line-clamp-2">Agents are adjusting positions as the market prepares for potential redistribution of wealth across majors...</p>
                </div>
            </div>
        </section>
    );
}
