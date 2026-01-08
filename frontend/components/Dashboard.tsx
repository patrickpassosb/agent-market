"use client";

import { useEffect, useMemo, useState } from "react";
import AgentFeed from "./AgentFeed";
import MarketWatch from "./MarketWatch";
import TerminalFeed from "./TerminalFeed";

type Ticker = "AAPL" | "TSLA" | "NVDA" | "MSFT";

type TickerMap = Record<Ticker, number>;

type AgentRecord = {
  id?: string | number;
  name?: string;
  role?: string;
  status?: string;
  last_action?: string;
  updated_at?: string;
  timestamp?: string;
  [key: string]: unknown;
};

type AgentFeedItem = {
  id: string;
  title: string;
  detail: string;
  time: string;
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

const pickTickers = (data: Record<string, unknown>): Partial<TickerMap> => {
  return TICKERS.reduce<Partial<TickerMap>>((acc, ticker) => {
    const value = data[ticker];
    if (typeof value === "number" && Number.isFinite(value)) {
      acc[ticker] = value;
    }
    return acc;
  }, {});
};

const normalizeAgentFeed = (agents: AgentRecord[]): AgentFeedItem[] => {
  return agents.map((agent, index) => {
    const title = agent.name ?? agent.role ?? `Agent ${index + 1}`;
    const detail =
      agent.last_action ??
      agent.status ??
      (typeof agent["action"] === "string" ? (agent["action"] as string) : "Active");
    const time =
      agent.updated_at ??
      agent.timestamp ??
      (typeof agent["last_seen"] === "string"
        ? (agent["last_seen"] as string)
        : "just now");
    const id = String(agent.id ?? `${title}-${index}`);
    return { id, title, detail, time };
  });
};

export default function Dashboard() {
  const [tickers, setTickers] = useState<TickerMap>(DEFAULT_TICKERS);
  const [previousTickers, setPreviousTickers] = useState<TickerMap>(DEFAULT_TICKERS);
  const [terminalLines, setTerminalLines] = useState<string[]>([]);
  const [agentFeed, setAgentFeed] = useState<AgentFeedItem[]>([]);
  const [status, setStatus] = useState<
    "connecting" | "live" | "reconnecting" | "error"
  >("connecting");
  const [lastUpdate, setLastUpdate] = useState<string | null>(null);

  const chartSymbol = useMemo(() => "AAPL", []);

  useEffect(() => {
    let ignore = false;

    const fetchInitial = async () => {
      try {
        const response = await fetch(`${API_BASE}/market/state`);
        if (!response.ok) return;
        const data = (await response.json()) as Record<string, unknown>;
        const payload =
          (data.tickers as Record<string, unknown>) ??
          (data.prices as Record<string, unknown>) ??
          (data.data as Record<string, unknown>) ??
          data;
        const next = pickTickers(payload ?? {});
        if (!ignore && Object.keys(next).length > 0) {
          setTickers((prev) => ({ ...prev, ...next }));
        }
      } catch (error) {
        console.warn("Failed to fetch market state", error);
      }

      try {
        const response = await fetch(`${API_BASE}/agents`);
        if (!response.ok) return;
        const data = (await response.json()) as AgentRecord[];
        if (!ignore && Array.isArray(data)) {
          setAgentFeed(normalizeAgentFeed(data));
        }
      } catch (error) {
        console.warn("Failed to fetch agents", error);
      }
    };

    fetchInitial();

    return () => {
      ignore = true;
    };
  }, []);

  useEffect(() => {
    // useEffect cleanup pattern per React docs (Context7 /websites/react_dev).
    let socket: WebSocket | null = null;
    let reconnectTimer: number | undefined;
    let isActive = true;

    const connect = () => {
      if (!isActive) return;
      setStatus((current) => (current === "live" ? "live" : "connecting"));
      socket = new WebSocket(WS_URL);

      socket.onopen = () => {
        setStatus("live");
      };

      socket.onmessage = (event) => {
        try {
          const payload = JSON.parse(event.data) as {
            type?: string;
            data?: Record<string, unknown>;
          };

          if (payload.type === "ticker" && payload.data) {
            const next = pickTickers(payload.data);
            if (Object.keys(next).length === 0) return;

            setTickers((prev) => {
              setPreviousTickers(prev);
              const merged = { ...prev, ...next };
              const value = merged[chartSymbol];
              const timestamp = new Date().toLocaleTimeString();
              const line = [
                `[${timestamp}]`,
                ...TICKERS.map((ticker) => `${ticker} ${merged[ticker].toFixed(4)}`),
              ].join(" ");
              setTerminalLines((lines) => [...lines.slice(-39), line]);
              setLastUpdate(timestamp);
              return merged;
            });
          }
        } catch (error) {
          console.warn("WebSocket message parse error", error);
        }
      };

      socket.onclose = () => {
        if (!isActive) return;
        setStatus("reconnecting");
        reconnectTimer = window.setTimeout(connect, 1500);
      };

      socket.onerror = () => {
        setStatus("error");
        socket?.close();
      };
    };

    connect();

    return () => {
      isActive = false;
      if (reconnectTimer) window.clearTimeout(reconnectTimer);
      socket?.close();
    };
  }, [chartSymbol]);

  return (
    <div className="min-h-screen bg-[radial-gradient(circle_at_top,_rgba(56,189,248,0.15),_transparent_55%),radial-gradient(circle_at_top_right,_rgba(16,185,129,0.2),_transparent_45%),radial-gradient(circle_at_bottom,_rgba(139,92,246,0.2),_transparent_55%)]">
      <div className="mx-auto flex min-h-screen max-w-6xl flex-col gap-8 px-6 py-10">
        <header className="flex flex-wrap items-center justify-between gap-6">
          <div>
            <p className="text-xs uppercase tracking-[0.4em] text-emerald-200/70">
              Agent Market
            </p>
            <h1 className="text-4xl font-semibold text-white">Terminal Live</h1>
            <p className="mt-2 max-w-xl text-sm text-white/60">
              Real-time simulation feed powered by WebSocket updates and agent
              activity.
            </p>
          </div>
          <div className="rounded-full border border-white/10 bg-white/10 px-4 py-2 text-xs text-white/70">
            {API_BASE}
          </div>
        </header>

        <div className="grid gap-6 lg:grid-cols-[1.1fr_1.9fr]">
          <div className="rounded-3xl border border-white/10 bg-white/10 p-6 backdrop-blur-2xl">
            <MarketWatch
              tickers={tickers}
              previous={previousTickers}
              status={status}
              lastUpdate={lastUpdate}
            />
          </div>
          <div className="rounded-3xl border border-white/10 bg-white/10 p-6 backdrop-blur-2xl">
            <TerminalFeed lines={terminalLines} title={`${chartSymbol} Live Feed`} />
          </div>
        </div>

        <div className="rounded-3xl border border-white/10 bg-white/10 p-6 backdrop-blur-2xl">
          <AgentFeed items={agentFeed} />
        </div>
      </div>
    </div>
  );
}
