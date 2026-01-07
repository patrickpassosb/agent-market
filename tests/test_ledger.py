import pytest
import os
import tempfile
from src.market.ledger import Ledger
from src.market.schema import Transaction


class TestLedger:
    """Unit tests for Ledger database persistence"""
    
    @pytest.fixture
    def temp_db(self):
        """Create a temporary database for testing"""
        fd, path = tempfile.mkstemp(suffix=".db")
        os.close(fd)
        yield path
        # Cleanup
        if os.path.exists(path):
            os.remove(path)
    
    def test_initialization(self, temp_db):
        """Test that Ledger initializes database correctly"""
        ledger = Ledger(temp_db)
        assert os.path.exists(temp_db)
    
    def test_record_transaction(self, temp_db):
        """Test recording a transaction"""
        ledger = Ledger(temp_db)
        
        tx = Transaction(
            buyer_id="agent_1",
            seller_id="agent_2",
            item="AAPL",
            price=10.5
        )
        
        ledger.record_transaction(tx)
        
        # Verify it was saved
        transactions = ledger.get_transactions(limit=1)
        assert len(transactions) == 1
        assert transactions[0].buyer_id == "agent_1"
        assert transactions[0].seller_id == "agent_2"
        assert transactions[0].price == 10.5
    
    def test_get_transactions_limit(self, temp_db):
        """Test that limit parameter works"""
        ledger = Ledger(temp_db)
        
        # Add 5 transactions
        for i in range(5):
            tx = Transaction(
                buyer_id=f"buyer_{i}",
                seller_id=f"seller_{i}",
                item="AAPL",
                price=float(i)
            )
            ledger.record_transaction(tx)
        
        # Get last 3
        recent = ledger.get_transactions(limit=3)
        assert len(recent) == 3
        assert recent[0].price == 4.0  # Most recent first
    
    def test_persistence(self, temp_db):
        """Test that data persists across Ledger instances"""
        # Create and record
        ledger1 = Ledger(temp_db)
        tx = Transaction(buyer_id="a", seller_id="b", item="AAPL", price=99.9)
        ledger1.record_transaction(tx)
        
        # Re-open database with new instance
        ledger2 = Ledger(temp_db)
        transactions = ledger2.get_transactions()
        
        assert len(transactions) == 1
        assert transactions[0].price == 99.9
