"""
Tests for Trader decision-making and error handling.
"""

import pytest
from unittest.mock import Mock, patch
from src.agents.trader import Trader
from src.market.schema import MarketState, AgentAction


class TestTrader:
    """Unit tests for Trader agent logic"""
    
    @pytest.fixture
    def mock_market_state(self):
        """Create a mock market state"""
        return MarketState(
            current_price=10.0,
            order_book_summary={
                "best_bid": 9.5,
                "best_ask": 10.5,
                "bids_count": 3,
                "asks_count": 2
            }
        )
    
    def test_trader_initialization(self):
        """Test that Trader initializes with correct attributes"""
        trader = Trader(
            agent_id="test_agent",
            persona="A cautious value investor",
            model_name="groq/llama-3.1-8b-instant"
        )
        
        assert trader.id == "test_agent"
        assert trader.persona == "A cautious value investor"
        assert trader.model_name == "groq/llama-3.1-8b-instant"
    
    @patch('src.agents.trader.completion')
    def test_act_returns_valid_decision(self, mock_completion, mock_market_state):
        """Test that act() returns a properly structured decision"""
        # Mock LLM response - note lowercase action and item field
        mock_completion.return_value = Mock(
            choices=[Mock(
                message=Mock(
                    content='{"action": "buy", "item": "AAPL", "price": 10.0, "reasoning": "Test reason"}'
                )
            )]
        )
        
        trader = Trader("agent_1", "Test persona", "groq/llama-3.1-8b-instant")
        decision = trader.act(
            market_state=mock_market_state, 
            focused_item="AAPL",
            all_current_prices={"AAPL": 10.0}
        )
        
        assert decision is not None
        assert decision["action"] == AgentAction.BUY
        assert decision["price"] == 10.0
        assert "reasoning" in decision
    
    @patch('src.agents.trader.completion')
    def test_act_handles_llm_failure_gracefully(self, mock_completion, mock_market_state):
        """Test that act() handles LLM errors without crashing"""
        # Mock LLM failure
        mock_completion.side_effect = Exception("API Error")
        
        trader = Trader("agent_1", "Test persona", "groq/llama-3.1-8b-instant")
        decision = trader.act(
            market_state=mock_market_state,
            focused_item="AAPL",
            all_current_prices={"AAPL": 10.0}
        )
        
        # Should return None or default action, not crash
        assert decision is None or isinstance(decision, dict)
    
    @patch('src.agents.trader.completion')
    def test_act_with_reflection_action(self, mock_completion, mock_market_state):
        """Test that reflection actions are handled"""
        mock_completion.return_value = Mock(
            choices=[Mock(
                message=Mock(
                    content='{"action": "reflection", "item": "AAPL", "price": 0.0, "reasoning": "Waiting for better price"}'
                )
            )]
        )
        
        trader = Trader("agent_1", "Patient investor", "groq/llama-3.1-8b-instant")
        decision = trader.act(
            market_state=mock_market_state,
            focused_item="AAPL",
            all_current_prices={"AAPL": 10.0}
        )
        
        # Reflection returns a dict but with REFLECTION action
        assert decision is not None
        assert decision["action"] == AgentAction.REFLECTION

    @patch('src.agents.trader.completion')
    def test_act_handles_dict_content(self, mock_completion, mock_market_state):
        """Test that act() handles already-parsed dict content"""
        mock_completion.return_value = Mock(
            choices=[Mock(
                message=Mock(
                    content={"action": "buy", "item": "AAPL", "price": 10.0, "reasoning": "Parsed dict"}
                )
            )]
        )

        trader = Trader("agent_1", "Test persona", "groq/llama-3.1-8b-instant")
        decision = trader.act(
            market_state=mock_market_state,
            focused_item="AAPL",
            all_current_prices={"AAPL": 10.0}
        )

        assert decision is not None
        assert decision["action"] == AgentAction.BUY