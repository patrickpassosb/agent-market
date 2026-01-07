import heapq
from typing import List, Tuple, Optional
from datetime import datetime
from .schema import Transaction

class OrderBook:
    def __init__(self):
        # Buy orders: Max-heap (store negative price to simulate max-heap with python's min-heap)
        # Format: (-price, timestamp, agent_id, item)
        self.bids: List[Tuple[float, float, str, str]] = []
        
        # Sell orders: Min-heap
        # Format: (price, timestamp, agent_id, item)
        self.asks: List[Tuple[float, float, str, str]] = []

    def add_buy(self, agent_id: str, item: str, price: float) -> Optional[Transaction]:
        """
        Add a buy order. Try to match immediately with lowest ask.
        Returns a Transaction if matched, else None.
        """
        timestamp = datetime.utcnow().timestamp()
        
        # Check if we can match with existing sell orders (asks)
        # Lowest ask is at asks[0]
        if self.asks:
            best_ask_price, ask_ts, seller_id, ask_item = self.asks[0]
            if price >= best_ask_price:
                # MATCH!
                heapq.heappop(self.asks)
                # Use the older order's price (maker's price) - here it's the ask price
                execution_price = best_ask_price
                return Transaction(
                    buyer_id=agent_id,
                    seller_id=seller_id,
                    item=item,
                    price=execution_price,
                    timestamp=datetime.utcnow()
                )
        
        # No match, add to bids
        heapq.heappush(self.bids, (-price, timestamp, agent_id, item))
        return None

    def add_sell(self, agent_id: str, item: str, price: float) -> Optional[Transaction]:
        """
        Add a sell order. Try to match immediately with highest bid.
        Returns a Transaction if matched, else None.
        """
        timestamp = datetime.utcnow().timestamp()
        
        # Check if we can match with existing buy orders (bids)
        # Highest bid is at bids[0] (stored as negative)
        if self.bids:
            neg_best_bid_price, bid_ts, buyer_id, bid_item = self.bids[0]
            best_bid_price = -neg_best_bid_price
            
            if best_bid_price >= price:
                # MATCH!
                heapq.heappop(self.bids)
                # Use the older order's price (maker's price) - here it's the bid price
                execution_price = best_bid_price
                return Transaction(
                    buyer_id=buyer_id,
                    seller_id=agent_id,
                    item=item,
                    price=execution_price,
                    timestamp=datetime.utcnow()
                )
        
        # No match, add to asks
        heapq.heappush(self.asks, (price, timestamp, agent_id, item))
        return None

    def get_summary(self) -> dict:
        best_bid = -self.bids[0][0] if self.bids else None
        best_ask = self.asks[0][0] if self.asks else None
        return {
            "best_bid": best_bid,
            "best_ask": best_ask,
            "bids_count": len(self.bids),
            "asks_count": len(self.asks)
        }
