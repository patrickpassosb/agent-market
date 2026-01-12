"use client";
// Context7 /vercel/next.js/v16.1.1 ("use client" directive).

import { useEffect, useState } from "react";
import MarketPulse from "./MarketPulse";
import RealtimeChart from "./RealtimeChart";
import AgentRoster from "./AgentRoster";
import SentimentFeed from "./SentimentFeed";
import {
  CpuChipIcon,
  GlobeAltIcon,
  ServerIcon
} from "@heroicons/react/24/outline";

/**
 * Dashboard coordinates API polling, WebSocket streaming, and the premium UI panels.
 *
 * It keeps local state for tickers, news, sentiment, performance metrics, and selected symbol,
 * and stitches together `MarketPulse`, `RealtimeChart`, `AgentRoster`, and `SentimentFeed`.
 */

type Ticker = "AAPL" | "TSLA" | "NVDA" | "MSFT";
type TickerMap = Record<Ticker, number>;
type ChartPoint = {
  time: number;
  value: number;
};
type TransactionHistoryRecord = {
  item: Ticker;
  price: number;
  timestamp: string;
  buyer_id?: string;
  seller_id?: string;
  run_id?: string;
};

type AgentRecord = {
  id: string;
  persona: string;
  model: string;
  portfolio?: {
    total_value: number;
    pnl: number;
    pnl_percent: number;
    roi: number;
  };
};

type NewsItem = {
  headline: string;
  body: string;
  tick: number;
};

const TICKERS: Ticker[] = ["AAPL", "TSLA", "NVDA", "MSFT"];
const DEFAULT_TICKERS: TickerMap = {
  AAPL: 0,
  TSLA: 0,
  NVDA: 0,
  MSFT: 0,
};

const API_BASE = process.env.NEXT_PUBLIC_API_BASE ?? "http://localhost:8000";
const WS_URL = process.env.NEXT_PUBLIC_WS_URL ?? "ws://localhost:8000/ws";
// Context7 /vercel/next.js/v16.1.1 (environment variables).
const API_KEY = process.env.NEXT_PUBLIC_API_KEY;
const API_HEADERS = API_KEY ? { "X-API-Key": API_KEY } : undefined;
const WS_URL_WITH_TOKEN = API_KEY
  ? `${WS_URL}${WS_URL.includes("?") ? "&" : "?"}token=${encodeURIComponent(API_KEY)}`
  : WS_URL;

const HISTORY_LIMIT = 200;

const createEmptyHistory = (basePrices: TickerMap): Record<Ticker, ChartPoint[]> => {
  return TICKERS.reduce((acc, symbol) => {
    const basePrice = basePrices[symbol] ?? 0;
    acc[symbol] = basePrice > 0 ? [{ time: Math.floor(Date.now() / 1000), value: basePrice }] : [];
    return acc;
  }, {} as Record<Ticker, ChartPoint[]>);
};

const ensureAscending = (series: ChartPoint[]): ChartPoint[] => {
  if (!series.length) return [];
  const sorted = [...series].sort((a, b) => a.time - b.time);
  const normalized: ChartPoint[] = [];
  let lastTime = -Infinity;
  for (const point of sorted) {
    let time = point.time;
    if (time <= lastTime) {
      time = lastTime + 1;
    }
    normalized.push({ ...point, time });
    lastTime = time;
  }
  return normalized;
};

const normalizeHistory = (records: TransactionHistoryRecord[], basePrices: TickerMap): Record<Ticker, ChartPoint[]> => {
  const history = TICKERS.reduce((acc, symbol) => {
    acc[symbol] = [];
    return acc;
  }, {} as Record<Ticker, ChartPoint[]>);

  records.forEach((record) => {
    if (!TICKERS.includes(record.item)) return;
    const point: ChartPoint = {
      time: Math.floor(new Date(record.timestamp).getTime() / 1000),
      value: record.price,
    };
    history[record.item].push(point);
  });

  for (const symbol of TICKERS) {
    if (!history[symbol].length && (basePrices[symbol] ?? 0) > 0) {
      history[symbol].push({
        time: Math.floor(Date.now() / 1000),
        value: basePrices[symbol],
      });
    }
    history[symbol] = ensureAscending(history[symbol]).slice(-HISTORY_LIMIT);
  }

  return history;
};

export default function Dashboard() {
  const [tickers, setTickers] = useState<TickerMap>(DEFAULT_TICKERS);
  const [previousTickers, setPreviousTickers] = useState<TickerMap>(DEFAULT_TICKERS);
  const [agents, setAgents] = useState<AgentRecord[]>([]);
  const [latestNews, setLatestNews] = useState<NewsItem | null>(null);
  const [status, setStatus] = useState<"connecting" | "live" | "reconnecting" | "error">("connecting");
  const [tickCount, setTickCount] = useState(0);
  const [sentiment, setSentiment] = useState({ bullish_pct: 52, label: "Neutral" });
  const [metrics, setMetrics] = useState({ total_volume: 0, volatility: "Low" });

  const [priceHistory, setPriceHistory] = useState<Record<Ticker, ChartPoint[]>>(() => createEmptyHistory(DEFAULT_TICKERS));

  const [activeSymbol, setActiveSymbol] = useState<Ticker>("AAPL");

  const activeSeries = priceHistory[activeSymbol] ?? [];

  useEffect(() => {
    // Initial HTTP poll to bootstrap market state + agent roster.
    const fetchData = async () => {
      try {
        const [marketRes, agentsRes] = await Promise.all([
          fetch(`${API_BASE}/state`, { headers: API_HEADERS }),
          fetch(`${API_BASE}/agents`, { headers: API_HEADERS })
        ]);

        if (marketRes.ok) {
          const data = await marketRes.json();
          setTickers(data.prices || data.tickers || DEFAULT_TICKERS);
          setTickCount(data.tick || 0);
          if (data.sentiment) setSentiment(data.sentiment);
          if (data.metrics) setMetrics(data.metrics);
          const history = Array.isArray(data.history) ? data.history : [];
          setPriceHistory(normalizeHistory(history, data.prices || DEFAULT_TICKERS));
        }

        if (agentsRes.ok) {
          setAgents(await agentsRes.json());
        }
      } catch (e) {
        console.error("Initial fetch failed", e);
      }
    };
    fetchData();
  }, []);

  // React useEffect is used to sync this component with WebSocket updates.
  // Context7 /websites/react_dev (useEffect hook docs).
  useEffect(() => {
    // Maintain a resilient WebSocket connection to stream live updates.
    let socket: WebSocket | null = null;
    let reconnectTimer: any;

    const appendHistoryPoint = (record: TransactionHistoryRecord) => {
      if (!record || !TICKERS.includes(record.item)) {
        return;
      }
      const baseTime = Math.floor(new Date(record.timestamp).getTime() / 1000);
      setPriceHistory((prev) => {
        const next = { ...prev };
        const series = next[record.item] ?? [];
        const lastTime = series.length ? series[series.length - 1].time : -Infinity;
        const point: ChartPoint = {
          time: baseTime <= lastTime ? lastTime + 1 : baseTime,
          value: record.price,
        };
        const updated = [...series, point];
        if (updated.length > HISTORY_LIMIT) {
          updated.shift();
        }
        next[record.item] = updated;
        return next;
      });
    };

    const connect = () => {
      setStatus("connecting");
      socket = new WebSocket(WS_URL_WITH_TOKEN);

      socket.onopen = () => setStatus("live");
      socket.onmessage = (event) => {
        try {
          const payload = JSON.parse(event.data);
          if (payload.type === "ticker" && payload.data) {
            setTickers(prev => {
              setPreviousTickers(prev);
              return { ...prev, ...payload.data };
            });
            if (payload.sentiment) {
              setSentiment(payload.sentiment);
            }
            if (payload.metrics) {
              setMetrics(payload.metrics);
            }
            if (typeof payload.tick === "number") {
              setTickCount(payload.tick);
            }
            if (payload.latest_transaction) {
              appendHistoryPoint(payload.latest_transaction);
            }
            if (Array.isArray(payload.agents)) {
              setAgents(payload.agents);
            }
          }
          if (payload.type === "news") {
            setLatestNews(payload.data);
          }
        } catch (e) { console.error(e); }
      };
      socket.onclose = () => {
        setStatus("reconnecting");
        reconnectTimer = setTimeout(connect, 2000);
      };
    };

    connect();
    return () => {
      socket?.close();
      clearTimeout(reconnectTimer);
    };
  }, []);

  return (
    <div className="flex min-h-screen flex-col overflow-hidden">
      {/* Top Navigation Bar */}
      <nav className="flex items-center justify-between border-b border-white/5 bg-black/20 px-8 py-3 backdrop-blur-md">
        <div className="flex items-center gap-6">
          <div className="flex items-center gap-2">
            <span className="font-display text-lg font-bold tracking-tight text-white">
              AI AGENT <span className="font-light text-white/50">MARKET</span>
            </span>
          </div>
          <div className="h-4 w-px bg-white/10" />
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-1.5 text-xs text-white/40">
              <ServerIcon className="h-3.5 w-3.5" />
              <span>{API_BASE}</span>
            </div>
            <div className="flex items-center gap-1.5 text-xs text-white/40">
              <GlobeAltIcon className="h-3.5 w-3.5" />
              <span>Tick: <span className="text-white">{tickCount}</span></span>
            </div>
          </div>
        </div>
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2 rounded-full bg-white/5 px-3 py-1 border border-white/10">
            <div className={`h-1.5 w-1.5 rounded-full ${status === 'live' ? 'bg-primary' : 'bg-accent'} shadow-[0_0_8px_hsl(var(--primary-glow))]`} />
            <span className="text-[10px] font-bold uppercase tracking-widest text-white/60">{status === 'live' ? 'System Online' : 'Connecting'}</span>
          </div>
          <div className="h-8 w-8 rounded-full bg-gradient-to-br from-white/10 to-transparent p-[1px]">
            <div className="h-full w-full rounded-full bg-background" />
          </div>
        </div>
      </nav>

      <main className="grid flex-1 gap-6 p-6 lg:grid-cols-[300px_1fr_350px]">
        {/* Left Column: Market Pulse & Sentiment */}
        <section className="flex flex-col gap-6 pr-2">
          <div className="glass-panel rounded-[2.5rem] p-6 shadow-indigo-500/5">
            <MarketPulse
              tickers={tickers}
              previous={previousTickers}
              status={status}
              activeSymbol={activeSymbol}
              onSelectSymbol={(symbol) => setActiveSymbol(symbol as Ticker)}
            />
          </div>
          <div className="glass-panel rounded-[2.5rem] p-6 bg-gradient-to-br from-secondary/20 to-primary/10">
            <p className="text-[10px] uppercase tracking-widest text-white/40">Market Sentiment</p>
            <div className="mt-2 flex items-end justify-between">
              <p className="text-xl font-display font-bold text-white">{sentiment.label}</p>
              <p className="text-xs text-primary font-medium">{sentiment.bullish_pct}% Bullish</p>
            </div>
            <div className="mt-2 h-1.5 w-full overflow-hidden rounded-full bg-white/5">
              <div className="h-full bg-primary transition-all duration-500" style={{ width: `${sentiment.bullish_pct}%` }} />
            </div>
          </div>
          <div className="glass-panel rounded-[2.5rem] p-6 bg-gradient-to-br from-primary/5 to-transparent">
            <div className="flex items-center gap-2 mb-4">
              <CpuChipIcon className="h-5 w-5 text-primary" />
              <p className="text-xs font-bold uppercase tracking-widest text-primary/70">Performance Metrics</p>
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <p className="text-[10px] text-white/30 uppercase mb-1">Total Volume</p>
                <p className="text-xl font-mono text-white">{metrics.total_volume}</p>
              </div>
              <div>
                <p className="text-[10px] text-white/30 uppercase mb-1">Volatility</p>
                <p className="text-xl font-mono text-accent">{metrics.volatility}</p>
              </div>
            </div>
          </div>
        </section>

        {/* Center Column: Chart & Main Agent Roster */}
        <section className="flex flex-col gap-6">
          <div className="glass-panel flex-1 rounded-[2.5rem] p-8">
            <RealtimeChart key={activeSymbol} seriesData={activeSeries} symbol={activeSymbol} />
          </div>
          <div className="glass-panel max-h-[400px] rounded-[2.5rem] p-8 overflow-y-auto">
            <AgentRoster agents={agents} />
          </div>
        </section>

        {/* Right Column: Sentiment & Headlines */}
        <section className="flex flex-col gap-6">
          <div className="glass-panel flex-1 rounded-[2.5rem] p-8 overflow-y-auto">
            <SentimentFeed latestNews={latestNews} />
          </div>
        </section>
      </main>

      {/* Footer / Status Bar */}
      <footer className="border-t border-white/5 bg-black/40 px-8 py-2 text-[10px] uppercase tracking-[0.2em] text-white/30 flex justify-between">
        <div className="flex gap-6">
          <span>Simulation Mode: Reactive</span>
          <span>Seed Inventory: 10.0</span>
        </div>
        <div>
          © 2026 AI Agent Market Framework
        </div>
      </footer>
    </div>
  );
}
