"""
Market Engine (Facade).

This module serves as the central controller for the market simulation.
It follows the **Facade Pattern**, providing a simplified interface to the
complex underlying subsystems: the OrderBook (matching) and the Ledger (persistence).

Responsibilities:
1. Maintain the current state of the market (Last Price) for each asset.
2. Route agent actions to the correct Order Book (AAPL, TSLA, etc.).
3. Record successful trades in the Ledger.
4. Expose market state to agents.
"""

import math
from typing import Any

from .ledger import Ledger
from .order_book import OrderBook
from .schema import SUPPORTED_ASSETS, AgentAction, MarketState, Transaction


class MarketEngine:
    """
    The main engine driving the market logic.

    Attributes:
        ledger (Ledger): Handle to the database.
        order_books (Dict[str, OrderBook]): One matching engine per supported asset.
        current_prices (Dict[str, float]): Last trade price for each asset (in BTC).
    """

    def __init__(
        self,
        db_path: str = "market.db",
        run_id: str | None = None,
        initial_price: float = 0.005,  # Default seed price in BTC
    ):
        """
        Initialize the market engine.

        Args:
            db_path (str): Path to the SQLite database file.
        """
        self.ledger = Ledger(db_path)

        # Use a single OrderBook instance for all assets (Phase 3 refactor)
        self.order_book = OrderBook()

        if (
            not isinstance(initial_price, (int, float))
            or not math.isfinite(initial_price)
            or initial_price <= 0
        ):
            initial_price = 0.005

        # Initialize prices for all assets
        self.current_prices: dict[str, float] = {
            asset: float(initial_price) for asset in SUPPORTED_ASSETS
        }

        self.total_volume = 0
        self.price_history: dict[str, list[float]] = {
            asset: [float(initial_price)] for asset in SUPPORTED_ASSETS
        }

        self.run_id = run_id
        self.last_transaction: Transaction | None = None

    def get_global_sentiment(self) -> dict:
        """
        Calculate global sentiment based on total bid/ask counts across the order book.
        """
        summary = self.order_book.get_summary()  # Global aggregate if no item passed.
        total_bids = summary["bids_count"]
        total_asks = summary["asks_count"]

        total = total_bids + total_asks
        bullish_pct = 50.0
        if total > 0:
            bullish_pct = (total_bids / total) * 100

        label = "Neutral"
        if bullish_pct > 85:
            label = "Super Bullish"
        elif bullish_pct > 65:
            label = "Bullish"
        elif bullish_pct < 15:
            label = "Super Bearish"
        elif bullish_pct < 35:
            label = "Bearish"

        return {
            "bullish_pct": round(bullish_pct, 1),
            "label": label,
        }

    def get_state(self, item: str = "AAPL") -> MarketState:
        """
        Constructs and returns the current state of the market for a specific asset.

        This is the "sensor" data provided to agents.

        Args:
            item (str): The ticker symbol to query.

        Returns:
            MarketState: Object containing price and order book summary.
        """
        # Fallback for invalid items
        target_item = item if item in SUPPORTED_ASSETS else SUPPORTED_ASSETS[0]

        summary = self.order_book.get_summary(target_item)
        return MarketState(
            current_price=self.current_prices.get(target_item, 0.0), order_book_summary=summary
        )

    def process_action(
        self,
        agent: Any,
        action: AgentAction,
        item: str,
        price: float = 0.0,
        agent_registry: dict[str, Any] | None = None,
    ) -> Transaction | None:
        """
        Processes an action submitted by an agent.

        This method acts as the central transaction coordinator. It:
        1. Validates the input arguments.
        2. Performs a pre-validation check on the initiating agent's portfolio.
        3. Routes the order to the single `OrderBook`.
        4. If a match occurs, it validates the counterparty's portfolio.
        5. If BOTH are valid, records the transaction and updates BOTH portfolios.

        Args:
            agent (BaseAgent): The agent instance submitting the action.
            action (AgentAction): The type of action (BUY, SELL, HOLD, REFLECTION).
            item (str): The asset involved (e.g. "AAPL", "TSLA").
            price (float): The limit price for the order (in BTC).
            agent_registry (dict): Optional mapping of agent_id to agent instances
                                  for multi-agent portfolio updates.

        Returns:
            Optional[Transaction]: The resulting transaction if a trade occurred, else None.
        """
        # 1. Basic Validation
        if action in (AgentAction.HOLD, AgentAction.REFLECTION):
            return None

        if not isinstance(item, str) or item not in SUPPORTED_ASSETS:
            return None

        if not isinstance(price, (int, float)) or not math.isfinite(price) or price <= 0:
            return None

        # 2. Pre-validate Initiating Agent (Taker)
        if action == AgentAction.BUY:
            if not agent.portfolio.has_funds(float(price)):
                return None
            match = self.order_book.add_buy(agent.id, item, float(price))

        elif action == AgentAction.SELL:
            if not agent.portfolio.has_inventory(item, 1):
                return None
            match = self.order_book.add_sell(agent.id, item, float(price))
        else:
            return None

        # 3. Handle Matching (Taker meets Maker)
        transaction = match.transaction if match else None
        if transaction:
            # We matched an existing order in the book.
            # We must ensure the Maker can still fulfill their side.
            buyer = agent if action == AgentAction.BUY else None
            seller = agent if action == AgentAction.SELL else None

            # Resolve the counterparty from the registry
            if agent_registry:
                if action == AgentAction.BUY:
                    seller = agent_registry.get(transaction.seller_id)
                else:
                    buyer = agent_registry.get(transaction.buyer_id)

            # Atomic Commit: Only execute if BOTH sides are valid
            # If registry is missing, we fallback to partial update (legacy/tests)
            buyer_valid = True
            if buyer and not buyer.portfolio.has_funds(transaction.price):
                buyer_valid = False
            seller_valid = True
            if seller and not seller.portfolio.has_inventory(transaction.item, 1):
                seller_valid = False

            can_execute = buyer_valid and seller_valid
            taker_valid = buyer_valid if action == AgentAction.BUY else seller_valid
            maker_valid = seller_valid if action == AgentAction.BUY else buyer_valid

            if can_execute:
                # COMMIT BOTH SIDES
                if buyer:
                    buyer.portfolio.execute_buy(transaction.item, 1, transaction.price)
                if seller:
                    seller.portfolio.execute_sell(transaction.item, 1, transaction.price)
            else:
                if match and maker_valid and not taker_valid:
                    # Restore maker liquidity if the taker lost funds/inventory mid-tick.
                    self.order_book.restore_order(item, match.maker_is_bid, match.maker_order)
                # Transaction is aborted; maker orders stay removed when maker is invalid.
                return None

        # 4. Finalize Successful Transaction
        if transaction:
            if self.run_id:
                transaction.run_id = self.run_id
            self.ledger.record_transaction(transaction)
            self.last_transaction = transaction

            self.current_prices[item] = transaction.price
            self.total_volume += 1
            self.price_history[item].append(transaction.price)
            if len(self.price_history[item]) > 50:
                self.price_history[item].pop(0)

        return transaction

    def get_recent_transactions(self, limit: int = 100) -> list[Transaction]:
        return self.ledger.get_transactions(limit=limit)

    def get_latest_transaction(self) -> Transaction | None:
        return self.last_transaction

    def get_market_metrics(self) -> dict:
        """
        Calculate global market metrics like volume and volatility.
        """
        # Calculate volatility as average price deviation across all assets
        vol_ratios = []
        for _asset, prices in self.price_history.items():
            if len(prices) < 2:
                continue
            # Simple volatility: (max - min) / avg
            avg = sum(prices) / len(prices)
            if avg > 0:
                vol = (max(prices) - min(prices)) / avg
                vol_ratios.append(vol)

        avg_vol = sum(vol_ratios) / len(vol_ratios) if vol_ratios else 0.0

        vol_label = "Low"
        if avg_vol > 0.15:
            vol_label = "Extreme"
        elif avg_vol > 0.08:
            vol_label = "High"
        elif avg_vol > 0.03:
            vol_label = "Medium"

        return {
            "total_volume": self.total_volume,
            "volatility": vol_label,
            "volatility_index": round(avg_vol * 100, 2),
        }

    def negotiate_price(
        self,
        agent_id: str,
        action: AgentAction,
        item: str,
        price: float,
    ) -> tuple[float, dict | None]:
        """
        Provides a counter-offer price based on current best quotes.
        """
        if item not in SUPPORTED_ASSETS:
            return price, None

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
            if self.run_id:
                details["run_id"] = self.run_id
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
            if self.run_id:
                details["run_id"] = self.run_id
            return counter_price, details

        return price, None
