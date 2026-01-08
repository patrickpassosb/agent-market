"""
Post-run report generation for marketplace simulations.
"""

from __future__ import annotations

from typing import Any, Iterable, Optional
import argparse
import json
import os
from datetime import datetime, timezone

import pandas as pd
import matplotlib.pyplot as plt
from sqlmodel import Session, create_engine, select

from src.market.schema import Transaction, InteractionLog, DEFAULT_ITEM


def _to_dataframe(items: Iterable[Any]) -> pd.DataFrame:
    """
    Convert a list of SQLModel/Pydantic objects into a DataFrame.
    """
    data = [item.model_dump(mode="json") for item in items]  # https://docs.pydantic.dev/latest/api/base_model (Context7 /websites/pydantic_dev)
    return pd.DataFrame(data)  # https://pandas.pydata.org/docs/user_guide/dsintro (Context7 /websites/pandas_pydata)


def _load_transactions(db_path: str, run_id: Optional[str]) -> list[Transaction]:
    engine = create_engine(f"sqlite:///{db_path}")
    with Session(engine) as session:
        statement = select(Transaction)
        if run_id:
            statement = statement.where(Transaction.run_id == run_id)
        statement = statement.order_by(Transaction.timestamp.asc())
        return list(session.exec(statement).all())


def _load_interactions(db_path: str, run_id: Optional[str]) -> list[InteractionLog]:
    engine = create_engine(f"sqlite:///{db_path}")
    with Session(engine) as session:
        statement = select(InteractionLog)
        if run_id:
            statement = statement.where(InteractionLog.run_id == run_id)
        statement = statement.order_by(InteractionLog.timestamp.asc())
        return list(session.exec(statement).all())


def _write_plot(path: str, fig) -> None:
    fig.savefig(path, dpi=200, bbox_inches="tight")  # https://github.com/matplotlib/matplotlib/blob/main/galleries/users_explain/figure/figure_intro.rst (Context7 /matplotlib/matplotlib)
    plt.close(fig)


def _markdown_table(df: pd.DataFrame, columns: list[str]) -> str:
    if df.empty:
        return "No data."
    subset = df[columns].fillna("")
    headers = " | ".join(columns)
    divider = " | ".join(["---"] * len(columns))
    rows = [" | ".join(str(value) for value in row) for row in subset.values.tolist()]
    return "\n".join([headers, divider, *rows])


def _build_agent_summary(agents: Iterable[Any], current_price: float) -> pd.DataFrame:
    rows = []
    for agent in agents:
        metrics = agent.portfolio.get_metrics({DEFAULT_ITEM: current_price})
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
    df = pd.DataFrame(rows)  # https://pandas.pydata.org/docs/user_guide/dsintro (Context7 /websites/pandas_pydata)
    if not df.empty:
        df = df.sort_values(by="roi", ascending=False)  # https://pandas.pydata.org/docs/dev/user_guide/basics (Context7 /websites/pandas_pydata)
    return df


def _build_trade_activity(tx_df: pd.DataFrame) -> pd.DataFrame:
    if tx_df.empty:
        return pd.DataFrame(columns=["agent_id", "trade_count"])
    buyers = tx_df["buyer_id"].value_counts().rename("trade_count")
    sellers = tx_df["seller_id"].value_counts().rename("trade_count")
    combined = buyers.add(sellers, fill_value=0).reset_index()
    combined.columns = ["agent_id", "trade_count"]
    return combined.sort_values(by="trade_count", ascending=False)


def _build_action_activity(interactions_df: pd.DataFrame) -> pd.DataFrame:
    if interactions_df.empty:
        return pd.DataFrame(columns=["agent_id", "action_count"])
    actions = interactions_df[interactions_df["kind"] == "action"]
    if actions.empty:
        return pd.DataFrame(columns=["agent_id", "action_count"])
    counts = actions["agent_id"].value_counts().reset_index()
    counts.columns = ["agent_id", "action_count"]
    return counts


def _summarize_market(tx_df: pd.DataFrame) -> dict:
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
    os.makedirs(path, exist_ok=True)  # https://github.com/python/cpython/blob/main/Doc/faq/library.rst (Context7 /python/cpython)


def generate_report(
    run_id: str,
    db_path: str,
    report_root: str,
    agents: Iterable[Any],
    current_price: float,
) -> str:
    """
    Generate a report for a single run. Returns report directory path.
    """
    report_dir = os.path.join(report_root, run_id)
    _ensure_dir(report_dir)

    transactions = _load_transactions(db_path, run_id)
    interactions = _load_interactions(db_path, run_id)

    tx_df = _to_dataframe(transactions)
    interactions_df = _to_dataframe(interactions)

    agent_df = _build_agent_summary(agents, current_price)
    trade_activity_df = _build_trade_activity(tx_df)
    action_activity_df = _build_action_activity(interactions_df)
    market_summary = _summarize_market(tx_df)

    plot_paths = {}
    if transactions:
        fig, ax = plt.subplots(figsize=(10, 4))
        times = [tx.timestamp for tx in transactions]
        prices = [tx.price for tx in transactions]
        ax.plot(times, prices, label="Trade Price")
        ax.set_title("Price Over Time")
        ax.set_xlabel("Time")
        ax.set_ylabel("Price")
        ax.grid(True, alpha=0.3)
        ax.legend(loc="upper left")
        price_path = os.path.join(report_dir, "price_history.png")
        _write_plot(price_path, fig)
        plot_paths["price_history"] = os.path.relpath(price_path, report_root)

    if not agent_df.empty:
        fig, ax = plt.subplots(figsize=(10, 4))
        ax.bar(agent_df["agent_id"], agent_df["roi"])
        ax.set_title("ROI by Agent")
        ax.set_xlabel("Agent")
        ax.set_ylabel("ROI (%)")
        ax.tick_params(axis="x", rotation=45)
        ax.grid(True, axis="y", alpha=0.3)
        roi_path = os.path.join(report_dir, "agent_roi.png")
        _write_plot(roi_path, fig)
        plot_paths["agent_roi"] = os.path.relpath(roi_path, report_root)

    top_agent = agent_df.iloc[0]["agent_id"] if not agent_df.empty else None
    top_roi = float(agent_df.iloc[0]["roi"]) if not agent_df.empty else None

    report_lines = []
    report_lines.append(f"# Run Report: {run_id}")
    report_lines.append("")
    report_lines.append("## Market Summary")
    report_lines.append("")
    report_lines.append(f"- Total trades: {market_summary['total_trades']}")
    report_lines.append(f"- Avg price: {market_summary['avg_price']}")
    report_lines.append(f"- Min price: {market_summary['min_price']}")
    report_lines.append(f"- Max price: {market_summary['max_price']}")
    report_lines.append(f"- Volatility (std): {market_summary['volatility']}")
    report_lines.append(f"- Top agent: {top_agent} (ROI {top_roi})")
    report_lines.append("")

    if plot_paths.get("price_history"):
        report_lines.append("## Price History")
        report_lines.append("")
        report_lines.append(f"![Price History]({plot_paths['price_history']})")
        report_lines.append("")

    if not agent_df.empty:
        report_lines.append("## Agent Performance")
        report_lines.append("")
        report_lines.append(
            _markdown_table(
                agent_df,
                ["agent_id", "persona", "model", "cash", "portfolio_value", "total_pnl", "roi", "trades_count"],
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
        "generated_at": datetime.now(timezone.utc).isoformat(),  # https://github.com/python/cpython/blob/main/Doc/library/datetime.rst (Context7 /python/cpython)
        "total_trades": market_summary["total_trades"],
        "top_agent": top_agent,
        "top_roi": top_roi,
        "report_path": os.path.relpath(report_path, report_root),
    }
    _update_index(report_root, summary)
    return report_dir


def _update_index(report_root: str, summary: dict) -> None:
    index_json = os.path.join(report_root, "index.json")
    entries = []
    if os.path.exists(index_json):
        with open(index_json, "r", encoding="utf-8") as handle:
            entries = json.load(handle)
    entries = [e for e in entries if e.get("run_id") != summary["run_id"]]
    entries.append(summary)
    entries.sort(key=lambda x: x.get("run_id", ""), reverse=True)
    with open(index_json, "w", encoding="utf-8") as handle:
        json.dump(entries, handle, indent=2, sort_keys=True)  # https://github.com/python/cpython/blob/main/Doc/library/json.rst (Context7 /python/cpython)

    index_lines = ["# Reports Index", ""]
    if entries:
        df = pd.DataFrame(entries)  # https://pandas.pydata.org/docs/user_guide/dsintro (Context7 /websites/pandas_pydata)
        index_lines.append(_markdown_table(df, ["run_id", "total_trades", "top_agent", "top_roi", "report_path"]))
    else:
        index_lines.append("No reports found.")

    index_md = os.path.join(report_root, "index.md")
    with open(index_md, "w", encoding="utf-8") as handle:
        handle.write("\n".join(index_lines))


def parse_args():
    parser = argparse.ArgumentParser(
        description="Generate a post-run report",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )  # https://github.com/python/cpython/blob/main/Doc/library/argparse.rst (Context7 /python/cpython)
    parser.add_argument("--run-id", required=True, help="Simulation run identifier")
    parser.add_argument("--db-path", default="market.db", help="SQLite DB path")
    parser.add_argument("--report-root", default="reports", help="Reports directory")
    return parser.parse_args()


def main():
    args = parse_args()
    generate_report(args.run_id, args.db_path, args.report_root, agents=[], current_price=0.0)


if __name__ == "__main__":
    main()
