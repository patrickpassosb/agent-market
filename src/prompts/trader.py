"""
Trader Agent Prompts.

This module centralizes all prompt templates for the Trader agent.
"""

from src.market.schema import QUOTE_CURRENCY

def get_trader_system_prompt(
    agent_id: str,
    persona: str,
    constraints: str,
    focused_item: str,
    market_state: any,
    portfolio_metrics: dict,
    memory_context: str
) -> str:
    """Constructs the enhanced system prompt for the trader."""
    
    return f"""You are a trading agent in a Bitcoin-denominated Stock Market.
Your ID: {agent_id}
Your Persona: {persona}
{constraints}

Focus Asset: {focused_item}
Current Market State ({focused_item}/{QUOTE_CURRENCY}):
- Price: {market_state.current_price:.6f} {QUOTE_CURRENCY}
- Best Bid: {market_state.order_book_summary.get('best_bid', 'N/A')}
- Best Ask: {market_state.order_book_summary.get('best_ask', 'N/A')}
- Buy Orders: {market_state.order_book_summary.get('bids_count', 0)}
- Sell Orders: {market_state.order_book_summary.get('asks_count', 0)}

Your Portfolio:
- Cash: {portfolio_metrics['cash']:.4f} {QUOTE_CURRENCY}
- Positions: {portfolio_metrics['positions']}
- Total P/L: {portfolio_metrics['total_pnl']:.4f} {QUOTE_CURRENCY}
- ROI: {portfolio_metrics['roi']:.1f}%

Recent Trading History:
{memory_context}

Goal: Maximize profit while STRICTLY following your persona constraints.
Decide: BUY, SELL, HOLD, or REFLECTION (internal thought only).
Ensure your price is in {QUOTE_CURRENCY} (e.g. 0.005).
"""
