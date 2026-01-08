"use client";

type Ticker = "AAPL" | "TSLA" | "NVDA" | "MSFT";

type MarketWatchProps = {
  tickers: Record<Ticker, number>;
  previous: Record<Ticker, number>;
  status: "connecting" | "live" | "reconnecting" | "error";
  lastUpdate: string | null;
};

const orderedTickers: Ticker[] = ["AAPL", "TSLA", "NVDA", "MSFT"];

const formatBtc = (value: number) =>
  value.toLocaleString("en-US", {
    minimumFractionDigits: 4,
    maximumFractionDigits: 6,
  });

export default function MarketWatch({
  tickers,
  previous,
  status,
  lastUpdate,
}: MarketWatchProps) {
  return (
    <section className="flex h-full flex-col gap-4">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-xs uppercase tracking-[0.3em] text-emerald-200/70">
            Market Watch
          </p>
          <h2 className="text-2xl font-semibold text-white">Crypto Equities</h2>
        </div>
        <div className="flex flex-col items-end text-xs text-white/60">
          <span className="flex items-center gap-2">
            <span
              className={`h-2 w-2 rounded-full ${
                status === "live"
                  ? "bg-emerald-400"
                  : status === "reconnecting"
                  ? "bg-amber-400"
                  : status === "error"
                  ? "bg-rose-400"
                  : "bg-slate-400"
              }`}
            />
            {status}
          </span>
          {lastUpdate ? <span>{lastUpdate}</span> : <span>No data yet</span>}
        </div>
      </div>
      <div className="grid gap-3">
        {orderedTickers.map((ticker) => {
          const current = tickers[ticker];
          const prior = previous[ticker] ?? current;
          const delta = current - prior;
          const isUp = delta >= 0;
          return (
            <div
              key={ticker}
              className="flex items-center justify-between rounded-xl border border-white/10 bg-white/5 px-4 py-3 shadow-[0_0_24px_-16px_rgba(45,212,191,0.7)]"
            >
              <div>
                <p className="text-sm text-white/60">{ticker}</p>
                <p className="text-xl font-semibold text-white">
                  {formatBtc(current)} BTC
                </p>
              </div>
              <div
                className={`rounded-full px-3 py-1 text-xs font-semibold ${
                  isUp
                    ? "bg-emerald-400/15 text-emerald-200"
                    : "bg-rose-400/15 text-rose-200"
                }`}
              >
                {isUp ? "+" : ""}
                {delta.toFixed(6)}
              </div>
            </div>
          );
        })}
      </div>
    </section>
  );
}
