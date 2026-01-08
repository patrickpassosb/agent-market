"""
Market Schema Definitions.

This module defines the core data structures and types used throughout the market simulation.
It utilizes:
- `Enum` for fixed sets of values (Actions).
- `SQLModel` (SQLAlchemy + Pydantic) for database persistence of Transactions.
- `Pydantic` for transient data validation (MarketState).
"""

from datetime import datetime, timezone
from enum import Enum
from typing import Dict, Any, Optional, List

from pydantic import BaseModel
from sqlmodel import Field, SQLModel

# Base Currency Configuration
QUOTE_CURRENCY = "BTC"
SUPPORTED_ASSETS = ["AAPL", "TSLA", "NVDA", "MSFT"]

class AgentAction(str, Enum):
    """
    Enumeration of possible actions an agent can take in a single simulation tick.
    
    Attributes:
        BUY (str): Place a bid to purchase the asset.
        SELL (str): Place an ask to sell the asset.
        HOLD (str): Do nothing this tick.
        REFLECTION (str): Internal state update (no market action).
    """
    BUY = "buy"
    SELL = "sell"
    HOLD = "hold"
    REFLECTION = "reflection"

class Transaction(SQLModel, table=True):
    """
    Represents a successful trade executed in the market.
    
    This model serves as the schema for the 'transaction' table in the SQLite database.
    It records who bought/sold, what item, at what price, and when.
    
    Attributes:
        id (Optional[int]): Primary Key. Auto-incrementing integer.
        buyer_id (str): The ID of the agent acting as the buyer. Indexed for faster queries.
        seller_id (str): The ID of the agent acting as the seller. Indexed for faster queries.
        item (str): The identifier of the asset traded (e.g., 'apple').
        price (float): The final execution price of the trade.
        timestamp (datetime): UTC timestamp of when the trade occurred. Defaults to now.
    """
    __table_args__ = {"extend_existing": True}
    
    id: Optional[int] = Field(default=None, primary_key=True, description="Unique Transaction ID")
    run_id: Optional[str] = Field(default=None, index=True, description="Simulation run identifier")
    buyer_id: str = Field(index=True, description="ID of the buying agent")
    seller_id: str = Field(index=True, description="ID of the selling agent")
    item: str = Field(description="Name of the asset traded")
    price: float = Field(description="Execution price")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="Time of transaction (UTC)")  # https://github.com/python/cpython/blob/main/Doc/library/datetime.rst (Context7 /python/cpython)

class MarketState(BaseModel):
    """
    Snapshot of the market conditions at a specific point in time.
    
    This object is passed to agents to inform their decision-making process.
    It does not contain the full history, but rather the current "ticker" info
    and a summary of the order book.
    
    Attributes:
        current_price (float): The price of the last executed trade.
        order_book_summary (Dict[str, Any]): A simplified view of the order book 
                                             (e.g., best_bid, best_ask, counts).
    """
    current_price: float
    order_book_summary: Dict[str, Any]

class ActionLog(BaseModel):
    """
    Structure for logging an agent's decision and reasoning for the UI.
    
    Attributes:
        agent_id (str): ID of the agent performing the action.
        action (AgentAction): The type of action taken.
        price (float): The price point of the action.
        reasoning (str): The agent's explanation for their decision.
    """
    agent_id: str
    action: AgentAction
    price: float
    reasoning: str

class InteractionLog(SQLModel, table=True):  # https://sqlmodel.tiangolo.com/tutorial/create-db-and-table (Context7 /websites/sqlmodel_tiangolo)
    """
    Records non-transaction interactions (agent actions, negotiations, commentary).
    """
    __table_args__ = {"extend_existing": True}

    id: Optional[int] = Field(default=None, primary_key=True, description="Unique Interaction ID")
    run_id: Optional[str] = Field(default=None, index=True, description="Simulation run identifier")
    agent_id: str = Field(index=True, description="ID of the acting agent")
    kind: str = Field(description="Interaction category (e.g., action, negotiation)")
    action: Optional[str] = Field(default=None, description="Action label, if applicable")
    item: Optional[str] = Field(default=None, description="Asset identifier, if applicable")
    price: Optional[float] = Field(default=None, description="Price associated with the interaction")
    counterparty_id: Optional[str] = Field(default=None, description="Counterparty agent ID, if applicable")
    details: Optional[str] = Field(default=None, description="Free-form details or notes")
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Time of interaction (UTC)",
    )  # https://github.com/python/cpython/blob/main/Doc/library/datetime.rst (Context7 /python/cpython)
