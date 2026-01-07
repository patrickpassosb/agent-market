import os
import json
from typing import Optional, Literal
from pydantic import BaseModel, Field
from litellm import completion
from .base import BaseAgent
from src.market.schema import MarketState, AgentAction

# Define the structured output model for the LLM
class TraderDecision(BaseModel):
    action: Literal["buy", "sell", "hold", "reflection"]
    item: str = Field(description="The item to trade, e.g., 'apple'")
    price: float = Field(description="The price to buy or sell at. 0.0 if hold/reflection.")
    reasoning: str = Field(description="Short reasoning for the decision, under 1 sentence.")

class Trader(BaseAgent):
    def __init__(self, agent_id: str, persona: str, model_name: str = "groq/llama-3.1-8b-instant"):
        super().__init__(agent_id, persona)
        self.model_name = model_name

    def act(self, market_state: MarketState) -> Optional[dict]:
        # 1. Retrieve relevant memories (simple context for now)
        recent_memories = self.memory.retrieve_memory("market strategy", n_results=3)
        memory_context = "\n".join(recent_memories) if recent_memories else "No specific recent memories."

        # 2. Construct Prompt
        system_prompt = f"""You are a trading agent in a market simulation.
Your ID: {self.id}
Your Persona: {self.persona}

Current Market State:
Price: {market_state.current_price}
Order Book: {market_state.order_book_summary}

Your recent memories:
{memory_context}

Goal: Maximize profit based on your persona.
Decide your next action: BUY, SELL, HOLD, or REFLECTION.
"""

        # 3. Call LLM
        try:
            response = completion(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": "What is your next move?"}
                ],
                response_format=TraderDecision
            )
            
            content = response.choices[0].message.content
            decision = TraderDecision.model_validate_json(content)
            
            # Log reasoning to memory
            self.remember(f"Decided to {decision.action} at {decision.price}: {decision.reasoning}")

            # Return standard dict for the engine
            # Convert string action to Enum
            action_enum = AgentAction(decision.action)
            
            return {
                "action": action_enum,
                "item": decision.item,
                "price": decision.price,
                "reasoning": decision.reasoning
            }

        except Exception as e:
            print(f"Error in agent {self.id}: {e}")
            return None
