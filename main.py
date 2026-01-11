"""Multi-Agent Marketplace Simulation - Entry Point.

This script orchestrates the entire market simulation. It:
1. Initializes a MarketEngine (orderbook + ledger).
2. Creates multiple trading agents with diverse personas and LLMs.
3. Runs an asynchronous simulation loop where agents observe, decide, and act.
4. Displays live updates using the Rich library for a dynamic terminal UI.

Usage:
    python main.py

Stop the simulation with Ctrl+C (SIGINT). The script will handle graceful shutdown.
"""

import argparse
import asyncio
import logging
import math
import os
import random
from collections import deque
from collections.abc import Iterable
from datetime import datetime

import litellm
from dotenv import load_dotenv
from rich.console import Console
from rich.layout import Layout
from rich.live import Live
from rich.panel import Panel
from rich.table import Table

# Suppress LiteLLM verbose logging completely
litellm.set_verbose = False
os.environ["LITELLM_LOG"] = "CRITICAL"  # Only critical errors
logging.getLogger("LiteLLM").setLevel(logging.CRITICAL)
logging.getLogger("litellm").setLevel(logging.CRITICAL)

from src.agents.trader import Trader
from src.analysis.report import generate_report
from src.market.engine import MarketEngine
from src.market.schema import (
    QUOTE_CURRENCY,
    SUPPORTED_ASSETS,
    ActionLog,
    AgentAction,
    InteractionLog,
)
from src.utils.checkpoints import build_checkpoint, write_checkpoint
from src.utils.personas import PersonaStrategy, get_model_for_persona

# --- Configuration ---

# Load environment variables from .env file
load_dotenv()

# Simulation Parameters

NUM_AGENTS = 12       # Number of agents to spawn
Tick_Duration = 2.0   # Minimum duration of a simulation tick (seconds)

console = Console()

# --- UI / Layout Functions ---

def generate_layout() -> Layout:
    """
    Creates the main dashboard layout using Rich. 
    """
    layout = Layout()
    layout.split_column(
        Layout(name="header", size=3),
        Layout(name="news_flash", size=3),
        Layout(name="main", ratio=1),
        Layout(name="footer", size=3)
    )
    layout["main"].split_row(
        Layout(name="market_status", ratio=1),
        Layout(name="recent_activity", ratio=2)
    )
    return layout

def create_market_table(engine: MarketEngine) -> Panel:
    """
    Renders the Market Status panel. 
    """
    table = Table(title=f"Market Status ({QUOTE_CURRENCY})")
    table.add_column("Asset", style="bold yellow")
    table.add_column("Price", style="bold cyan")
    table.add_column("Spread", style="dim")
    table.add_column("Depth (B/A)", style="white")
    
    for asset in SUPPORTED_ASSETS:
        state = engine.get_state(asset)
        obs = state.order_book_summary
        
        # Calculate Spread
        bid = obs.get("best_bid")
        ask = obs.get("best_ask")
        spread = f"{(ask - bid):.5f}" if (bid and ask) else "-"
        
        # Format Price
        price_display = f"{state.current_price:.5f}"
        
        table.add_row(
            asset,
            price_display,
            spread,
            f"{obs.get('bids_count')}/{obs.get('asks_count')}"
        )
    
    return Panel(table, title="Live Ticker")

def create_activity_table(agents: list[Trader], recent_actions: Iterable[ActionLog]) -> Panel:
    """
    Renders the Agent Activity feed. 
    """
    table = Table(title="Agent Activity & Decisions")
    table.add_column("Agent / Model", style="white")
    table.add_column("Action", style="bold")
    table.add_column("Details", style="dim")
    
    # Create a quick lookup for agent models to display next to ID
    agent_models = {a.id: a.model_name for a in agents}

    for act in list(recent_actions)[-10:]: # Show last 10 actions only
        # Color coding for actions
        color = "green" if act.action == AgentAction.BUY else "red" if act.action == AgentAction.SELL else "yellow"
        
        # Format Model Name for concise display
        model_raw = agent_models.get(act.agent_id, "?")
        if "70b" in model_raw:
            model_display = "[bold cyan]Llama 70B[/]"
        elif "gemini" in model_raw:
            model_display = "[bold blue]Gemini[/]"
        elif "gpt" in model_raw:
            model_display = "[bold green]GPT-4o Mini[/]"
        else:
            model_display = "[dim]Llama 8B[/]"

        table.add_row(
            f"{act.agent_id} ({model_display})",
            f"[{color}]{act.action.value.upper()}[/{color}]",
            f"{act.reasoning} (@ {act.price:.5f})"
        )
    
    return Panel(table, title="Live Feed")

def _format_optional_float(value: float | None, decimals: int = 6) -> str:
    if value is None or not math.isfinite(value):
        return "n/a"
    return f"{value:.{decimals}f}"


def _build_run_summary(
    run_id: str,
    ticks: int,
    agents: list[Trader],
    transactions: list,
    current_prices: dict[str, float],
    report_dir: str | None,
    report_enabled: bool,
) -> dict[str, object]:
    prices = [tx.price for tx in transactions]
    avg_price = sum(prices) / len(prices) if prices else None
    min_price = min(prices) if prices else None
    max_price = max(prices) if prices else None

    agent_metrics = []
    for agent in agents:
        metrics = agent.portfolio.get_metrics(current_prices)
        agent_metrics.append((agent.id, metrics.get("roi")))
    agent_metrics.sort(
        key=lambda item: item[1] if item[1] is not None else float("-inf"),
        reverse=True,
    )

    top_agent = agent_metrics[0][0] if agent_metrics else None
    top_roi = agent_metrics[0][1] if agent_metrics else None
    report_path = os.path.join(report_dir, "report.md") if report_dir else None

    return {
        "run_id": run_id,
        "ticks": ticks,
        "total_trades": len(transactions),
        "avg_price": avg_price,
        "min_price": min_price,
        "max_price": max_price,
        "top_agent": top_agent,
        "top_roi": top_roi,
        "report_path": report_path,
        "report_enabled": report_enabled,
    }


def _render_run_summary(summary: dict[str, object]) -> None:
    table = Table(title="End of Simulation Summary")  # https://github.com/textualize/rich/blob/master/docs/source/tables.rst (Context7 /textualize/rich)
    table.add_column("Metric", style="bold")
    table.add_column("Value")
    table.add_row("Run ID", str(summary["run_id"]))
    table.add_row("Ticks", str(summary["ticks"]))
    table.add_row("Total trades", str(summary["total_trades"]))
    avg_price = summary.get("avg_price")
    min_price = summary.get("min_price")
    max_price = summary.get("max_price")
    table.add_row(
        "Avg price (BTC)",
        _format_optional_float(avg_price if isinstance(avg_price, (int, float)) else None),
    )
    table.add_row(
        "Min price (BTC)",
        _format_optional_float(min_price if isinstance(min_price, (int, float)) else None),
    )
    table.add_row(
        "Max price (BTC)",
        _format_optional_float(max_price if isinstance(max_price, (int, float)) else None),
    )

    top_agent = summary.get("top_agent")
    top_roi = summary.get("top_roi")
    if top_agent and top_roi is not None and isinstance(top_roi, (int, float)) and math.isfinite(top_roi):
        top_agent_label = f"{top_agent} (ROI {_format_optional_float(top_roi, 1)}%)"
    elif top_agent:
        top_agent_label = str(top_agent)
    else:
        top_agent_label = "n/a"
    table.add_row("Top agent", top_agent_label)

    report_path = summary.get("report_path")
    if report_path:
        report_label = str(report_path)
    else:
        report_label = "disabled" if summary.get("report_enabled") is False else "n/a"
    table.add_row("Report", report_label)

    console.print(table)

def parse_args():
    """
    Parse CLI args for bounded runs and checkpointing.
    """
    parser = argparse.ArgumentParser(
        description="Agent Market Simulation",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("--max-ticks", type=int, default=0, help="Stop after N ticks (0 = run indefinitely).")
    parser.add_argument("--checkpoint-every", type=int, default=0, help="Write a checkpoint every N ticks (0 = disabled).")
    parser.add_argument("--checkpoint-dir", type=str, default="checkpoints", help="Directory for checkpoint JSON files.")
    parser.add_argument("--checkpoint-transactions", type=int, default=50, help="Transactions to include in checkpoints.")
    parser.add_argument("--checkpoint-interactions", type=int, default=100, help="Interactions to include in checkpoints.")
    parser.add_argument("--initial-price", type=float, default=0.005, help="Seed price for the first tick (BTC).")
    parser.add_argument("--seed-inventory", type=int, default=10, help="Initial units assigned to each agent per asset.")
    parser.add_argument("--report-dir", type=str, default="reports", help="Directory for post-run reports.")
    parser.add_argument("--report", action="store_true", help="Generate post-run report on exit.")
    parser.add_argument("--no-report", action="store_true", help="Disable post-run report generation.")
    return parser.parse_args()


# --- Main Simulation Loop ---

async def main():
    """
    Run the simulation loop, wiring UI, agents, and reporting.
    """
    # 1. Setup & Initialization
    args = parse_args()
    
    # Ensure logs directory exists and setup logging
    os.makedirs("logs", exist_ok=True)
    run_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_filename = f"logs/simulation_{run_id}.log"
    
    # Configure global logging
    logging.basicConfig(
        filename=log_filename,
        level=logging.INFO,
        format='%(asctime)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    logging.info(f"Starting Agent Market Simulation | run_id={run_id}")

    # Initialize Market Engine
    engine = MarketEngine("market.db", run_id=run_id, initial_price=args.initial_price)
    agents: list[Trader] = []
    
    # Initialize Agents with random personas
    available_strategies = list(PersonaStrategy)
    for i in range(NUM_AGENTS):
        agent_id = f"Agent_{i+1}"
        strategy = random.choice(available_strategies)
        # Determine appropriate LLM for this persona
        model = get_model_for_persona(strategy.value)
        
        agent = Trader(agent_id=agent_id, strategy=strategy, model_name=model)
        if args.seed_inventory > 0:
            # Seed inventory for ALL supported assets
            for asset in SUPPORTED_ASSETS:
                agent.portfolio.seed_position(asset, args.seed_inventory, args.initial_price)
        agents.append(agent)
    
    # Initialize UI
    layout = generate_layout()
    layout["header"].update(Panel(f"Agent Market Simulation - {QUOTE_CURRENCY} Denominated Stock Exchange", style="bold blue"))
    layout["news_flash"].update(Panel("Market Opening...", title="BREAKING NEWS", style="bold red"))
    layout["footer"].update(Panel("Press Ctrl+C to stop", style="dim"))

    recent_actions = deque(maxlen=200)
    
    # Initialize Journalist
    from src.agents.journalist import JournalistAgent
    journalist = JournalistAgent()

    # 2. Execution Loop
    report_dir = None
    report_enabled = args.report or not args.no_report
    tick = 0
    try:
        with Live(layout, refresh_per_second=4, screen=True):
            try:
                while True:
                    tick += 1
                    start_time = asyncio.get_event_loop().time()

                    # --- JOURNALIST UPDATE ---
                    if tick % 10 == 0:
                        recent_txns = engine.ledger.get_transactions(limit=20)
                        try:
                            news = await journalist.analyze(engine.get_state(SUPPORTED_ASSETS[0]), recent_txns)
                            layout["news_flash"].update(Panel(f"[bold]{news.headline}[/bold]\n{news.body}", title="BREAKING NEWS", style="bold red"))
                        except Exception as e:
                            logging.error(f"Journalist error: {e}")

                    # Shuffle agents so they act in random order
                    random.shuffle(agents)

                    # --- PHASE 2: THINK & ACT (Concurrent Batches) ---
                    async def run_agent(agent: Trader):
                        # Smart Asset Selection: Biases towards assets with higher volatility/movement
                        if random.random() < 0.7:  # 70% chance to follow market "heat"
                            # Find the asset with the highest deviation from its base price (simulated volatility)
                            # In a real system, we'd use moving average variance.
                            # Here, we pick the asset with the highest raw price as a proxy for "activity"
                            # or randomly weight it by current price to simulate attention.
                            weighted_assets = []
                            for asset in SUPPORTED_ASSETS:
                                price = engine.current_prices.get(asset, 0)
                                # Weight by price + random noise to simulate varying attention
                                weight = price * random.uniform(0.8, 1.2)
                                weighted_assets.append((asset, weight))
                            
                            focused_asset = max(weighted_assets, key=lambda x: x[1])[0]
                        else:
                            # 30% chance to explore random assets (maintain liquidity in quiet markets)
                            focused_asset = random.choice(SUPPORTED_ASSETS)
                        
                        # Agent perceives state of that asset, retrieves memory, and decides
                        state = engine.get_state(focused_asset)
                        decision = await agent.act(state, focused_item=focused_asset, all_current_prices=engine.current_prices)
                        
                        if decision:
                            # Negotiate a counter-offer
                            negotiated_price, negotiation_details = engine.negotiate_price(
                                agent_id=agent.id,
                                action=decision["action"],
                                item=decision["item"],
                                price=decision["price"],
                            )
                            if negotiation_details:
                                decision["price"] = negotiated_price
                                engine.ledger.record_interaction(InteractionLog(**negotiation_details))

                            # Execute action against the market engine
                            tx = engine.process_action(
                                agent, 
                                decision["action"], 
                                decision["item"], 
                                decision["price"]
                            )
                            
                            # Prepare log entry
                            log_entry = ActionLog(
                                agent_id=agent.id,
                                action=decision["action"],
                                price=decision["price"],
                                reasoning=decision["reasoning"]
                            )
                            recent_actions.append(log_entry)
                            
                            # --- PHASE 3: LOG & PERSIST ---
                            logging.info(f"AGENT: {agent.id} | ITEM: {decision['item']} | ACTION: {decision['action'].value} | PRICE: {decision['price']} | REASON: {decision['reasoning']}")
                            engine.ledger.record_interaction(
                                InteractionLog(
                                    run_id=run_id,
                                    agent_id=agent.id,
                                    kind="action",
                                    action=decision["action"].value,
                                    item=decision["item"],
                                    price=decision["price"],
                                    details=decision["reasoning"],
                                )
                            )
                            if tx:
                                logging.info(f"  -> TRADE EXECUTED: {tx}")

                    # Execute all agents concurrently
                    # The GlobalRateLimiter will handle queuing if we exceed API limits
                    await asyncio.gather(*[run_agent(a) for a in agents], return_exceptions=True)

                    # --- PHASE 4: VISUALIZE ---
                    layout["market_status"].update(create_market_table(engine))
                    layout["recent_activity"].update(create_activity_table(agents, recent_actions))
                    
                    # Control simulation speed
                    elapsed = asyncio.get_event_loop().time() - start_time
                    sleep_time = max(0, Tick_Duration - elapsed)
                    await asyncio.sleep(sleep_time)

                    # --- CHECKPOINTS ---
                    if args.checkpoint_every and tick % args.checkpoint_every == 0:
                        payload = build_checkpoint(
                            tick=tick,
                            current_prices=engine.current_prices,
                            agents=agents,
                            transactions=engine.ledger.get_transactions(limit=args.checkpoint_transactions),
                            interactions=engine.ledger.get_interactions(limit=args.checkpoint_interactions),
                        )
                        filename = f"checkpoint_{tick:06d}.json"
                        path = write_checkpoint(payload, args.checkpoint_dir, filename)
                        logging.info(f"CHECKPOINT: {path}")

                    if args.max_ticks and tick >= args.max_ticks:
                        logging.info(f"Simulation completed after {tick} ticks.")
                        break
            finally:
                if report_enabled:
                    report_dir = generate_report(
                        run_id=run_id,
                        db_path="market.db",
                        report_root=args.report_dir,
                        agents=agents,
                        current_prices=engine.current_prices,
                    )
    finally:
        transactions = engine.ledger.get_transactions_for_run(run_id)
        summary = _build_run_summary(
            run_id=run_id,
            ticks=tick,
            agents=agents,
            transactions=transactions,
            current_prices=engine.current_prices,
            report_dir=report_dir,
            report_enabled=report_enabled,
        )
        _render_run_summary(summary)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nSimulation stopped by user.")
