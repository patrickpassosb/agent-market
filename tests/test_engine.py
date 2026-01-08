"""
Tests for MarketEngine validation and routing behavior.
"""

import os
import tempfile

import pytest

from src.market.engine import MarketEngine
from src.market.schema import AgentAction


@pytest.fixture
def temp_db():
    """Create a temporary SQLite database file for tests."""
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    yield path
    if os.path.exists(path):
        os.remove(path)


@pytest.mark.parametrize("price", [-1.0, 0.0, float("nan"), float("inf")])
def test_process_action_rejects_invalid_price(temp_db, price):
    """Ensure invalid prices are rejected without touching the order book."""
    engine = MarketEngine(temp_db)

    result = engine.process_action("agent_1", AgentAction.BUY, "AAPL", price)

    assert result is None
    # Access the specific order book for AAPL
    summary = engine.order_books["AAPL"].get_summary()
    assert summary["bids_count"] == 0
    assert summary["asks_count"] == 0


def test_process_action_rejects_empty_item(temp_db):
    """Ensure empty item names are rejected without touching the order book."""
    engine = MarketEngine(temp_db)

    result = engine.process_action("agent_1", AgentAction.SELL, "", 10.0)

    assert result is None
    # Check any order book (e.g. AAPL) to ensure it's empty
    summary = engine.order_books["AAPL"].get_summary()
    assert summary["bids_count"] == 0
    assert summary["asks_count"] == 0