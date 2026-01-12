"use client";
// Context7 (Next.js "use client" directive): https://github.com/vercel/next.js/blob/canary/docs/01-app/03-api-reference/01-directives/use-client.mdx

import { ArrowTrendingUpIcon, ArrowTrendingDownIcon } from "@heroicons/react/20/solid";

type MarketPulseProps = {
    tickers: Record<string, number>;
    previous: Record<string, number>;
    status: string;
    activeSymbol: string;
    onSelectSymbol?: (symbol: string) => void;
};

/**
 * MarketPulse renders the ticker list, highlights the live status, and emits
 * selection events for the active instrument.
 */
export default function MarketPulse({ tickers, previous, status, activeSymbol, onSelectSymbol }: MarketPulseProps) {
    // Derive the list of symbols from the ticker state to keep rendering deterministic.
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
                {/* Each row shows the latest price delta and status indicator */}
                {assets.map((symbol) => {
                    const price = tickers[symbol];
                    const prev = previous[symbol] || price;
                    const diff = price - prev;
                    const isUp = diff >= 0;

                    const isActive = symbol === activeSymbol;
                    return (
                        <button
                            key={symbol}
                            type="button"
                            onClick={() => onSelectSymbol?.(symbol)}
                            aria-pressed={isActive}
                            className={`glass-panel group flex w-full items-center justify-between rounded-2xl p-4 text-left transition-all hover:bg-white/[0.08] ${
                                isActive ? "ring-1 ring-secondary/50 bg-white/[0.06]" : ""
                            }`}
                        >
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
                        </button>
                    );
                })}
            </div>

        </div>
    );
}
