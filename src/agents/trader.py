"""
Trader Agent Implementation.

This module contains the concrete implementation of a trading agent powered by an LLM.
It handles:
1. Context construction (Memory retrieval + Market State).
2. Prompt engineering.
3. Structured Output parsing (using `litellm` and `pydantic`).
"""

from typing import Optional, Literal
import math
from pydantic import BaseModel, Field
import litellm
from litellm import completion
from .base import BaseAgent
from src.market.schema import MarketState, AgentAction, DEFAULT_ITEM

# --- Data Models for LLM Output ---

litellm.enable_json_schema_validation = True

def _parse_structured_response(model_cls: type[BaseModel], content):
    if isinstance(content, model_cls):
        return content
    if isinstance(content, dict):
        return model_cls.model_validate(content)
    return model_cls.model_validate_json(content)

class TraderDecision(BaseModel):
    """
    Pydantic model defining the expected JSON structure from the LLM.
    Used for strict type validation of the agent's output.
    """
    action: Literal["buy", "sell", "hold", "reflection"] = Field(
        description="The action to take. 'reflection' is for internal thought only."
    )
    item: str = Field(
        description="The item to trade, typically 'apple' in this simulation."
    )
    price: float = Field(
        description="The limit price for the order. Set to 0.0 if holding or reflecting."
    )
    reasoning: str = Field(
        description="A concise explanation (under 1 sentence) for this decision."
    )

# --- Agent Implementation ---

class Trader(BaseAgent):
    """
    An AI-powered trading agent.
    
    This agent uses a Large Language Model (LLM) to decide on market actions.
    It combines its static 'persona' with dynamic market data and retrieved memories
    to form a decision.
    
    Attributes:
        model_name (str): The specific LLM model identifier (e.g., 'groq/llama-3.1-8b-instant').
    """

    def __init__(self, agent_id: str, persona: str, model_name: str = "groq/llama-3.1-8b-instant"):
        """
        Args:
            agent_id (str): Unique ID.
            persona (str): Strategy description.
            model_name (str): The LLM to use for inference.
        """
        super().__init__(agent_id, persona)
        self.model_name = model_name
    
    def _get_persona_constraints(self) -> str:
        """
        Return specific behavioral rules based on persona type.
        This helps enforce persona adherence.
        """
        p_lower = self.persona.lower()
        
        # Panic sellers MUST sell on drops
        if "panic" in p_lower:
            return "CRITICAL: You MUST sell immediately if the current price is below your average cost."
        
        # Contrarians MUST go against the majority
        elif "contrar" in p_lower:
            return "CRITICAL: You MUST trade AGAINST the majority. If bids > asks, you MUST sell. If asks > bids, you MUST buy."
        
        # Market makers MUST provide liquidity on both sides
        elif "market maker" in p_lower:
            return "CRITICAL: Your goal is to profit from the spread. You should place BOTH a buy order below market and a sell order above market."
        
        # FOMO buyers buy on spikes
        elif "fomo" in p_lower:
            return "You are driven by fear of missing out. Buy aggressively when prices are rising."
        
        # Conservative investors only buy dips
        elif "conservative" in p_lower or "long-term" in p_lower:
            return "You only buy when prices are significantly below historical averages. Be patient and selective."
        
        # DCA buyers buy every tick
        elif "dca" in p_lower or "dollar cost" in p_lower:
            return "You MUST buy a small amount every single tick, regardless of price."
        
        # Default: no special constraints
        return "Follow your general strategy as described in your persona."

    def act(self, market_state: MarketState) -> Optional[dict]:
        """
        Execute one decision cycle.
        
        Steps:
        1. Query Memory: Retrieve relevant past experiences based on "market strategy".
        2. Build Context: Combine Persona, Market Data, and Memories into a system prompt.
        3. Inference: Call the LLM asking for a JSON response conforming to `TraderDecision`.
        4. Parse & Log: Validate output, store reasoning in memory, and return action.
        """
        
        # 1. Get portfolio context
        current_prices = {DEFAULT_ITEM: market_state.current_price}  # TODO: Multi-asset
        portfolio_metrics = self.portfolio.get_metrics(current_prices)
        
        # 2. Retrieve relevant memories
        recent_memories = self.memory.retrieve_memory("trading decision", n_results=3)
        memory_context = "\n".join(recent_memories) if recent_memories else "No past trades recorded."

        # 3. Get persona-specific constraints
        constraints = self._get_persona_constraints()

        # 4. Construct enhanced system prompt
        system_prompt = f"""You are a trading agent in a market simulation.
Your ID: {self.id}
Your Persona: {self.persona}
{constraints}

Current Market State:
- Price: ${market_state.current_price:.2f}
- Best Bid: {market_state.order_book_summary.get('best_bid', 'N/A')}
- Best Ask: {market_state.order_book_summary.get('best_ask', 'N/A')}
- Buy Orders: {market_state.order_book_summary.get('bids_count', 0)}
- Sell Orders: {market_state.order_book_summary.get('asks_count', 0)}

Your Portfolio:
- Cash: ${portfolio_metrics['cash']:.2f}
- Positions: {portfolio_metrics['positions']}
- Total P/L: ${portfolio_metrics['total_pnl']:.2f}
- ROI: {portfolio_metrics['roi']:.1f}%

Recent Trading History:
{memory_context}

Goal: Maximize profit while STRICTLY following your persona constraints.
Decide: BUY, SELL, HOLD, or REFLECTION (internal thought only).
"""

        # 3. Call LLM
        try:
            # We use litellm's `response_format` to enforce the Pydantic schema
            response = completion(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": "What is your next move?"}
                ],
                response_format=TraderDecision
            )
            
            # 4. Process Response
            content = response.choices[0].message.content
            
            # Validate JSON against Pydantic model
            decision = _parse_structured_response(TraderDecision, content)
            
            if decision.action in ("buy", "sell"):
                if not math.isfinite(decision.price) or decision.price <= 0:
                    # Ensure tradable prices to avoid zero-trade runs (Context7 /python/cpython https://github.com/python/cpython/blob/main/Doc/library/math.rst)
                    decision.price = market_state.current_price if market_state.current_price > 0 else 1.0

            # Log the reasoning to the agent's internal long-term memory
            # This allows the agent to "remember" why it did something in future turns.
            self.remember(f"Decided to {decision.action} at {decision.price}: {decision.reasoning}")

            # Convert string action to internal Enum
            action_enum = AgentAction(decision.action)
            
            return {
                "action": action_enum,
                "item": decision.item,
                "price": decision.price,
                "reasoning": decision.reasoning
            }

        except Exception as e:
            # Graceful degradation: Log error and do nothing (HOLD)
            # In a real system, we might want to retry or trigger a circuit breaker.
            print(f"Error in agent {self.id}: {e}")
            return None
