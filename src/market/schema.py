from datetime import datetime
from enum import Enum
from typing import Dict, Any, Optional

from pydantic import BaseModel
from sqlmodel import Field, SQLModel

class AgentAction(str, Enum):
    BUY = "buy"
    SELL = "sell"
    HOLD = "hold"
    REFLECTION = "reflection"

class Transaction(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    buyer_id: str = Field(index=True)
    seller_id: str = Field(index=True)
    item: str
    price: float
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class MarketState(BaseModel):
    current_price: float
    order_book_summary: Dict[str, Any]
