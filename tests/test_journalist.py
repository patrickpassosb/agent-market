"""
Tests for the JournalistAgent narrative generation.
"""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock

from src.agents.journalist import JournalistAgent
from src.market.schema import MarketState, Transaction


def _make_market_state():
    """Return a minimal MarketState with stable book values."""
    return MarketState(
        current_price=10.0,
        order_book_summary={"best_bid": 9.0, "best_ask": 11.0, "bids_count": 1, "asks_count": 1}
    )


@pytest.mark.asyncio
@patch("src.agents.journalist.acompletion", new_callable=AsyncMock)
async def test_analyze_trend_rising_from_desc_order(mock_acompletion):
    """Ensure trend detection handles newest-first transactions."""
    captured = {}

    async def _mock_acompletion(**kwargs):
        """Capture prompt content and return a fixed response."""
        captured["prompt"] = kwargs["messages"][0]["content"]
        return MagicMock(choices=[MagicMock(message=MagicMock(content={"headline": "h", "body": "b"}))])

    mock_acompletion.side_effect = _mock_acompletion

    agent = JournalistAgent(model_name="gemini/gemini-2.5-flash")
    market_state = _make_market_state()

    tx_old = Transaction(buyer_id="b1", seller_id="s1", item="AAPL", price=10.0)
    tx_new = Transaction(buyer_id="b2", seller_id="s2", item="AAPL", price=12.0)

    await agent.analyze(market_state, [tx_new, tx_old])  # newest-first order

    assert "Trend: rising" in captured["prompt"]