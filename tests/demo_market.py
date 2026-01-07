import sys
import os

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), "../src"))

from market.engine import MarketEngine
from market.schema import AgentAction
from rich.console import Console
from rich.table import Table

def main():
    console = Console()
    console.print("[bold green]Starting Market Demo...[/bold green]")
    
    # Initialize Engine
    engine = MarketEngine("demo_market.db")
    
    # Scene 1: A lone seller
    console.print("\n[bold]Step 1: Agent A sells an apple for $10[/bold]")
    action = engine.process_action("Agent_A", AgentAction.SELL, "apple", 10.0)
    if action:
        console.print(f"[red]Trade Executed![/red] {action}")
    else:
        console.print("[yellow]Order added to book (no match).[/yellow]")
        
    state = engine.get_state()
    console.print(f"Market State: {state}")

    # Scene 2: A cheap buyer (no match)
    console.print("\n[bold]Step 2: Agent B wants to buy for $5[/bold]")
    action = engine.process_action("Agent_B", AgentAction.BUY, "apple", 5.0)
    if action:
        console.print(f"[red]Trade Executed![/red] {action}")
    else:
        console.print("[yellow]Order added to book (no match).[/yellow]")
        
    state = engine.get_state()
    console.print(f"Market State: {state}")

    # Scene 3: A willing buyer (match!)
    console.print("\n[bold]Step 3: Agent C wants to buy for $11[/bold]")
    # Should match with Agent A at $10 (Maker price)
    action = engine.process_action("Agent_C", AgentAction.BUY, "apple", 11.0)
    if action:
        console.print(f"[red]Trade Executed![/red] {action}")
    else:
        console.print("[yellow]Order added to book (no match).[/yellow]")
        
    state = engine.get_state()
    console.print(f"Market State: {state}")

    # Verify Ledger
    console.print("\n[bold]Verifying Ledger...[/bold]")
    txs = engine.ledger.get_transactions()
    table = Table(title="Ledger Transactions")
    table.add_column("Buyer")
    table.add_column("Seller")
    table.add_column("Price")
    table.add_column("Item")
    
    for tx in txs:
        table.add_row(tx.buyer_id, tx.seller_id, str(tx.price), tx.item)
        
    console.print(table)

if __name__ == "__main__":
    main()
