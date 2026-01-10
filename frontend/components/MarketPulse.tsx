"use client";

import { ArrowTrendingUpIcon, ArrowTrendingDownIcon } from "@heroicons/react/20/solid";

type MarketPulseProps = {
    tickers: Record<string, number>;
    previous: Record<string, number>;
    status: string;
    sentiment: {
        bullish_pct: number;
        label: string;
    };
};

export default function MarketPulse({ tickers, previous, status, sentiment }: MarketPulseProps) {
    const assets = Object.keys(tickers);

    return (
        <div className="flex flex-col gap-6">
            <div className="flex items-center justify-between">
                <div>
                    <p className="text-xs uppercase tracking-[0.3em] text-secondary/70">
                        Market Pulse
                    </p>
                    <h2 className="font-display text-2xl font-semibold text-white">Equities</h2>
                </div>
                <div className="flex items-center gap-2">
                    <div className={`h-2 w-2 rounded-full ${status === 'live' ? 'bg-primary shadow-[0_0_8px_rgba(16,185,129,0.8)] animate-pulse' : 'bg-white/20'}`} />
                    <span className="text-[10px] uppercase tracking-widest text-white/40">{status}</span>
                </div>
            </div>

            <div className="flex flex-col gap-3">
                {assets.map((symbol) => {
                    const price = tickers[symbol];
                    const prev = previous[symbol] || price;
                    const diff = price - prev;
                    const isUp = diff >= 0;

                    return (
                        <div key={symbol} className="glass-panel group flex items-center justify-between rounded-2xl p-4 transition-all hover:bg-white/[0.08]">
                            <div className="flex items-center gap-4">
                                <div className={`flex h-10 w-10 items-center justify-center rounded-xl font-bold ${isUp ? 'bg-primary/10 text-primary' : 'bg-accent/10 text-accent'
                                    }`}>
                                    {symbol[0]}
                                </div>
                                <div>
                                    <h3 className="text-sm font-bold text-white group-hover:neon-text-secondary transition-all">{symbol}</h3>
                                    <p className="text-[10px] text-white/40">Equity Index</p>
                                </div>
                            </div>

                            <div className="text-right">
                                <p className="font-mono text-sm font-semibold text-white">
                                    {price.toFixed(6)}
                                </p>
                                <div className={`flex items-center justify-end gap-1 text-[10px] font-medium ${isUp ? 'text-primary' : 'text-accent'
                                    }`}>
                                    {isUp ? <ArrowTrendingUpIcon className="h-3 w-3" /> : <ArrowTrendingDownIcon className="h-3 w-3" />}
                                    {Math.abs(diff).toFixed(6)}
                                </div>
                            </div>
                        </div>
                    );
                })}
            </div>

            <div className="mt-4 rounded-2xl bg-gradient-to-br from-secondary/20 to-primary/10 p-4 border border-white/5">
                <p className="text-[10px] uppercase tracking-widest text-white/40">Market Sentiment</p>
                <div className="mt-2 flex items-end justify-between">
                    <p className="text-xl font-display font-bold text-white">{sentiment.label}</p>
                    <p className="text-xs text-primary font-medium">{sentiment.bullish_pct}% Bullish</p>
                </div>
                <div className="mt-2 h-1.5 w-full overflow-hidden rounded-full bg-white/5">
                    <div className="h-full bg-primary transition-all duration-500" style={{ width: `${sentiment.bullish_pct}%` }} />
                </div>
            </div>
        </div>
    );
}
