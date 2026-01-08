import pytest
from src.market.order_book import OrderBook


class TestOrderBook:
    """Unit tests for OrderBook matching logic"""
    
    def test_initialization(self):
        """Test that OrderBook initializes with empty queues"""
        book = OrderBook()
        summary = book.get_summary()
        assert summary["best_bid"] is None
        assert summary["best_ask"] is None
        assert summary["bids_count"] == 0
        assert summary["asks_count"] == 0
    
    def test_add_buy_order(self):
        """Test adding a buy order updates the book"""
        book = OrderBook()
        result = book.add_buy("agent_1", "AAPL", 10.0)
        
        # Should not match (no sellers), returns None
        assert result is None
        
        summary = book.get_summary()
        assert summary["best_bid"] == 10.0
        assert summary["bids_count"] == 1
    
    def test_add_sell_order(self):
        """Test adding a sell order updates the book"""
        book = OrderBook()
        result = book.add_sell("agent_1", "AAPL", 9.0)
        
        # Should not match (no buyers), returns None
        assert result is None
        
        summary = book.get_summary()
        assert summary["best_ask"] == 9.0
        assert summary["asks_count"] == 1
    
    def test_match_compatible_orders(self):
        """Test that compatible buy/sell orders match"""
        book = OrderBook()
        
        # Seller wants 9, adds first (becomes maker)
        book.add_sell("seller", "AAPL", 9.0)
        
        # Buyer offers 10 -> Should match at 9 (maker price)
        match = book.add_buy("buyer", "AAPL", 10.0)
        
        assert match is not None
        assert match.buyer_id == "buyer"
        assert match.seller_id == "seller"
        assert match.price == 9.0  # Maker's price (seller was first)
    
    def test_no_match_when_prices_incompatible(self):
        """Test that incompatible prices don't match"""
        book = OrderBook()
        
        # Buyer offers 5
        book.add_buy("buyer", "AAPL", 5.0)
        
        # Seller wants 10 -> No match
        match = book.add_sell("seller", "AAPL", 10.0)
        assert match is None
        
        # Both should remain in book
        summary = book.get_summary()
        assert summary["best_bid"] == 5.0
        assert summary["best_ask"] == 10.0
    
    def test_multiple_matches(self):
        """Test that multiple sequential matches work"""
        book = OrderBook()
        
        book.add_sell("seller1", "AAPL", 10.0)
        book.add_sell("seller2", "AAPL", 11.0)
        
        # First buyer takes seller1 at 10
        match1 = book.add_buy("buyer1", "AAPL", 12.0)
        assert match1 is not None
        assert match1.price == 10.0
        
        # Second buyer takes seller2 at 11
        match2 = book.add_buy("buyer2", "AAPL", 12.0)
        assert match2 is not None
        assert match2.price == 11.0
        
        # No more sellers
        summary = book.get_summary()
        assert summary["asks_count"] == 0

    def test_no_match_across_items(self):
        """Orders for different items should not match"""
        book = OrderBook()

        book.add_sell("seller", "MSFT", 9.0)
        match = book.add_buy("buyer", "AAPL", 10.0)

        assert match is None
        summary = book.get_summary()
        assert summary["bids_count"] == 1
        assert summary["asks_count"] == 1
