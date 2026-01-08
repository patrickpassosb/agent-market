"""
Base Agent Interface.

This module defines the abstract base class for all agents in the simulation.
It enforces a standard interface (`act`) that the simulation loop relies on.
"""

from abc import ABC, abstractmethod
from typing import Optional
from src.market.schema import MarketState, AgentAction, Transaction
from src.memory.memory import AgentMemory
from src.agents.portfolio import Portfolio

class BaseAgent(ABC):
    """
    Abstract base class for all trading agents.
    
    Defines the common interface and shared utilities for agents in the simulation.
    All agents have:
    - A unique ID
    - A persona/strategy description
    - Access to a long-term memory system (via ChromaDB)
    - A portfolio to track wealth and positions
    """

    def __init__(self, agent_id: str, persona: str):
        """
        Args:
            agent_id (str): Unique identifier for this agent.
            persona (str): Natural language description of the agent's trading strategy.
        """
        self.id = agent_id
        self.persona = persona
        # Initialize memory system for this specific agent
        self.memory = AgentMemory(agent_id=agent_id)
        # Initialize portfolio for this specific agent
        self.portfolio = Portfolio()

    @abstractmethod
    def act(self, market_state: MarketState) -> Optional[dict]:
        """
        The core decision-making method.
        
        Must be implemented by subclasses.
        
        Args:
            market_state (MarketState): The current view of the market.
            
        Returns:
            Optional[dict]: A dictionary containing the decision keys:
                            - action (AgentAction)
                            - item (str)
                            - price (float)
                            - reasoning (str)
                            Or None if no action is taken.
        """
        pass

    def remember(self, text: str):
        """
        Stores a text string into the agent's long-term memory.
        
        Args:
            text (str): The fact, observation, or thought to remember.
        """
        self.memory.add_memory(text)