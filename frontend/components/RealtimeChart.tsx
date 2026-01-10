"use client";

import { useEffect, useRef } from "react";
import {
  createChart,
  AreaSeries,
  type IChartApi,
  type ISeriesApi,
  type LineData,
  type UTCTimestamp,
  ColorType,
  CrosshairMode,
} from "lightweight-charts";

type RealtimeChartProps = {
  latestPoint: LineData | null;
  symbol: string;
};

export default function RealtimeChart({ latestPoint, symbol }: RealtimeChartProps) {
  const containerRef = useRef<HTMLDivElement | null>(null);
  const chartRef = useRef<IChartApi | null>(null);
  const seriesRef = useRef<ISeriesApi<"Area"> | null>(null);

  useEffect(() => {
    if (!containerRef.current) return;

    const chart = createChart(containerRef.current, {
      layout: {
        background: { type: ColorType.Solid, color: "transparent" },
        textColor: "rgba(255, 255, 255, 0.5)",
        fontFamily: "'Inter', sans-serif",
      },
      grid: {
        vertLines: { color: "rgba(255, 255, 255, 0.03)" },
        horzLines: { color: "rgba(255, 255, 255, 0.03)" },
      },
      rightPriceScale: {
        borderColor: "rgba(255, 255, 255, 0.1)",
        visible: true,
      },
      timeScale: {
        borderColor: "rgba(255, 255, 255, 0.1)",
        timeVisible: true,
        secondsVisible: true,
      },
      crosshair: {
        mode: CrosshairMode.Normal,
        vertLine: {
          color: "#0EA5E9",
          width: 1,
          style: 2,
        },
        horzLine: {
          color: "#0EA5E9",
          width: 1,
          style: 2,
        },
      },
      handleScale: {
        axisPressedMouseMove: true,
      },
      width: containerRef.current.clientWidth,
      height: 400,
    });

    const areaSeries = chart.addSeries(AreaSeries, {
      lineColor: "#0EA5E9",
      topColor: "rgba(14, 165, 233, 0.3)",
      bottomColor: "rgba(14, 165, 233, 0.02)",
      lineWidth: 3,
    });

    chartRef.current = chart;
    seriesRef.current = areaSeries;

    const resizeObserver = new ResizeObserver((entries) => {
      for (const entry of entries) {
        if (!chartRef.current) return;
        chartRef.current.applyOptions({
          width: entry.contentRect.width,
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
  }, [latestPoint]);

  return (
    <div className="flex h-full flex-col gap-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="rounded-lg bg-secondary/10 px-2 py-1 text-xs font-bold text-secondary border border-secondary/20">
            {symbol} / BTC
          </div>
          <h2 className="font-display text-2xl font-semibold text-white">Market Activity</h2>
        </div>
        <div className="flex gap-2">
          {['1m', '5m', '15m', '1h', 'D'].map(t => (
            <button key={t} className="px-2 py-1 text-[10px] font-bold text-white/40 hover:text-white transition-colors">{t}</button>
          ))}
        </div>
      </div>
      <div className="relative flex-1 min-h-[400px]">
        <div ref={containerRef} className="absolute inset-0" />
      </div>
    </div>
  );
}
