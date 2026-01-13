"use client";
// Context7 /vercel/next.js/v16.1.1 ("use client" directive).

import { useEffect, useRef, useState } from "react";
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

type SimulationConfig = {
  max_ticks: number;
  checkpoint_every: number;
  checkpoint_dir: string;
  report_enabled: boolean;
  report_dir: string;
  initial_price: number;
  seed_inventory: number;
  agent_count: number;
  tick_duration: number;
  model_provider_order: string;
};

type SimulationSummary = {
  run_id: string;
  ticks: number;
  total_trades: number;
  avg_price: number | null;
  min_price: number | null;
  max_price: number | null;
  negotiation_count: number;
  report_dir?: string | null;
};

const TICKERS: Ticker[] = ["AAPL", "TSLA", "NVDA", "MSFT"];
const DEFAULT_TICKERS: TickerMap = {
  AAPL: 0,
  TSLA: 0,
  NVDA: 0,
  MSFT: 0,
};
const DEFAULT_SIM_CONFIG: SimulationConfig = {
  max_ticks: 0,
  checkpoint_every: 10,
  checkpoint_dir: "checkpoints",
  report_enabled: true,
  report_dir: "reports",
  initial_price: 0.005,
  seed_inventory: 10,
  agent_count: 12,
  tick_duration: 2.0,
  model_provider_order: "cerebras,groq,gemini,openrouter,ollama",
};
// Context7 /websites/v3_tailwindcss (hover/focus/disabled variants).
// Context7 /websites/v3_tailwindcss (appearance-none utility).
const CONTROL_INPUT_CLASSES =
  "h-9 rounded-xl border border-white/15 bg-black/50 px-3 text-xs text-white/85 transition focus:outline-none focus:ring-1 focus:ring-white/30 focus:border-white/40 hover:border-white/35 disabled:cursor-not-allowed disabled:opacity-60 appearance-none";
const CONTROL_BUTTON_PRIMARY_CLASSES =
  "rounded-full border border-white/20 bg-white px-4 py-2 text-[10px] font-bold uppercase tracking-widest text-black transition-all duration-200 hover:-translate-y-0.5 hover:bg-black hover:text-white hover:border-white/70 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-white/50 focus-visible:ring-offset-2 focus-visible:ring-offset-black/40 disabled:cursor-not-allowed disabled:bg-white/10 disabled:text-white/40";
const CONTROL_BUTTON_SECONDARY_CLASSES =
  "rounded-full border border-white/25 bg-transparent px-4 py-2 text-[10px] font-bold uppercase tracking-widest text-white/70 transition-all duration-200 hover:-translate-y-0.5 hover:border-white/60 hover:bg-white/10 hover:text-white focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-white/40 focus-visible:ring-offset-2 focus-visible:ring-offset-black/40 disabled:cursor-not-allowed disabled:border-white/10 disabled:text-white/30";

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
  const [simRunning, setSimRunning] = useState(false);
  const [simConfig, setSimConfig] = useState<SimulationConfig>(DEFAULT_SIM_CONFIG);
  const [simSummary, setSimSummary] = useState<SimulationSummary | null>(null);
  const [simReportDir, setSimReportDir] = useState<string | null>(null);

  const [priceHistory, setPriceHistory] = useState<Record<Ticker, ChartPoint[]>>(() => createEmptyHistory(DEFAULT_TICKERS));
  // Context7: https://react.dev/reference/react/useRef (store mutable values without re-rendering)
  const lastTickRef = useRef<number | null>(null);

  const [activeSymbol, setActiveSymbol] = useState<Ticker>("AAPL");

  const activeSeries = priceHistory[activeSymbol] ?? [];

  useEffect(() => {
    // Initial HTTP poll to bootstrap market state + agent roster.
    const fetchData = async () => {
      try {
        const [marketRes, agentsRes, statusRes] = await Promise.all([
          fetch(`${API_BASE}/state`, { headers: API_HEADERS }),
          fetch(`${API_BASE}/agents`, { headers: API_HEADERS }),
          fetch(`${API_BASE}/simulation/status`, { headers: API_HEADERS }),
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
        if (statusRes.ok) {
          const statusData = await statusRes.json();
          setSimRunning(Boolean(statusData.running));
          setSimConfig({ ...DEFAULT_SIM_CONFIG, ...(statusData.config ?? {}) });
          setSimSummary(statusData.summary ?? null);
          setSimReportDir(statusData.report_dir ?? null);
        }
      } catch (e) {
        console.error("Initial fetch failed", e);
      }
    };
    fetchData();
  }, []);

  const refreshSimulationStatus = async () => {
    try {
      const statusRes = await fetch(`${API_BASE}/simulation/status`, { headers: API_HEADERS });
      if (!statusRes.ok) return;
      const statusData = await statusRes.json();
      setSimRunning(Boolean(statusData.running));
      setSimConfig({ ...DEFAULT_SIM_CONFIG, ...(statusData.config ?? {}) });
      setSimSummary(statusData.summary ?? null);
      setSimReportDir(statusData.report_dir ?? null);
    } catch (e) {
      console.error("Simulation status fetch failed", e);
    }
  };

  const startSimulation = async () => {
    try {
      const response = await fetch(`${API_BASE}/simulation/start`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          ...(API_HEADERS ?? {}),
        },
        body: JSON.stringify(simConfig),
      });
      if (!response.ok) {
        console.error("Failed to start simulation");
      }
      await refreshSimulationStatus();
    } catch (e) {
      console.error("Start simulation failed", e);
    }
  };

  const stopSimulation = async () => {
    try {
      const response = await fetch(`${API_BASE}/simulation/stop`, {
        method: "POST",
        headers: API_HEADERS,
      });
      if (!response.ok) {
        console.error("Failed to stop simulation");
      }
      await refreshSimulationStatus();
    } catch (e) {
      console.error("Stop simulation failed", e);
    }
  };

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

    const appendPriceSnapshot = (prices: TickerMap) => {
      const now = Math.floor(Date.now() / 1000);
      setPriceHistory((prev) => {
        const next = { ...prev };
        TICKERS.forEach((symbol) => {
          const value = prices[symbol];
          if (typeof value !== "number") {
            return;
          }
          const series = next[symbol] ?? [];
          const lastTime = series.length ? series[series.length - 1].time : -Infinity;
          const point: ChartPoint = {
            time: now <= lastTime ? lastTime + 1 : now,
            value,
          };
          const updated = [...series, point];
          if (updated.length > HISTORY_LIMIT) {
            updated.shift();
          }
          next[symbol] = updated;
        });
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
              const hasNewTick = payload.tick !== lastTickRef.current;
              if (hasNewTick && !payload.latest_transaction) {
                appendPriceSnapshot(payload.data);
              }
              if (hasNewTick) {
                lastTickRef.current = payload.tick;
              }
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
          <div className="glass-panel h-[360px] overflow-hidden rounded-[2.5rem] p-8 md:h-[420px]">
            <RealtimeChart key={activeSymbol} seriesData={activeSeries} symbol={activeSymbol} />
          </div>
          <div className="glass-panel max-h-[400px] rounded-[2.5rem] p-8 overflow-y-auto">
            <AgentRoster agents={agents} />
          </div>
        </section>

        {/* Right Column: Controls & Headlines */}
        <section className="flex flex-col gap-6">
          <div className="glass-panel rounded-[2.5rem] p-6 bg-gradient-to-br from-primary/10 to-transparent">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-[10px] uppercase tracking-widest text-white/40">Simulation Controls</p>
                <p className="text-lg font-display font-bold text-white">Control Deck</p>
              </div>
              <div className="text-xs text-white/50">
                Status: <span className={simRunning ? "text-primary" : "text-accent"}>{simRunning ? "Running" : "Idle"}</span>
              </div>
            </div>

            <div className="mt-4 grid grid-cols-2 gap-3 text-xs text-white/70">
              <label className="flex flex-col gap-1">
                Max Ticks
                <input
                  type="number"
                  value={simConfig.max_ticks}
                  disabled={simRunning}
                  onChange={(event) => setSimConfig(prev => ({ ...prev, max_ticks: Number(event.target.value) }))}
                  className={CONTROL_INPUT_CLASSES}
                />
              </label>
              <label className="flex flex-col gap-1">
                Tick Duration (s)
                <input
                  type="number"
                  step="0.1"
                  value={simConfig.tick_duration}
                  disabled={simRunning}
                  onChange={(event) => setSimConfig(prev => ({ ...prev, tick_duration: Number(event.target.value) }))}
                  className={CONTROL_INPUT_CLASSES}
                />
              </label>
              <label className="flex flex-col gap-1">
                Agent Count
                <input
                  type="number"
                  value={simConfig.agent_count}
                  disabled={simRunning}
                  onChange={(event) => setSimConfig(prev => ({ ...prev, agent_count: Number(event.target.value) }))}
                  className={CONTROL_INPUT_CLASSES}
                />
              </label>
              <label className="flex flex-col gap-1">
                Checkpoint Every
                <input
                  type="number"
                  value={simConfig.checkpoint_every}
                  disabled={simRunning}
                  onChange={(event) => setSimConfig(prev => ({ ...prev, checkpoint_every: Number(event.target.value) }))}
                  className={CONTROL_INPUT_CLASSES}
                />
              </label>
              <label className="flex flex-col gap-1">
                Initial Price
                <input
                  type="number"
                  step="0.0001"
                  value={simConfig.initial_price}
                  disabled={simRunning}
                  onChange={(event) => setSimConfig(prev => ({ ...prev, initial_price: Number(event.target.value) }))}
                  className={CONTROL_INPUT_CLASSES}
                />
              </label>
              <label className="flex flex-col gap-1">
                Seed Inventory
                <input
                  type="number"
                  value={simConfig.seed_inventory}
                  disabled={simRunning}
                  onChange={(event) => setSimConfig(prev => ({ ...prev, seed_inventory: Number(event.target.value) }))}
                  className={CONTROL_INPUT_CLASSES}
                />
              </label>
            </div>

            <div className="mt-4 grid grid-cols-2 gap-3 text-xs text-white/70">
              <label className="flex flex-col gap-1">
                Report Dir
                <input
                  type="text"
                  value={simConfig.report_dir}
                  disabled={simRunning}
                  onChange={(event) => setSimConfig(prev => ({ ...prev, report_dir: event.target.value }))}
                  className={CONTROL_INPUT_CLASSES}
                />
              </label>
              <label className="flex flex-col gap-1">
                Checkpoint Dir
                <input
                  type="text"
                  value={simConfig.checkpoint_dir}
                  disabled={simRunning}
                  onChange={(event) => setSimConfig(prev => ({ ...prev, checkpoint_dir: event.target.value }))}
                  className={CONTROL_INPUT_CLASSES}
                />
              </label>
            </div>

            <div className="mt-4 flex items-center gap-3">
              <button
                onClick={startSimulation}
                disabled={simRunning}
                className={CONTROL_BUTTON_PRIMARY_CLASSES}
              >
                Start Simulation
              </button>
              <button
                onClick={stopSimulation}
                disabled={!simRunning}
                className={CONTROL_BUTTON_SECONDARY_CLASSES}
              >
                Stop Simulation
              </button>
              <div className="text-[10px] text-white/40">
                {simSummary?.run_id ? `Run: ${simSummary.run_id}` : "No run yet"}
              </div>
            </div>

            <div className="mt-4 rounded-2xl border border-white/10 bg-black/20 p-3 text-[10px] text-white/60">
              <div className="flex justify-between">
                <span>Total Trades</span>
                <span className="text-white/90">{simSummary?.total_trades ?? 0}</span>
              </div>
              <div className="flex justify-between">
                <span>Avg / Min / Max</span>
                <span className="text-white/90">
                  {simSummary?.avg_price?.toFixed(4) ?? "n/a"} / {simSummary?.min_price?.toFixed(4) ?? "n/a"} / {simSummary?.max_price?.toFixed(4) ?? "n/a"}
                </span>
              </div>
              <div className="flex justify-between">
                <span>Negotiations</span>
                <span className="text-white/90">{simSummary?.negotiation_count ?? 0}</span>
              </div>
              <div className="flex justify-between">
                <span>Report</span>
                <span className="text-white/90">{simReportDir ?? simSummary?.report_dir ?? "n/a"}</span>
              </div>
            </div>
          </div>

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
