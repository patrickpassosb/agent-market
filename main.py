"""
Multi-Agent Marketplace Simulation - Entry Point.

This script orchestrates the entire market simulation. It:
1. Initializes a MarketEngine (orderbook + ledger).
2. Creates multiple trading agents with diverse personas and LLMs.
3. Runs a simulation loop where agents observe, decide, and act.
4. Displays live updates using the Rich library for a dynamic terminal UI.

Usage:
    python main.py

Stop the simulation with Ctrl+C (SIGINT). The script will handle graceful shutdown.
"""

import os
import argparse
import time
import random
import logging
from collections import deque
from datetime import datetime
from typing import List, Iterable
from dotenv import load_dotenv

from rich.live import Live
from rich.table import Table
from rich.layout import Layout
from rich.console import Console
from rich.panel import Panel
import litellm
import logging

# Suppress LiteLLM verbose logging completely
litellm.set_verbose = False
os.environ["LITELLM_LOG"] = "CRITICAL"  # Only critical errors
logging.getLogger("LiteLLM").setLevel(logging.CRITICAL)
logging.getLogger("litellm").setLevel(logging.CRITICAL)

from src.market.engine import MarketEngine
from src.agents.trader import Trader
from src.market.schema import AgentAction, Transaction, ActionLog, InteractionLog
from src.utils.personas import PERSONAS, get_model_for_persona
from src.utils.checkpoints import build_checkpoint, write_checkpoint

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
    
    Structure:
    - Header
    - Main Body
        - Left: Market Status (Price, Order Book)
        - Right: Recent Activity (Agent logs)
    - Footer
    """
    layout = Layout()
    layout.split_column(
        Layout(name="header", size=3),
        Layout(name="news_flash", size=3),  # New News Ticker
        Layout(name="main", ratio=1),
        Layout(name="footer", size=3)
    )
    layout["main"].split_row(
        Layout(name="market_status", ratio=1),
        Layout(name="recent_activity", ratio=2)
    )
    return layout

def create_market_table(state) -> Panel:
    """
    Renders the Market Status panel. 
    
    Args:
        state (MarketState): Current state of the market.
    """
    table = Table(title="Market Status")
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="magenta")
    
    table.add_row("Current Price", f"${state.current_price:.2f}")
    
    obs = state.order_book_summary
    table.add_row("Best Bid", str(obs.get("best_bid")) if obs.get("best_bid") else "-")
    table.add_row("Best Ask", str(obs.get("best_ask")) if obs.get("best_ask") else "-")
    table.add_row("Bids Count", str(obs.get("bids_count")))
    table.add_row("Asks Count", str(obs.get("asks_count")))
    
    return Panel(table, title="Order Book & Price")

def create_activity_table(agents: List[Trader], recent_actions: Iterable[ActionLog]) -> Panel:
    """
    Renders the Agent Activity feed. 
    
    Args:
        agents (List[Trader]): List of all agents (for ID->Model lookup).
        recent_actions (Iterable[ActionLog]): List of recent action logs.
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
            model_display = "[bold blue]Gemini Flash[/]"
        elif "gpt" in model_raw:
            model_display = "[bold green]GPT-4o Mini[/]"
        else:
            model_display = "[dim]Llama 8B[/]"

        table.add_row(
            f"{act.agent_id} ({model_display})",
            f"[{color}]{act.action.value.upper()}[/{color}]",
            f"{act.reasoning} (@ {act.price})"
        )
    
    return Panel(table, title="Live Feed")

def parse_args():
    """
    Parse CLI args for bounded runs and checkpointing.
    """
    parser = argparse.ArgumentParser(
        description="Agent Market Simulation",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )  # https://github.com/python/cpython/blob/main/Doc/library/argparse.rst (Context7 /python/cpython)
    parser.add_argument("--max-ticks", type=int, default=0, help="Stop after N ticks (0 = run indefinitely).")
    parser.add_argument("--checkpoint-every", type=int, default=0, help="Write a checkpoint every N ticks (0 = disabled).")
    parser.add_argument("--checkpoint-dir", type=str, default="checkpoints", help="Directory for checkpoint JSON files.")
    parser.add_argument("--checkpoint-transactions", type=int, default=50, help="Transactions to include in checkpoints.")
    parser.add_argument("--checkpoint-interactions", type=int, default=100, help="Interactions to include in checkpoints.")
    return parser.parse_args()


# --- Main Simulation Loop ---

def main():
    # 1. Setup & Initialization
    args = parse_args()
    
    # Ensure logs directory exists and setup logging
    os.makedirs("logs", exist_ok=True)
    log_filename = f"logs/simulation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    
    # Configure global logging
    logging.basicConfig(
        filename=log_filename,
        level=logging.INFO,
        format='%(asctime)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    logging.info("Starting Agent Market Simulation")

    # Initialize Market Engine
    engine = MarketEngine("market.db")
    agents: List[Trader] = []
    
    # Initialize Agents with random personas
    selected_personas = random.sample(PERSONAS, min(NUM_AGENTS, len(PERSONAS)))
    
    for i, persona in enumerate(selected_personas):
        agent_id = f"Agent_{i+1}"
        # Determine appropriate LLM for this persona
        model = get_model_for_persona(persona)
        
        agent = Trader(agent_id=agent_id, persona=persona, model_name=model)
        agents.append(agent)
    
    # Initialize UI
    layout = generate_layout()
    layout["header"].update(Panel("Agent Market Simulation - AI Traders (Hybrid Models)", style="bold blue"))
    layout["news_flash"].update(Panel("Market Opening...", title="BREAKING NEWS", style="bold red"))
    layout["footer"].update(Panel("Press Ctrl+C to stop", style="dim"))

    recent_actions = deque(maxlen=200)
    
    # Initialize Journalist
    from src.agents.journalist import JournalistAgent
    journalist = JournalistAgent()  # Defaults to Gemini

    # 2. Execution Loop
    with Live(layout, refresh_per_second=4, screen=True) as live:
        tick = 0
        while True:
            tick += 1
            start_time = time.time()
            
            # --- MARKET TICK ---
            market_state = engine.get_state()
            
            # --- JOURNALIST UPDATE ---
            if tick % 10 == 0:
                # Get last 20 txns for context
                recent_txns = engine.ledger.get_transactions(limit=20)
                news = journalist.analyze(market_state, recent_txns)
                layout["news_flash"].update(Panel(f"[bold]{news.headline}[/bold]\n{news.body}", title="BREAKING NEWS", style="bold red"))
            
            # Shuffle agents so they act in random order (fairness in sequential processing)
            random.shuffle(agents)
            
            # --- PHASE 2: THINK & ACT ---
            for agent in agents:
                # Agent perceives state, retrieves memory, and decides
                decision = agent.act(market_state)
                
                if decision:
                    # Negotiate a counter-offer if quotes are far from the submitted price
                    negotiated_price, negotiation_details = engine.negotiate_price(
                        agent_id=agent.id,
                        action=decision["action"],
                        item=decision["item"],
                        price=decision["price"],
                    )
                    if negotiation_details:
                        decision["price"] = negotiated_price
                        engine.ledger.record_interaction(InteractionLog(**negotiation_details))
                        logging.info(
                            f"NEGOTIATION: {agent.id} | ACTION: {decision['action'].value} | PRICE: {decision['price']}"
                        )

                    # Execute action against the market engine
                    # Now passes the full agent object (for portfolio access)
                    tx = engine.process_action(
                        agent,  # Changed from agent.id
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
                    # Persist log to file
                    logging.info(f"AGENT: {agent.id} | ACTION: {decision['action'].value} | PRICE: {decision['price']} | REASON: {decision['reasoning']}")
                    engine.ledger.record_interaction(
                        InteractionLog(
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

            # --- PHASE 4: VISUALIZE ---
            # Update the UI components with the new state
            layout["market_status"].update(create_market_table(engine.get_state()))
            layout["recent_activity"].update(create_activity_table(agents, recent_actions))
            
            # Control simulation speed
            elapsed = time.time() - start_time
            sleep_time = max(0, Tick_Duration - elapsed)
            time.sleep(sleep_time)

            # --- CHECKPOINTS ---
            if args.checkpoint_every and tick % args.checkpoint_every == 0:
                payload = build_checkpoint(
                    tick=tick,
                    market_state=market_state,
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

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        # Handle manual stop gracefully
        print("\nSimulation stopped by user.")
