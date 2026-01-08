"""
Portfolio Management for Trading Agents.

Tracks cash, positions, and calculates profit/loss metrics.
"""

from typing import Dict
import math
from pydantic import BaseModel, Field, ConfigDict, PrivateAttr


class Portfolio(BaseModel):
    """
    Manages an agent's financial state.
    
    Tracks:
    - Cash balance
    - Asset positions (quantity held per item)
    - Trade history for P/L calculation
    """
    
    model_config = ConfigDict()  # Pydantic v2 config style per https://github.com/pydantic/pydantic/blob/main/docs/concepts/config.md (Context7 /pydantic/pydantic)

    cash: float = Field(default=10000.0, description="Available cash balance")
    positions: Dict[str, int] = Field(default_factory=dict, description="Holdings: {item: quantity}")
    realized_pnl: float = Field(default=0.0, description="Locked-in profit/loss from closed positions")
    trades_count: int = Field(default=0, description="Total number of trades executed")
    
    # Cost basis tracking for P/L calculation
    _cost_basis: Dict[str, float] = PrivateAttr(default_factory=dict)  # PrivateAttr per https://github.com/pydantic/pydantic/blob/main/docs/concepts/models.md (Context7 /pydantic/pydantic)
    
    def execute_buy(self, item: str, quantity: int, price: float) -> bool:
        """
        Execute a buy order if sufficient cash.
        
        Returns:
            bool: True if trade executed, False if insufficient funds
        """
        total_cost = quantity * price
        
        if self.cash < total_cost:
            return False  # Insufficient funds
        
        # Update cash
        self.cash -= total_cost
        
        # Update positions and cost basis
        current_qty = self.positions.get(item, 0)
        current_basis = self._cost_basis.get(item, 0.0)
        
        # Calculate new average cost
        total_units = current_qty + quantity
        total_value = (current_qty * current_basis) + (quantity * price)
        new_basis = total_value / total_units if total_units > 0 else 0.0
        
        self.positions[item] = total_units
        self._cost_basis[item] = new_basis
        self.trades_count += 1
        
        return True
    
    def execute_sell(self, item: str, quantity: int, price: float) -> bool:
        """
        Execute a sell order if sufficient inventory.
        
        Returns:
            bool: True if trade executed, False if insufficient inventory
        """
        current_qty = self.positions.get(item, 0)
        
        if current_qty < quantity:
            return False  # Insufficient inventory
        
        # Calculate realized P/L
        cost_basis = self._cost_basis.get(item, 0.0)
        pnl_this_trade = (price - cost_basis) * quantity
        self.realized_pnl += pnl_this_trade
        
        # Update cash
        self.cash += quantity * price
        
        # Update positions
        self.positions[item] = current_qty - quantity
        if self.positions[item] == 0:
            del self.positions[item]
            if item in self._cost_basis:
                del self._cost_basis[item]
        
        self.trades_count += 1
        
        return True
    
    def get_unrealized_pnl(self, current_prices: Dict[str, float]) -> float:
        """
        Calculate unrealized P/L based on current market prices.
        
        Args:
            current_prices: {item: current_market_price}
        """
        unrealized = 0.0
        for item, qty in self.positions.items():
            cost_basis = self._cost_basis.get(item, 0.0)
            market_price = current_prices.get(item, cost_basis)
            unrealized += (market_price - cost_basis) * qty
        
        return unrealized
    
    def get_total_pnl(self, current_prices: Dict[str, float]) -> float:
        """Total P/L = realized + unrealized"""
        return self.realized_pnl + self.get_unrealized_pnl(current_prices)
    
    def get_portfolio_value(self, current_prices: Dict[str, float]) -> float:
        """Total wealth = cash + market value of positions"""
        position_value = sum(
            qty * current_prices.get(item, 0)
            for item, qty in self.positions.items()
        )
        return self.cash + position_value
    
    def get_metrics(self, current_prices: Dict[str, float]) -> dict:
        """
        Return performance metrics for analytics.
        """
        total_pnl = self.get_total_pnl(current_prices)
        initial_capital = 10000.0
        
        return {
            "cash": self.cash,
            "positions": dict(self.positions),
            "realized_pnl": self.realized_pnl,
            "unrealized_pnl": self.get_unrealized_pnl(current_prices),
            "total_pnl": total_pnl,
            "portfolio_value": self.get_portfolio_value(current_prices),
            "roi": (total_pnl / initial_capital) * 100 if initial_capital > 0 else 0.0,
            "trades_count": self.trades_count
        }

    def seed_position(self, item: str, quantity: int, price: float) -> None:
        """
        Seed initial inventory while preserving total portfolio value.
        """
        if quantity <= 0 or not math.isfinite(price) or price <= 0:
            return  # https://github.com/python/cpython/blob/main/Doc/library/math.rst (Context7 /python/cpython)
        total_cost = quantity * price
        if self.cash < total_cost:
            return
        self.cash -= total_cost

        current_qty = self.positions.get(item, 0)
        current_basis = self._cost_basis.get(item, 0.0)
        total_units = current_qty + quantity
        total_value = (current_qty * current_basis) + total_cost
        new_basis = total_value / total_units if total_units > 0 else 0.0

        self.positions[item] = total_units
        self._cost_basis[item] = new_basis
