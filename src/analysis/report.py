"""
Post-run report generation for marketplace simulations.
"""

from __future__ import annotations

import argparse
import json
import math
import os
from collections.abc import Iterable
from datetime import UTC, datetime
from typing import Any

import pandas as pd

from src.analysis.chart import generate_agent_performance_chart, generate_market_summary_plot
from src.market.ledger import Ledger


def _to_dataframe(items: Iterable[Any]) -> pd.DataFrame:
    """
    Convert a list of SQLModel/Pydantic objects into a DataFrame.
    """
    # Context7 /websites/pydantic_dev (BaseModel model_dump).
    data = [item.model_dump(mode="json") for item in items]
    # Context7 /websites/pandas_pydata (DataFrame intro).
    return pd.DataFrame(data)


def _format_optional_float(value: float | None, decimals: int = 6) -> str:
    """Format optional floats safely for report output."""
    if value is None or not math.isfinite(value):
        return "n/a"
    return f"{value:.{decimals}f}"


def _format_price(value: float | None) -> str:
    """Format optional prices with currency when available."""
    formatted = _format_optional_float(value)
    return f"{formatted} BTC" if formatted != "n/a" else "n/a"


def _markdown_table(df: pd.DataFrame, columns: list[str]) -> str:
    """Render a DataFrame subset as a Markdown table without pandas extras."""
    if df.empty:
        return "No data."
    subset = df[columns].fillna("")
    headers = " | ".join(columns)
    divider = " | ".join(["---"] * len(columns))
    rows = [" | ".join(str(value) for value in row) for row in subset.values.tolist()]
    return "\n".join([headers, divider, *rows])


def _build_agent_summary(agents: Iterable[Any], current_prices: dict[str, float]) -> pd.DataFrame:
    """Compute per-agent portfolio metrics at the end of a run."""
    rows = []
    for agent in agents:
        metrics = agent.portfolio.get_metrics(current_prices)
        rows.append(
            {
                "agent_id": agent.id,
                "persona": agent.persona,
                "model": getattr(agent, "model_name", None),
                "cash": metrics["cash"],
                "portfolio_value": metrics["portfolio_value"],
                "total_pnl": metrics["total_pnl"],
                "roi": metrics["roi"],
                "trades_count": metrics["trades_count"],
            }
        )
    # Context7 /websites/pandas_pydata (DataFrame intro).
    df = pd.DataFrame(rows)
    if not df.empty:
        # Context7 /websites/pandas_pydata (sort_values basics).
        df = df.sort_values(by="roi", ascending=False)
    return df


def _build_trade_activity(tx_df: pd.DataFrame) -> pd.DataFrame:
    """Aggregate trade counts per agent from transaction data."""
    if tx_df.empty:
        return pd.DataFrame(columns=["agent_id", "trade_count"])
    buyers = tx_df["buyer_id"].value_counts().rename("trade_count")
    sellers = tx_df["seller_id"].value_counts().rename("trade_count")
    combined = buyers.add(sellers, fill_value=0).reset_index()
    combined.columns = ["agent_id", "trade_count"]
    return combined.sort_values(by="trade_count", ascending=False)


def _build_action_activity(interactions_df: pd.DataFrame) -> pd.DataFrame:
    """Aggregate action counts per agent from interaction logs."""
    if interactions_df.empty:
        return pd.DataFrame(columns=["agent_id", "action_count"])
    actions = interactions_df[interactions_df["kind"] == "action"]
    if actions.empty:
        return pd.DataFrame(columns=["agent_id", "action_count"])
    counts = actions["agent_id"].value_counts().reset_index()
    counts.columns = ["agent_id", "action_count"]
    return counts


def _summarize_market(tx_df: pd.DataFrame) -> dict:
    """Summarize market-level stats from transaction data."""
    if tx_df.empty:
        return {
            "total_trades": 0,
            "avg_price": None,
            "min_price": None,
            "max_price": None,
            "volatility": None,
        }
    return {
        "total_trades": int(tx_df.shape[0]),
        "avg_price": float(tx_df["price"].mean()),
        "min_price": float(tx_df["price"].min()),
        "max_price": float(tx_df["price"].max()),
        "volatility": float(tx_df["price"].std()),
    }


def _ensure_dir(path: str) -> None:
    """Create output directory if it does not exist."""
    # Context7 /python/cpython (os.makedirs docs).
    os.makedirs(path, exist_ok=True)


def generate_report(
    run_id: str,
    db_path: str,
    report_root: str,
    agents: Iterable[Any],
    current_prices: dict[str, float],
) -> str:
    """
    Generate a report for a single run. Returns report directory path.
    """
    report_dir = os.path.join(report_root, run_id)
    _ensure_dir(report_dir)

    ledger = Ledger(db_path)
    transactions = ledger.get_transactions_for_run(run_id)
    interactions = ledger.get_interactions_for_run(run_id)

    tx_df = _to_dataframe(transactions)
    interactions_df = _to_dataframe(interactions)

    agent_df = _build_agent_summary(agents, current_prices)
    trade_activity_df = _build_trade_activity(tx_df)
    action_activity_df = _build_action_activity(interactions_df)
    market_summary = _summarize_market(tx_df)

    plot_paths: dict[str, str] = {}
    if not tx_df.empty:
        price_plots = generate_market_summary_plot(tx_df, report_dir)
        for key, path in price_plots.items():
            plot_paths[key] = os.path.relpath(path, report_root)

    if not agent_df.empty:
        roi_path = generate_agent_performance_chart(
            agent_df,
            os.path.join(report_dir, "agent_roi.png"),
        )
        if roi_path:
            plot_paths["agent_roi"] = os.path.relpath(roi_path, report_root)

    top_agent = agent_df.iloc[0]["agent_id"] if not agent_df.empty else None
    top_roi = float(agent_df.iloc[0]["roi"]) if not agent_df.empty else None

    report_lines = []
    report_lines.append(f"# Run Report: {run_id}")
    report_lines.append("")
    report_lines.append("## Market Summary")
    report_lines.append("")
    report_lines.append(f"- Total trades: {market_summary['total_trades']}")
    report_lines.append(f"- Avg price: {_format_price(market_summary['avg_price'])}")
    report_lines.append(f"- Min price: {_format_price(market_summary['min_price'])}")
    report_lines.append(f"- Max price: {_format_price(market_summary['max_price'])}")
    if top_agent and top_roi is not None and math.isfinite(top_roi):
        top_agent_label = f"{top_agent} (ROI {_format_optional_float(top_roi, 1)}%)"
    elif top_agent:
        top_agent_label = top_agent
    else:
        top_agent_label = "n/a"
    report_lines.append(f"- Top agent: {top_agent_label}")
    report_lines.append("")

    if plot_paths.get("all_assets"):
        report_lines.append("## Price History")
        report_lines.append("")
        report_lines.append(f"![Price History]({plot_paths['all_assets']})")
        report_lines.append("")

    asset_plots = {
        key: path for key, path in plot_paths.items() if key not in {"all_assets", "agent_roi"}
    }
    if asset_plots:
        report_lines.append("## Per-Asset Price History")
        report_lines.append("")
        for asset in sorted(asset_plots):
            report_lines.append(f"### {asset}")
            report_lines.append(f"![{asset} Price]({asset_plots[asset]})")
            report_lines.append("")

    if not agent_df.empty:
        report_lines.append("## Agent Performance")
        report_lines.append("")
        report_lines.append(
            _markdown_table(
                agent_df,
                [
                    "agent_id",
                    "persona",
                    "model",
                    "cash",
                    "portfolio_value",
                    "total_pnl",
                    "roi",
                    "trades_count",
                ],
            )
        )
        report_lines.append("")

    if plot_paths.get("agent_roi"):
        report_lines.append("![Agent ROI]({})".format(plot_paths["agent_roi"]))
        report_lines.append("")

    if not trade_activity_df.empty:
        report_lines.append("## Trade Activity")
        report_lines.append("")
        report_lines.append(_markdown_table(trade_activity_df, ["agent_id", "trade_count"]))
        report_lines.append("")

    if not action_activity_df.empty:
        report_lines.append("## Action Activity")
        report_lines.append("")
        report_lines.append(_markdown_table(action_activity_df, ["agent_id", "action_count"]))
        report_lines.append("")

    if not interactions_df.empty:
        negotiation_count = int(interactions_df[interactions_df["kind"] == "negotiation"].shape[0])
        report_lines.append("## Negotiation Activity")
        report_lines.append("")
        report_lines.append(f"- Negotiation events: {negotiation_count}")
        report_lines.append("")

    report_path = os.path.join(report_dir, "report.md")
    with open(report_path, "w", encoding="utf-8") as handle:
        handle.write("\n".join(report_lines))

    summary = {
        "run_id": run_id,
        # Context7 /python/cpython (datetime docs).
        "generated_at": datetime.now(UTC).isoformat(),
        "total_trades": market_summary["total_trades"],
        "top_agent": top_agent,
        "top_roi": top_roi,
        "report_path": os.path.relpath(report_path, report_root),
    }
    _update_index(report_root, summary)
    return report_dir


def _update_index(report_root: str, summary: dict) -> None:
    """Update JSON and Markdown indices for report summaries."""
    index_json = os.path.join(report_root, "index.json")
    entries = []
    if os.path.exists(index_json):
        with open(index_json, encoding="utf-8") as handle:
            entries = json.load(handle)
    entries = [e for e in entries if e.get("run_id") != summary["run_id"]]
    entries.append(summary)
    entries.sort(key=lambda x: x.get("run_id", ""), reverse=True)
    with open(index_json, "w", encoding="utf-8") as handle:
        # Context7 /python/cpython (json docs).
        json.dump(entries, handle, indent=2, sort_keys=True)

    index_lines = ["# Reports Index", ""]
    if entries:
        # Context7 /websites/pandas_pydata (DataFrame intro).
        df = pd.DataFrame(entries)
        index_lines.append(
            _markdown_table(
                df,
                ["run_id", "total_trades", "top_agent", "top_roi", "report_path"],
            )
        )
    else:
        index_lines.append("No reports found.")

    index_md = os.path.join(report_root, "index.md")
    with open(index_md, "w", encoding="utf-8") as handle:
        handle.write("\n".join(index_lines))


def parse_args():
    """Parse CLI args for report generation."""
    parser = argparse.ArgumentParser(
        description="Generate a post-run report",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )  # Context7 /python/cpython (argparse docs).
    parser.add_argument("--run-id", required=True, help="Simulation run identifier")
    parser.add_argument("--db-path", default="market.db", help="SQLite DB path")
    parser.add_argument("--report-root", default="reports", help="Reports directory")
    return parser.parse_args()


def main():
    """CLI entry point for manual report generation."""
    args = parse_args()
    generate_report(args.run_id, args.db_path, args.report_root, agents=[], current_prices={})


if __name__ == "__main__":
    main()
