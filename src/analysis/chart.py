"""
Market Analysis and Visualization.

This module queries the ledger and generates visual evidence of simulation runs.
"""

from __future__ import annotations

import os
from collections.abc import Iterable

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

from src.market.ledger import Ledger
from src.market.schema import QUOTE_CURRENCY


def _to_dataframe(items: Iterable[object]) -> pd.DataFrame:
    """Convert SQLModel/Pydantic objects into a DataFrame."""
    data = [item.model_dump(mode="json") for item in items]
    return pd.DataFrame(data)


def _ensure_dir(path: str) -> None:
    """Create output directory if it does not exist."""
    os.makedirs(path, exist_ok=True)


def generate_market_summary_plot(tx_df: pd.DataFrame, output_dir: str) -> dict[str, str]:
    """Create price history plots for all assets."""
    if tx_df.empty:
        return {}

    _ensure_dir(output_dir)
    if "timestamp" in tx_df.columns:
        tx_df["timestamp"] = pd.to_datetime(tx_df["timestamp"], utc=True, errors="coerce")
        tx_df = tx_df.sort_values(by="timestamp")

    plots: dict[str, str] = {}

    fig, ax = plt.subplots(figsize=(12, 6))
    # Context7 /mwaskom/seaborn (lineplot docs).
    sns.lineplot(
        data=tx_df,
        x="timestamp",
        y="price",
        hue="item",
        ax=ax,
    )
    ax.set_title("Price History by Asset")
    ax.set_xlabel("Time")
    ax.set_ylabel(f"Price ({QUOTE_CURRENCY})")
    ax.grid(True, alpha=0.3)
    combined_path = os.path.join(output_dir, "price_history.png")
    # Context7 /matplotlib/matplotlib (figure intro docs).
    fig.savefig(combined_path, dpi=200, bbox_inches="tight")
    plt.close(fig)
    plots["all_assets"] = combined_path

    for asset in sorted(tx_df["item"].dropna().unique()):
        asset_df = tx_df[tx_df["item"] == asset]
        if asset_df.empty:
            continue
        fig, ax = plt.subplots(figsize=(10, 4))
        # Context7 /mwaskom/seaborn (lineplot docs).
        sns.lineplot(
            data=asset_df,
            x="timestamp",
            y="price",
            ax=ax,
        )
        ax.set_title(f"Price History: {asset}")
        ax.set_xlabel("Time")
        ax.set_ylabel(f"Price ({QUOTE_CURRENCY})")
        ax.grid(True, alpha=0.3)
        asset_path = os.path.join(output_dir, f"price_history_{asset}.png")
        # Context7 /matplotlib/matplotlib (figure intro docs).
        fig.savefig(asset_path, dpi=200, bbox_inches="tight")
        plt.close(fig)
        plots[asset] = asset_path

    return plots


def generate_agent_performance_chart(agent_df: pd.DataFrame, output_path: str) -> str | None:
    """Create an ROI ranking chart for agents."""
    if agent_df.empty:
        return None

    fig, ax = plt.subplots(figsize=(10, 4))
    # Context7 /mwaskom/seaborn (barplot docs).
    sns.barplot(
        data=agent_df,
        x="agent_id",
        y="roi",
        ax=ax,
    )
    ax.set_title("ROI by Agent")
    ax.set_xlabel("Agent")
    ax.set_ylabel("ROI (%)")
    ax.tick_params(axis="x", rotation=45)
    ax.grid(True, axis="y", alpha=0.3)
    # Context7 /matplotlib/matplotlib (figure intro docs).
    fig.savefig(output_path, dpi=200, bbox_inches="tight")
    plt.close(fig)
    return output_path


def _generate_agent_activity_chart(tx_df: pd.DataFrame, output_path: str) -> str | None:
    """Create a trade count chart from transaction data."""
    if tx_df.empty:
        return None

    agent_counts = (
        tx_df["buyer_id"].value_counts().add(tx_df["seller_id"].value_counts(), fill_value=0)
    )
    agent_df = agent_counts.rename("trade_count").reset_index()
    agent_df.columns = ["agent_id", "trade_count"]
    agent_df = agent_df.sort_values(by="trade_count", ascending=False)

    fig, ax = plt.subplots(figsize=(10, 4))
    # Context7 /mwaskom/seaborn (barplot docs).
    sns.barplot(
        data=agent_df,
        x="agent_id",
        y="trade_count",
        ax=ax,
    )
    ax.set_title("Trading Activity by Agent")
    ax.set_xlabel("Agent")
    ax.set_ylabel("Total Transactions")
    ax.tick_params(axis="x", rotation=45)
    ax.grid(True, axis="y", alpha=0.3)
    # Context7 /matplotlib/matplotlib (figure intro docs).
    fig.savefig(output_path, dpi=200, bbox_inches="tight")
    plt.close(fig)
    return output_path


def plot_market_history(
    db_path: str = "market.db",
    output_dir: str = "plots",
    run_id: str | None = None,
):
    """Reads the ledger and generates market analysis plots."""
    if not os.path.exists(db_path):
        print(f"Database {db_path} not found.")
        return

    ledger = Ledger(db_path)
    transactions = ledger.get_transactions_for_run(run_id)
    tx_df = _to_dataframe(transactions)

    if tx_df.empty:
        print("No transactions found in database.")
        return

    _ensure_dir(output_dir)
    plots = generate_market_summary_plot(tx_df, output_dir)
    activity_path = _generate_agent_activity_chart(
        tx_df,
        os.path.join(output_dir, "agent_activity.png"),
    )

    if plots:
        print(f"Saved {plots.get('all_assets')}")
    if activity_path:
        print(f"Saved {activity_path}")


if __name__ == "__main__":
    plot_market_history()
