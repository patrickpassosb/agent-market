"""
Market Engine (Facade).

This module serves as the central controller for the market simulation.
It follows the **Facade Pattern**, providing a simplified interface to the 
complex underlying subsystems: the OrderBook (matching) and the Ledger (persistence).

Responsibilities:
1. Maintain the current state of the market (Last Price).
2. Route agent actions to the Order Book.
3. Record successful trades in the Ledger.
4. Expose market state to agents.
"""

from typing import List, Any, Dict, Optional
import math
from datetime import datetime

from .ledger import Ledger
from .order_book import OrderBook
from .schema import Transaction, AgentAction, MarketState, DEFAULT_ITEM

class MarketEngine:
    """
    The main engine driving the market logic.
    
    Attributes:
        ledger (Ledger): Handle to the database.
        order_book (OrderBook): Handle to the in-memory matching engine.
        last_price (float): The price of the most recent execution. Used as the "current market price".
    """

    def __init__(self, db_path: str = "market.db"):
        """
        Initialize the market engine.
        
        Args:
            db_path (str): Path to the SQLite database file.
        """
        self.ledger = Ledger(db_path)
        self.order_book = OrderBook()
        self.last_price = 0.0 # Initialize at 0, or could be a seed price

    def get_state(self) -> MarketState:
        """
        Constructs and returns the current state of the market.
        
        This is the "sensor" data provided to agents.
        
        Returns:
            MarketState: Object containing price and order book summary.
        """
        summary = self.order_book.get_summary()
        return MarketState(
            current_price=self.last_price,
            order_book_summary=summary
        )

    def process_action(self, agent: Any, action: AgentAction, item: str = DEFAULT_ITEM, price: float = 0.0) -> Optional[Transaction]:
        """
        Processes an action submitted by an agent.
        
        This method acts as the central transaction coordinator. It:
        1. Validates the input arguments.
        2. Routes the order to the `OrderBook`.
        3. If a match occurs, it validates the trade against the agent's `Portfolio`.
        4. If valid, records the transaction in the `Ledger`.
        
        Args:
            agent (BaseAgent): The agent instance submitting the action. 
                               Must have a `portfolio` attribute.
            action (AgentAction): The type of action (BUY, SELL, HOLD, REFLECTION).
            item (str): The asset involved (default `DEFAULT_ITEM`).
            price (float): The limit price for the order.
            
        Returns:
            Optional[Transaction]: The resulting transaction if a trade occurred, else None.
        """
        transaction = None
        
        # HOLD or REFLECTION actions have no market impact
        if action in (AgentAction.HOLD, AgentAction.REFLECTION):
            return None

        if not isinstance(item, str) or not item.strip():
            return None

        if not isinstance(price, (int, float)) or not math.isfinite(price) or price <= 0:
            return None

        # Route action to the appropriate OrderBook method
        if action == AgentAction.BUY:
            transaction = self.order_book.add_buy(agent.id, item, float(price))
            
            # If trade matched, execute against portfolio
            if transaction:
                # Portfolio validation: Check if agent has enough cash
                success = agent.portfolio.execute_buy(
                    item=transaction.item,
                    quantity=1,  # TODO: Support variable quantities
                    price=transaction.price
                )
                
                if not success:
                    # Rollback: Insufficient funds, cancel the trade
                    # In a real system we'd need to put the order back on the book
                    return None
                    
        elif action == AgentAction.SELL:
            transaction = self.order_book.add_sell(agent.id, item, float(price))
            
            # If trade matched, execute against portfolio
            if transaction:
                # Portfolio validation: Check if agent has the asset
                success = agent.portfolio.execute_sell(
                    item=transaction.item,
                    quantity=1,
                    price=transaction.price
                )
                
                if not success:
                    # Rollback: Insufficient inventory
                    return None
        else:
            return None

        # If the order resulted in a trade AND portfolio execution succeeded
        if transaction:
            # 1. Persist to DB
            self.ledger.record_transaction(transaction)
            
            # 2. Update Market State
            self.last_price = transaction.price
            
            return transaction
        
        return None

    def negotiate_price(self, agent_id: str, action: AgentAction, item: str, price: float) -> tuple[float, Optional[dict]]:
        """
        Provides a counter-offer price based on current best quotes.
        """
        best_bid, best_ask = self.order_book.get_best_quotes(item)

        if action == AgentAction.BUY and best_ask is not None and price < best_ask:
            counter_price = (price + best_ask) / 2.0
            details = {
                "kind": "negotiation",
                "agent_id": agent_id,
                "counterparty_id": None,
                "action": action.value,
                "item": item,
                "price": counter_price,
                "details": f"Counter-offer between bid {price} and ask {best_ask}.",
            }
            return counter_price, details

        if action == AgentAction.SELL and best_bid is not None and price > best_bid:
            counter_price = (price + best_bid) / 2.0
            details = {
                "kind": "negotiation",
                "agent_id": agent_id,
                "counterparty_id": None,
                "action": action.value,
                "item": item,
                "price": counter_price,
                "details": f"Counter-offer between ask {price} and bid {best_bid}.",
            }
            return counter_price, details

        return price, None
