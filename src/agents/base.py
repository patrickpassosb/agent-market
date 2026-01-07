"""
Base Agent Interface.

This module defines the abstract base class for all agents in the simulation.
It enforces a standard interface (`act`) that the simulation loop relies on.
"""

from abc import ABC, abstractmethod
from typing import Optional
from src.market.schema import MarketState, AgentAction, Transaction
from src.memory.memory import AgentMemory

class BaseAgent(ABC):
    """
    Abstract Base Class for autonomous agents.
    
    Attributes:
        id (str): Unique identifier for the agent.
        persona (str): A natural language description of the agent's behavior/strategy.
        memory (AgentMemory): A handle to the agent's long-term memory (vector DB).
    """

    def __init__(self, agent_id: str, persona: str):
        """
        Initialize the base agent.
        
        Args:
            agent_id (str): Unique ID.
            persona (str): Description of the agent's character.
        """
        self.id = agent_id
        self.persona = persona
        # Initialize memory system for this specific agent
        self.memory = AgentMemory(agent_id=agent_id)

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