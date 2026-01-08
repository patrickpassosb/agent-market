"""
Tests for Portfolio accounting behavior.
"""

import pytest
from src.agents.portfolio import Portfolio


class TestPortfolio:
    """Unit tests for Portfolio P/L tracking"""
    
    def test_initialization(self):
        """Test portfolio starts with correct defaults"""
        p = Portfolio()
        assert p.cash == 10000.0
        assert len(p.positions) == 0
        assert p.realized_pnl == 0.0
    
    def test_execute_buy_success(self):
        """Test buying with sufficient funds"""
        p = Portfolio(cash=1000.0)
        success = p.execute_buy("AAPL", 10, 50.0)  # Buy 10 @ $50
        
        assert success is True
        assert p.cash == 500.0  # 1000 - (10 * 50)
        assert p.positions["AAPL"] == 10
    
    def test_execute_buy_insufficient_funds(self):
        """Test buying with insufficient cash"""
        p = Portfolio(cash=100.0)
        success = p.execute_buy("AAPL", 10, 50.0)  # Need $500, have $100
        
        assert success is False
        assert p.cash == 100.0  # Unchanged
        assert "AAPL" not in p.positions
    
    def test_execute_sell_success(self):
        """Test selling existing position"""
        p = Portfolio(cash=1000.0)
        p.execute_buy("AAPL",  10, 50.0)  # Buy 10 @ $50
        
        # Sell 5 @ $60 (profit of $10 per share)
        success = p.execute_sell("AAPL", 5, 60.0)
        
        assert success is True
        assert p.positions["AAPL"] == 5  # 10 - 5
        assert p.realized_pnl == 50.0  # (60 - 50) * 5
        assert p.cash == 800.0  # 500 + (5 * 60)
    
    def test_execute_sell_insufficient_inventory(self):
        """Test selling without holding the asset"""
        p = Portfolio()
        success = p.execute_sell("AAPL", 10, 50.0)
        
        assert success is False
        assert p.cash == 10000.0  # Unchanged
    
    def test_pnl_calculation(self):
        """Test profit/loss tracking"""
        p = Portfolio(cash=1000.0)
        
        # Buy 10 @ $50
        p.execute_buy("AAPL", 10, 50.0)
        
        current_prices = {"AAPL": 60.0}
        
        # Unrealized P/L: (60 - 50) * 10 = $100
        assert p.get_unrealized_pnl(current_prices) == 100.0
        assert p.get_total_pnl(current_prices) == 100.0  # No realized yet
        
        # Sell 5 @ $60
        p.execute_sell("AAPL", 5, 60.0)
        
        # Realized: (60 - 50) * 5 = $50
        # Unrealized: (60 - 50) * 5 = $50
        # Total: $100
        assert p.realized_pnl == 50.0
        assert p.get_unrealized_pnl(current_prices) == 50.0
        assert p.get_total_pnl(current_prices) == 100.0
    
    def test_portfolio_value(self):
        """Test total wealth calculation"""
        p = Portfolio(cash=1000.0)
        p.execute_buy("AAPL", 10, 50.0)
        
        current_prices = {"AAPL": 60.0}
        
        # Cash: $500, Positions: 10 * $60 = $600
        # Total: $1100
        assert p.get_portfolio_value(current_prices) == 1100.0
    
    def test_roi_calculation(self):
        """Test ROI percentage"""
        p = Portfolio(cash=10000.0)
        p.execute_buy("AAPL", 100, 50.0)  # Spend $5000
        
        current_prices = {"AAPL": 60.0}  # Price rises to $60
        
        metrics = p.get_metrics(current_prices)
        
        # P/L: (60 - 50) * 100 = $1000
        # ROI: (1000 / 10000) * 100 = 10%
        assert metrics["total_pnl"] == 1000.0
        assert metrics["roi"] == 10.0
