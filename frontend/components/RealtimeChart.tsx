"use client";

import { useEffect, useRef } from "react";
import {
  createChart,
  LineSeries,
  type IChartApi,
  type ISeriesApi,
  type LineData,
  type UTCTimestamp,
} from "lightweight-charts";

type RealtimeChartProps = {
  latestPoint: LineData | null;
  symbol: string;
};

export default function RealtimeChart({ latestPoint, symbol }: RealtimeChartProps) {
  const containerRef = useRef<HTMLDivElement | null>(null);
  const chartRef = useRef<IChartApi | null>(null);
  const seriesRef = useRef<ISeriesApi<"Line"> | null>(null);

  useEffect(() => {
    if (!containerRef.current) return;

    // Chart setup per Context7 docs: /tradingview/lightweight-charts (v5 addSeries).
    const chart = createChart(containerRef.current, {
      layout: {
        background: { type: "solid", color: "rgba(8, 12, 24, 0.6)" },
        textColor: "#d1fae5",
      },
      grid: {
        vertLines: { color: "rgba(148, 163, 184, 0.1)" },
        horzLines: { color: "rgba(148, 163, 184, 0.1)" },
      },
      rightPriceScale: {
        borderColor: "rgba(148, 163, 184, 0.2)",
      },
      timeScale: {
        borderColor: "rgba(148, 163, 184, 0.2)",
        timeVisible: true,
        secondsVisible: true,
      },
      crosshair: {
        vertLine: { color: "rgba(59, 130, 246, 0.4)" },
        horzLine: { color: "rgba(59, 130, 246, 0.4)" },
      },
      width: containerRef.current.clientWidth,
      height: 320,
    });

    const lineSeries = chart.addSeries(LineSeries, {
      color: "#38bdf8",
      lineWidth: 2,
    });

    chartRef.current = chart;
    seriesRef.current = lineSeries;

    const resizeObserver = new ResizeObserver((entries) => {
      for (const entry of entries) {
        if (!chartRef.current) return;
        chartRef.current.applyOptions({
          width: entry.contentRect.width,
          height: entry.contentRect.height,
        });
      }
    });

    resizeObserver.observe(containerRef.current);

    return () => {
      resizeObserver.disconnect();
      chart.remove();
      chartRef.current = null;
      seriesRef.current = null;
    };
  }, []);

  useEffect(() => {
    if (!latestPoint || !seriesRef.current) return;
    seriesRef.current.update({
      time: latestPoint.time as UTCTimestamp,
      value: latestPoint.value,
    });
    chartRef.current?.timeScale().fitContent();
  }, [latestPoint]);

  return (
    <section className="flex h-full flex-col gap-4">
      <div>
        <p className="text-xs uppercase tracking-[0.3em] text-sky-200/70">
          Real-time Chart
        </p>
        <h2 className="text-2xl font-semibold text-white">{symbol} in BTC</h2>
      </div>
      <div className="relative flex-1 overflow-hidden rounded-2xl border border-white/10 bg-white/5 p-4 shadow-[0_0_60px_-30px_rgba(56,189,248,0.7)]">
        <div ref={containerRef} className="h-full w-full" />
      </div>
    </section>
  );
}
