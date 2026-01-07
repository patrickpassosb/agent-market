from typing import List, Any, Dict, Optional
from datetime import datetime

from .ledger import Ledger
from .order_book import OrderBook
from .schema import Transaction, AgentAction, MarketState

class MarketEngine:
    def __init__(self, db_path: str = "market.db"):
        self.ledger = Ledger(db_path)
        self.order_book = OrderBook()
        self.last_price = 0.0

    def get_state(self) -> MarketState:
        summary = self.order_book.get_summary()
        return MarketState(
            current_price=self.last_price,
            order_book_summary=summary
        )

    def process_action(self, agent_id: str, action: AgentAction, item: str = "apple", price: float = 0.0) -> Optional[Transaction]:
        """
        Process a single agent action.
        Returns a Transaction if a trade occurred, else None.
        """
        if action == AgentAction.BUY:
            transaction = self.order_book.add_buy(agent_id, item, price)
        elif action == AgentAction.SELL:
            transaction = self.order_book.add_sell(agent_id, item, price)
        else:
            # HOLD or REFLECTION
            return None

        if transaction:
            self.ledger.record_transaction(transaction)
            self.last_price = transaction.price
            return transaction
        
        return None
