"""
Tests for MarketEngine validation, routing, and economic logic.
"""

import os
import tempfile
from unittest.mock import MagicMock

import pytest

from src.market.engine import MarketEngine
from src.market.schema import AgentAction, Transaction, SUPPORTED_ASSETS
from src.agents.portfolio import Portfolio


@pytest.fixture
def temp_db():
    """Create a temporary SQLite database file for tests."""
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    yield path
    if os.path.exists(path):
        os.remove(path)


@pytest.fixture
def engine(temp_db):
    """Create a MarketEngine instance with a temporary DB."""
    return MarketEngine(temp_db)


@pytest.fixture
def mock_agent():
    """Create a mock agent with a real Portfolio."""
    agent = MagicMock()
    agent.id = "agent_1"
    agent.portfolio = Portfolio(cash=10.0)
    return agent


@pytest.mark.parametrize("price", [-1.0, 0.0, float("nan"), float("inf")])
def test_process_action_rejects_invalid_price(engine, price):
    """Ensure invalid prices are rejected without touching the order book."""
    result = engine.process_action(MagicMock(), AgentAction.BUY, "AAPL", price)

    assert result is None
    summary = engine.order_book.get_summary("AAPL")
    assert summary["bids_count"] == 0
    assert summary["asks_count"] == 0


def test_process_action_rejects_empty_item(engine):
    """Ensure empty item names are rejected without touching the order book."""
    result = engine.process_action(MagicMock(), AgentAction.SELL, "", 10.0)

    assert result is None
    summary = engine.order_book.get_summary("AAPL")
    assert summary["bids_count"] == 0
    assert summary["asks_count"] == 0


def test_get_global_sentiment(engine):
    """Test global sentiment calculation based on order book state."""
    # Initial state should be Neutral (50% bullish)
    sentiment = engine.get_global_sentiment()
    assert sentiment["label"] == "Neutral"
    assert sentiment["bullish_pct"] == 50.0

    # Add some bids to make it bullish
    engine.order_book.add_buy("agent_2", "AAPL", 5.0)
    sentiment = engine.get_global_sentiment()
    assert sentiment["label"] == "Super Bullish"
    assert sentiment["bullish_pct"] == 100.0

    # Add more asks to shift sentiment
    engine.order_book.add_sell("agent_3", "AAPL", 6.0)
    engine.order_book.add_sell("agent_4", "AAPL", 7.0)
    engine.order_book.add_sell("agent_5", "AAPL", 8.0)
    # 1 bid, 3 asks -> 1/4 = 25% bullish
    sentiment = engine.get_global_sentiment()
    assert sentiment["label"] == "Bearish"
    assert sentiment["bullish_pct"] == 25.0


def test_process_action_buy_match(engine, mock_agent):
    """Test successful BUY match and portfolio update."""
    # Add a sell order first to match against
    engine.order_book.add_sell("agent_seller", "AAPL", 5.0)
    
    # Process BUY action at same price
    tx = engine.process_action(mock_agent, AgentAction.BUY, "AAPL", 5.0)
    
    assert isinstance(tx, Transaction)
    assert tx.price == 5.0
    assert tx.item == "AAPL"
    assert mock_agent.portfolio.cash == 5.0
    assert mock_agent.portfolio.positions["AAPL"] == 1
    assert engine.current_prices["AAPL"] == 5.0
    assert engine.total_volume == 1


def test_process_action_sell_match(engine, mock_agent):
    """Test successful SELL match and portfolio update."""
    # Give agent some assets to sell
    mock_agent.portfolio.execute_buy("AAPL", 1, 0.0)
    initial_cash = mock_agent.portfolio.cash

    # Add a buy order first to match against
    engine.order_book.add_buy("agent_buyer", "AAPL", 8.0)
    
    # Process SELL action
    tx = engine.process_action(mock_agent, AgentAction.SELL, "AAPL", 8.0)
    
    assert isinstance(tx, Transaction)
    assert tx.price == 8.0
    assert mock_agent.portfolio.cash == initial_cash + 8.0
    assert mock_agent.portfolio.positions.get("AAPL", 0) == 0


def test_process_action_insufficient_funds(engine, mock_agent):
    """Test BUY failure due to insufficient portfolio cash."""
    mock_agent.portfolio.cash = 1.0
    engine.order_book.add_sell("agent_seller", "AAPL", 5.0)
    
    tx = engine.process_action(mock_agent, AgentAction.BUY, "AAPL", 5.0)
    
    assert tx is None
    assert mock_agent.portfolio.cash == 1.0
    assert "AAPL" not in mock_agent.portfolio.positions


def test_process_action_insufficient_assets(engine, mock_agent):
    """Test SELL failure due to insufficient portfolio assets."""
    # Agent has no AAPL
    engine.order_book.add_buy("agent_buyer", "AAPL", 5.0)
    
    tx = engine.process_action(mock_agent, AgentAction.SELL, "AAPL", 5.0)
    
    assert tx is None
    assert mock_agent.portfolio.cash == 10.0


def test_get_market_metrics(engine):
    """Test market metrics calculation."""
    # Low volatility
    engine.price_history["AAPL"] = [1.0, 1.01, 0.99, 1.0]
    metrics = engine.get_market_metrics()
    assert metrics["volatility"] == "Low"
    
    # High volatility
    engine.price_history["TSLA"] = [1.0, 1.5, 0.5, 2.0]
    metrics = engine.get_market_metrics()
    assert metrics["volatility"] in ["High", "Extreme"]
    assert metrics["volatility_index"] > 0


def test_negotiate_price(engine):
    """Test price negotiation logic."""
    engine.order_book.add_sell("seller", "AAPL", 10.0)
    # Agent wants to buy at 8.0, seller is at 10.0
    new_price, details = engine.negotiate_price("agent_1", AgentAction.BUY, "AAPL", 8.0)
    assert new_price == 9.0 # (8+10)/2
    assert details["kind"] == "negotiation"
    assert details["price"] == 9.0

    engine.order_book.add_buy("buyer", "TSLA", 20.0)
    # Agent wants to sell at 30.0, buyer is at 20.0
    new_price, details = engine.negotiate_price("agent_1", AgentAction.SELL, "TSLA", 30.0)
    assert new_price == 25.0 # (30+20)/2
    assert details["price"] == 25.0


def test_get_state(engine):
    """Test market state construction."""
    state = engine.get_state("AAPL")
    assert state.current_price == 0.005 # Default seed price
    assert "best_bid" in state.order_book_summary
