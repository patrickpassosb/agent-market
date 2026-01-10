"""
Tests for analysis and report generation modules.
"""

import os
import tempfile
from datetime import UTC, datetime
from unittest.mock import MagicMock, patch

import pytest

from src.analysis.chart import plot_market_history
from src.analysis.report import generate_report
from src.market.ledger import Ledger
from src.market.schema import InteractionLog, Transaction


@pytest.fixture
def temp_dir():
    with tempfile.TemporaryDirectory() as tmp:
        yield tmp

def test_plot_market_history(temp_dir):
    # Create a dummy DB using Ledger to ensure schema is correct
    db_path = os.path.join(temp_dir, "test_market.db")
    ledger = Ledger(db_path)
    
    # Insert a transaction
    tx = Transaction(
        run_id="run_1", 
        buyer_id="Agent_1", 
        seller_id="Agent_2", 
        item="AAPL", 
        price=150.0,
        timestamp=datetime.now(UTC)
    )
    ledger.record_transaction(tx)

    output_dir = os.path.join(temp_dir, "plots")
    
    with patch("matplotlib.pyplot.savefig"):
        plot_market_history(db_path, output_dir)
    
    assert os.path.exists(output_dir)

def test_generate_report(temp_dir):
    db_path = os.path.join(temp_dir, "test_report.db")
    ledger = Ledger(db_path)
    
    # Insert data
    tx = Transaction(
        run_id="run_1", 
        buyer_id="Agent_1", 
        seller_id="Agent_2", 
        item="AAPL", 
        price=0.01,
        timestamp=datetime.now(UTC)
    )
    ledger.record_transaction(tx)
    
    log = InteractionLog(
        run_id="run_1", 
        agent_id="Agent_1", 
        kind="action", 
        action="buy", 
        item="AAPL", 
        price=0.01, 
        details="Test",
        timestamp=datetime.now(UTC)
    )
    ledger.record_interaction(log)

    mock_agent = MagicMock()
    mock_agent.id = "Agent_1"
    mock_agent.persona = "Conservative"
    mock_agent.portfolio.get_metrics.return_value = {
        "cash": 1.0,
        "portfolio_value": 1.1,
        "total_pnl": 0.1,
        "roi": 10.0,
        "trades_count": 1
    }

    with patch("matplotlib.pyplot.savefig"):
        report_dir = generate_report(
            run_id="run_1",
            db_path=db_path,
            report_root=temp_dir,
            agents=[mock_agent],
            current_prices={"AAPL": 0.01}
        )
    
    assert os.path.exists(os.path.join(report_dir, "report.md"))
    assert os.path.exists(os.path.join(temp_dir, "index.json"))
