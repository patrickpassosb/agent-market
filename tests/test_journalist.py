from unittest.mock import Mock, patch

from src.agents.journalist import JournalistAgent
from src.market.schema import MarketState, Transaction


def _make_market_state():
    return MarketState(
        current_price=10.0,
        order_book_summary={"best_bid": 9.0, "best_ask": 11.0, "bids_count": 1, "asks_count": 1}
    )


@patch("src.agents.journalist.completion")
def test_analyze_trend_rising_from_desc_order(mock_completion):
    captured = {}

    def _mock_completion(**kwargs):
        captured["prompt"] = kwargs["messages"][0]["content"]
        return Mock(choices=[Mock(message=Mock(content={"headline": "h", "body": "b"}))])

    mock_completion.side_effect = _mock_completion

    agent = JournalistAgent(model_name="gemini/gemini-1.5-flash")
    market_state = _make_market_state()

    tx_old = Transaction(buyer_id="b1", seller_id="s1", item="AAPL", price=10.0)
    tx_new = Transaction(buyer_id="b2", seller_id="s2", item="AAPL", price=12.0)

    agent.analyze(market_state, [tx_new, tx_old])  # newest-first order

    assert "Trend: rising" in captured["prompt"]
