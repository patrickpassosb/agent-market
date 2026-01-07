"""
Order Book Implementation.

This module implements a standard Limit Order Book using binary heaps.
It supports adding buy (bid) and sell (ask) orders and matching them efficiently.

Matching Engine Logic:
- **Price-Time Priority**: Better prices match first. If prices are equal, earlier orders match first.
- **Bids (Buys)**: Maintained in a MAX-Heap (highest price at root).
- **Asks (Sells)**: Maintained in a MIN-Heap (lowest price at root).

Python's `heapq` module implements a Min-Heap. 
To simulate a Max-Heap for bids, we negate the price before pushing to the heap.
"""

import heapq
from typing import List, Tuple, Optional
from datetime import datetime
from .schema import Transaction

class OrderBook:
    """
    In-memory Limit Order Book.
    
    Attributes:
        bids (List): A heap of buy orders. 
                     Format: (-price, timestamp, agent_id, item)
                     Note the negative price for Max-Heap simulation.
        asks (List): A heap of sell orders. 
                     Format: (price, timestamp, agent_id, item)
    """

    def __init__(self):
        # Buy orders: Max-heap (store negative price to simulate max-heap with python's min-heap)
        self.bids: List[Tuple[float, float, str, str]] = []
        
        # Sell orders: Min-heap
        self.asks: List[Tuple[float, float, str, str]] = []

    def add_buy(self, agent_id: str, item: str, price: float) -> Optional[Transaction]:
        """
        Processes a BUY order (Bid).
        
        Logic:
        1. Check if there is a matching SELL order (Ask) with price <= Bid Price.
        2. If match found: Execute trade at the ASK price (Maker's price).
        3. If no match: Add the Bid to the order book.

        Args:
            agent_id (str): ID of the agent placing the order.
            item (str): Asset name.
            price (float): Limit price agent is willing to pay.

        Returns:
            Optional[Transaction]: A Transaction object if a trade executed, otherwise None.
        """
        timestamp = datetime.utcnow().timestamp()
        
        # Check if we can match with existing sell orders (asks)
        # Lowest ask is at asks[0] (Min-Heap Root)
        if self.asks:
            best_ask_price, ask_ts, seller_id, ask_item = self.asks[0]
            
            # If the lowest ask is cheap enough for the buyer
            if price >= best_ask_price:
                # MATCH! Remove the ask from the book
                heapq.heappop(self.asks)
                
                # Execution happens at the Maker's price (the one already in the book)
                execution_price = best_ask_price
                
                return Transaction(
                    buyer_id=agent_id,
                    seller_id=seller_id,
                    item=item,
                    price=execution_price,
                    timestamp=datetime.utcnow()
                )
        
        # No match found, add to order book as a resting order
        # Push (-price) to simulate Max-Heap behavior with heapq
        heapq.heappush(self.bids, (-price, timestamp, agent_id, item))
        return None

    def add_sell(self, agent_id: str, item: str, price: float) -> Optional[Transaction]:
        """
        Processes a SELL order (Ask).
        
        Logic:
        1. Check if there is a matching BUY order (Bid) with price >= Ask Price.
        2. If match found: Execute trade at the BID price (Maker's price).
        3. If no match: Add the Ask to the order book.

        Args:
            agent_id (str): ID of the agent placing the order.
            item (str): Asset name.
            price (float): Limit price agent is willing to sell for.

        Returns:
            Optional[Transaction]: A Transaction object if a trade executed, otherwise None.
        """
        timestamp = datetime.utcnow().timestamp()
        
        # Check if we can match with existing buy orders (bids)
        # Highest bid is at bids[0] (stored as negative value)
        if self.bids:
            neg_best_bid_price, bid_ts, buyer_id, bid_item = self.bids[0]
            best_bid_price = -neg_best_bid_price
            
            # If the highest bid is high enough for the seller
            if best_bid_price >= price:
                # MATCH! Remove the bid from the book
                heapq.heappop(self.bids)
                
                # Execution happens at the Maker's price (the bid price)
                execution_price = best_bid_price
                
                return Transaction(
                    buyer_id=buyer_id,
                    seller_id=agent_id,
                    item=item,
                    price=execution_price,
                    timestamp=datetime.utcnow()
                )
        
        # No match found, add to order book as a resting order
        heapq.heappush(self.asks, (price, timestamp, agent_id, item))
        return None

    def get_summary(self) -> dict:
        """
        Returns a simplified summary of the current order book state.
        
        Useful for public feeds or agent observation.
        
        Returns:
            dict: {
                "best_bid": float | None,
                "best_ask": float | None,
                "bids_count": int,
                "asks_count": int
            }
        """
        # Best bid is at index 0 (negated)
        best_bid = -self.bids[0][0] if self.bids else None
        
        # Best ask is at index 0
        best_ask = self.asks[0][0] if self.asks else None
        
        return {
            "best_bid": best_bid,
            "best_ask": best_ask,
            "bids_count": len(self.bids),
            "asks_count": len(self.asks)
        }