"use client";

import { UserCircleIcon } from "@heroicons/react/24/outline";

/**
 * AgentRoster renders the list of active agents with their persona, model, and ROI.
 * It is used exclusively within the premium dashboard layout to surface realtime behavior.
 */

type AgentItem = {
    id: string;
    persona: string;
    model: string;
    portfolio?: {
        total_value: number;
        pnl: number;
        pnl_percent: number;
        roi: number;
    };
    last_action?: string;
};

export default function AgentRoster({ agents }: { agents: AgentItem[] }) {
    return (
        <section className="flex flex-col gap-6">
            <div className="flex items-center justify-between">
                <div>
                    <p className="text-xs uppercase tracking-[0.3em] text-primary/70">
                        Agent Roster
                    </p>
                    <h2 className="font-display text-2xl font-semibold text-white">Active Entities</h2>
                </div>
                <div className="rounded-full bg-primary/10 px-3 py-1 text-xs font-medium text-primary border border-primary/20">
                    {agents.length} Online
                </div>
            </div>

            <div className="grid items-stretch gap-4 sm:grid-cols-2 lg:grid-cols-4">
                {agents.map((agent) => (
                    <div
                        key={agent.id}
                        className="glass-card group flex h-full min-h-[280px] flex-col gap-4 p-5"
                    >
                        <div className="flex items-start justify-between">
                            <div className="flex items-center gap-3">
                                <div className="rounded-2xl bg-secondary/10 p-2 text-secondary ring-1 ring-secondary/20 group-hover:ring-secondary/40 transition-all">
                                    <UserCircleIcon className="h-6 w-6" />
                                </div>
                                <div>
                                    <h3 className="font-medium text-white">{agent.id}</h3>
                                    <p className="text-[10px] font-mono font-bold text-secondary uppercase tracking-tighter">
                                        {agent.model.includes("/") ? agent.model.split("/")[1] : agent.model}
                                    </p>
                                </div>
                            </div>
                            {/* ROI badge uses primary/ accent palette to indicate positive/negative performance */}
                            <div
                                className={`rounded-lg px-2 py-1 text-[10px] font-bold uppercase tracking-wider ${(
                                    agent.portfolio?.pnl ?? 0
                                ) >= 0 ? "bg-primary/10 text-primary" : "bg-accent/10 text-accent"
                                    }`}
                            >
                                ROI {(agent.portfolio?.roi ?? 0).toFixed(2)}%
                            </div>
                        </div>

                        <div className="space-y-2">
                            <span className="block text-[9px] uppercase tracking-widest text-white/40">
                                Persona
                            </span>
                            {/* Context7 /websites/react_dev (JSX markup rendering). */}
                            <p className="text-xs text-white/80 leading-relaxed break-words h-20 overflow-y-auto pr-1">
                                {agent.persona}
                            </p>
                        </div>

                        <div className="mt-auto space-y-4">
                            <div className="space-y-1">
                                <p className="text-[10px] uppercase tracking-widest text-white/30">Total Value</p>
                                <p className="text-lg font-mono font-semibold text-white">
                                    {(agent.portfolio?.total_value ?? 0).toFixed(4)}{" "}
                                    <span className="text-xs text-white/40">BTC</span>
                                </p>
                            </div>

                            {/* Provide a lightweight activity hint, using placeholder text when idle */}
                            <div className="border-t border-white/5 pt-3">
                                <p className="text-[10px] text-white/40 italic truncate">
                                    {agent.last_action || "Waiting for market signal..."}
                                </p>
                            </div>
                        </div>
                    </div>
                ))}
            </div>
        </section>
    );
}
