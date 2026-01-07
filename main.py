import os
import time
import random
from typing import List
from dotenv import load_dotenv

from rich.live import Live
from rich.table import Table
from rich.layout import Layout
from rich.console import Console
from rich.panel import Panel

from src.market.engine import MarketEngine
from src.agents.trader import Trader
from src.market.schema import AgentAction, Transaction
from src.utils.personas import PERSONAS

# Load environment variables
load_dotenv()

# Simulation Settings
NUM_AGENTS = 5  # Start small for clarity, can bump to 10
Tick_Duration = 2.0 # Seconds per tick

console = Console()

def generate_layout() -> Layout:
    layout = Layout()
    layout.split_column(
        Layout(name="header", size=3),
        Layout(name="main", ratio=1),
        Layout(name="footer", size=3)
    )
    layout["main"].split_row(
        Layout(name="market_status", ratio=1),
        Layout(name="recent_activity", ratio=2)
    )
    return layout

def create_market_table(state) -> Panel:
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

# Model Keywords
SMART_GROQ_KEYWORDS = ["whale", "market maker"]
GEMINI_KEYWORDS = ["value", "patient", "long-term", "conservative"]
OPENAI_KEYWORDS = ["algorithmic", "disciplined", "contrarian"]

def get_model_for_persona(persona: str) -> str:
    """
    Assigns models based on persona characteristics:
    - Smart/Big players -> Llama 70B (Groq)
    - Analytical/Patient -> Gemini 1.5 Flash
    - Structural/Rules  -> GPT-4o Mini
    - Reactive/Fast     -> Llama 8B (Groq) - Default
    """
    p_lower = persona.lower()
    
    if any(k in p_lower for k in SMART_GROQ_KEYWORDS):
        return "groq/llama-3.3-70b-versatile"
    
    if any(k in p_lower for k in GEMINI_KEYWORDS):
        return "gemini/gemini-1.5-flash"
        
    if any(k in p_lower for k in OPENAI_KEYWORDS):
        return "openai/gpt-4o-mini"
        
    return "groq/llama-3.1-8b-instant"

def create_activity_table(agents: List[Trader], recent_actions: List[dict]) -> Panel:
    table = Table(title="Agent Activity & Decisions")
    table.add_column("Agent / Model", style="white")
    table.add_column("Action", style="bold")
    table.add_column("Details", style="dim")
    
    # Create a quick lookup for agent models
    agent_models = {a.id: a.model_name for a in agents}

    for act in recent_actions[-10:]: # Show last 10
        color = "green" if act['action'] == AgentAction.BUY else "red" if act['action'] == AgentAction.SELL else "yellow"
        
        # Format Model Name for display
        model_raw = agent_models.get(act['agent_id'], "?")
        if "70b" in model_raw:
            model_display = "[bold cyan]Llama 70B[/]"
        elif "gemini" in model_raw:
            model_display = "[bold blue]Gemini Flash[/]"
        elif "gpt" in model_raw:
            model_display = "[bold green]GPT-4o Mini[/]"
        else:
            model_display = "[dim]Llama 8B[/]"

        table.add_row(
            f"{act['agent_id']} ({model_display})",
            f"[{color}]{act['action'].value.upper()}[/{color}]",
            f"{act['reasoning']} (@ {act['price']})"
        )
    
    return Panel(table, title="Live Feed")

def main():
    # 1. Setup
    engine = MarketEngine("market.db")
    agents: List[Trader] = []
    
    # Select random personas
    selected_personas = random.sample(PERSONAS, min(NUM_AGENTS, len(PERSONAS)))
    
    for i, persona in enumerate(selected_personas):
        agent_id = f"Agent_{i+1}"
        # Determine model based on persona
        model = get_model_for_persona(persona)
        
        agent = Trader(agent_id=agent_id, persona=persona, model_name=model)
        agents.append(agent)
    
    layout = generate_layout()
    layout["header"].update(Panel("Agent Market Simulation - AI Traders (Hybrid Models)", style="bold blue"))
    layout["footer"].update(Panel("Press Ctrl+C to stop", style="dim"))

    recent_actions = []

    # 2. Loop
    with Live(layout, refresh_per_second=4, screen=True) as live:
        tick = 0
        while True:
            tick += 1
            start_time = time.time()
            
            # --- MARKET TICK ---
            market_state = engine.get_state()
            
            # Shuffle agents so they act in random order (fairness)
            random.shuffle(agents)
            
            tick_actions = []
            
            for agent in agents:
                # Agent perceives and decides
                decision = agent.act(market_state)
                
                if decision:
                    # Execute
                    tx = engine.process_action(
                        agent.id, 
                        decision["action"], 
                        decision["item"], 
                        decision["price"]
                    )
                    
                    # Log result
                    log_entry = {
                        "agent_id": agent.id,
                        "action": decision["action"],
                        "price": decision["price"],
                        "reasoning": decision["reasoning"]
                    }
                    recent_actions.append(log_entry)
                    tick_actions.append(log_entry)
                    
                    # If trade happened, maybe log it differently? For now this is fine.

            # Update UI
            layout["market_status"].update(create_market_table(engine.get_state()))
            layout["recent_activity"].update(create_activity_table(agents, recent_actions))
            
            # Wait remainder of tick
            elapsed = time.time() - start_time
            sleep_time = max(0, Tick_Duration - elapsed)
            time.sleep(sleep_time)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nSimulation stopped by user.")
