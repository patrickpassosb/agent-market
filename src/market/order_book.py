"""
Order Book Implementation.

This module implements a standard Limit Order Book using binary heaps.
It supports adding buy (bid) and sell (ask) orders and matching them efficiently.

Matching Engine Logic:
- **Price-Time Priority**: Better prices match first. If prices are equal, earlier orders
  match first.
- **Bids (Buys)**: Maintained in a MAX-Heap (highest price at root).
- **Asks (Sells)**: Maintained in a MIN-Heap (lowest price at root).

Python's `heapq` module implements a Min-Heap.
To simulate a Max-Heap for bids, we negate the price before pushing to the heap.
"""

import heapq
from dataclasses import dataclass
from datetime import UTC, datetime

from .schema import Transaction


@dataclass(frozen=True)
class OrderMatch:
    transaction: Transaction
    maker_order: tuple[float, float, str]
    maker_is_bid: bool


class OrderBook:
    """
    In-memory Limit Order Book.

    Attributes:
        bids (Dict[str, List]): Per-item heap of buy orders.
                                Format: (-price, timestamp, agent_id)
                                Note the negative price for Max-Heap simulation.
        asks (Dict[str, List]): Per-item heap of sell orders.
                                Format: (price, timestamp, agent_id)
    """

    def __init__(self):
        """Initialize empty bid/ask heaps per item."""
        # Buy orders: Max-heap per item (store negative price for min-heap).
        self.bids: dict[str, list[tuple[float, float, str]]] = {}
        # Sell orders: Min-heap per item
        self.asks: dict[str, list[tuple[float, float, str]]] = {}

    def _get_bids(self, item: str) -> list[tuple[float, float, str]]:
        """
        Retrieve the bid heap for a specific item.
        Creates a new list if one doesn't exist.

        Args:
            item (str): The asset identifier.

        Returns:
            List: The heap list for bids on this item.
        """
        return self.bids.setdefault(item, [])

    def _get_asks(self, item: str) -> list[tuple[float, float, str]]:
        """
        Retrieve the ask heap for a specific item.
        Creates a new list if one doesn't exist.

        Args:
            item (str): The asset identifier.

        Returns:
            List: The heap list for asks on this item.
        """
        return self.asks.setdefault(item, [])

    def add_buy(self, agent_id: str, item: str, price: float) -> OrderMatch | None:
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
            Optional[OrderMatch]: A match result if a trade executed, otherwise None.
        """
        # Context7 /python/cpython (datetime docs).
        timestamp = datetime.now(UTC).timestamp()

        # Check if we can match with existing sell orders (asks) for this item
        # Lowest ask is at asks[0] (Min-Heap Root)
        asks = self._get_asks(item)
        if asks:
            best_ask_price, ask_ts, seller_id = asks[0]

            # If the lowest ask is cheap enough for the buyer
            if price >= best_ask_price:
                # MATCH! Remove the ask from the book
                maker_order = heapq.heappop(asks)

                # Execution happens at the Maker's price (the one already in the book)
                execution_price = best_ask_price

                return OrderMatch(
                    transaction=Transaction(
                        buyer_id=agent_id,
                        seller_id=seller_id,
                        item=item,
                        price=execution_price,
                        timestamp=datetime.now(UTC),
                    ),
                    maker_order=maker_order,
                    maker_is_bid=False,
                )

        # No match found, add to order book as a resting order
        # Push (-price) to simulate Max-Heap behavior with heapq
        bids = self._get_bids(item)
        heapq.heappush(bids, (-price, timestamp, agent_id))
        return None

    def add_sell(self, agent_id: str, item: str, price: float) -> OrderMatch | None:
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
            Optional[OrderMatch]: A match result if a trade executed, otherwise None.
        """
        # Context7 /python/cpython (datetime docs).
        timestamp = datetime.now(UTC).timestamp()

        # Check if we can match with existing buy orders (bids) for this item
        # Highest bid is at bids[0] (stored as negative value)
        bids = self._get_bids(item)
        if bids:
            neg_best_bid_price, bid_ts, buyer_id = bids[0]
            best_bid_price = -neg_best_bid_price

            # If the highest bid is high enough for the seller
            if best_bid_price >= price:
                # MATCH! Remove the bid from the book
                maker_order = heapq.heappop(bids)

                # Execution happens at the Maker's price (the bid price)
                execution_price = best_bid_price

                return OrderMatch(
                    transaction=Transaction(
                        buyer_id=buyer_id,
                        seller_id=agent_id,
                        item=item,
                        price=execution_price,
                        timestamp=datetime.now(UTC),
                    ),
                    maker_order=maker_order,
                    maker_is_bid=True,
                )

        # No match found, add to order book as a resting order
        asks = self._get_asks(item)
        heapq.heappush(asks, (price, timestamp, agent_id))
        return None

    def get_summary(self, item: str | None = None) -> dict:
        """
        Returns a simplified summary of the current order book state.

        Args:
            item (Optional[str]): If provided, returns summary for this asset only.
                                 Otherwise, returns an aggregate summary.

        Returns:
            dict: {
                "best_bid": float | None,
                "best_ask": float | None,
                "bids_count": int,
                "asks_count": int
            }
        """
        if item:
            bids = self.bids.get(item, [])
            asks = self.asks.get(item, [])
            best_bid = -bids[0][0] if bids else None
            best_ask = asks[0][0] if asks else None
            return {
                "best_bid": best_bid,
                "best_ask": best_ask,
                "bids_count": len(bids),
                "asks_count": len(asks),
            }

        # Global aggregation (fallback)
        best_bid = None
        for heap in self.bids.values():
            if not heap:
                continue
            price = -heap[0][0]
            if best_bid is None or price > best_bid:
                best_bid = price

        best_ask = None
        for heap in self.asks.values():
            if not heap:
                continue
            price = heap[0][0]
            if best_ask is None or price < best_ask:
                best_ask = price

        return {
            "best_bid": best_bid,
            "best_ask": best_ask,
            "bids_count": sum(len(heap) for heap in self.bids.values()),
            "asks_count": sum(len(heap) for heap in self.asks.values()),
        }

    def restore_order(
        self,
        item: str,
        maker_is_bid: bool,
        maker_order: tuple[float, float, str],
    ) -> None:
        """
        Restore a previously popped maker order back into the order book.
        """
        # Context7 /python/cpython (heapq docs).
        if maker_is_bid:
            heapq.heappush(self._get_bids(item), maker_order)
        else:
            heapq.heappush(self._get_asks(item), maker_order)

    def get_best_quotes(self, item: str) -> tuple[float | None, float | None]:
        """
        Returns the best bid and ask for a specific item.
        """
        bids = self.bids.get(item, [])
        asks = self.asks.get(item, [])
        best_bid = -bids[0][0] if bids else None
        best_ask = asks[0][0] if asks else None
        return best_bid, best_ask

    def reinsert_order(
        self,
        agent_id: str,
        item: str,
        price: float,
        is_buy: bool,
    ):
        """
        Puts an order back onto the book (e.g., if a match occurred but taker failed).
        Note: This doesn't preserve exact original timestamp but prevents order loss.
        """
        timestamp = datetime.now(UTC).timestamp()
        if is_buy:
            heapq.heappush(self._get_bids(item), (-float(price), timestamp, agent_id))
        else:
            heapq.heappush(self._get_asks(item), (float(price), timestamp, agent_id))
