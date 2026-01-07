from abc import ABC, abstractmethod
from typing import Optional
from market.schema import MarketState, AgentAction, Transaction
from memory.memory import AgentMemory

class BaseAgent(ABC):
    def __init__(self, agent_id: str, persona: str):
        self.id = agent_id
        self.persona = persona
        self.memory = AgentMemory(agent_id=agent_id)

    @abstractmethod
    def act(self, market_state: MarketState) -> Optional[dict]:
        """
        Decide on an action given the current market state.
        Returns a dict representing the action (type, item, price, reasoning) or None.
        """
        pass

    def remember(self, text: str):
        self.memory.add_memory(text)
