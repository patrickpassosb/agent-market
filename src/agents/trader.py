"""
Trader Agent Implementation.

This module contains the concrete implementation of a trading agent powered by an LLM.
It handles:
1. Context construction (Memory retrieval + Market State).
2. Prompt engineering.
3. Structured Output parsing (using `litellm` and `pydantic`).
"""

import os
import json
from typing import Optional, Literal
from pydantic import BaseModel, Field
from litellm import completion
from .base import BaseAgent
from src.market.schema import MarketState, AgentAction

# --- Data Models for LLM Output ---

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

    def act(self, market_state: MarketState) -> Optional[dict]:
        """
        Execute one decision cycle.
        
        Steps:
        1. Query Memory: Retrieve relevant past experiences based on "market strategy".
        2. Build Context: Combine Persona, Market Data, and Memories into a system prompt.
        3. Inference: Call the LLM asking for a JSON response conforming to `TraderDecision`.
        4. Parse & Log: Validate output, store reasoning in memory, and return action.
        """
        
        # 1. Retrieve relevant memories (RAG - Retrieval Augmented Generation)
        # We query for general strategy to see if the agent has formed past rules.
        recent_memories = self.memory.retrieve_memory("market strategy", n_results=3)
        memory_context = "\n".join(recent_memories) if recent_memories else "No specific recent memories."

        # 2. Construct System Prompt
        # We explicitly state the persona and current objective data.
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
            decision = TraderDecision.model_validate_json(content)
            
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