"""
Tests for Trader decision-making and error handling.
"""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from src.agents.trader import Trader
from src.market.schema import MarketState, AgentAction
from src.utils.personas import PersonaStrategy

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
            strategy=PersonaStrategy.CONSERVATIVE,
            model_name="groq/llama-3.1-8b-instant"
        )
        
        assert trader.id == "test_agent"
        assert trader.strategy == PersonaStrategy.CONSERVATIVE
        assert trader.model_name == "groq/llama-3.1-8b-instant"
    
    @pytest.mark.asyncio
    @patch('src.agents.trader.acompletion', new_callable=AsyncMock)
    async def test_act_returns_valid_decision(self, mock_acompletion, mock_market_state):
        """Test that act() returns a properly structured decision"""
        # Mock LLM response
        mock_acompletion.return_value = MagicMock(
            choices=[MagicMock(
                message=MagicMock(
                    content='{"action": "buy", "item": "AAPL", "price": 10.0, "reasoning": "Test reason"}'
                )
            )]
        )
        
        trader = Trader("agent_1", PersonaStrategy.ALGORITHMIC, "groq/llama-3.1-8b-instant")
        decision = await trader.act(
            market_state=mock_market_state, 
            focused_item="AAPL",
            all_current_prices={"AAPL": 10.0}
        )
        
        assert decision is not None
        assert decision["action"] == AgentAction.BUY
        assert decision["price"] == 10.0
        assert "reasoning" in decision
    
    @pytest.mark.asyncio
    @patch('src.agents.trader.acompletion', new_callable=AsyncMock)
    async def test_act_handles_llm_failure_gracefully(self, mock_acompletion, mock_market_state):
        """Test that act() handles LLM errors without crashing"""
        # Mock LLM failure
        mock_acompletion.side_effect = Exception("API Error")
        
        trader = Trader("agent_1", PersonaStrategy.PANIC, "groq/llama-3.1-8b-instant")
        decision = await trader.act(
            market_state=mock_market_state,
            focused_item="AAPL",
            all_current_prices={"AAPL": 10.0}
        )
        
        # Should return None (HOLD) on total failure
        assert decision is None
    
    @pytest.mark.asyncio
    @patch('src.agents.trader.acompletion', new_callable=AsyncMock)
    async def test_act_with_reflection_action(self, mock_acompletion, mock_market_state):
        """Test that reflection actions are handled"""
        mock_acompletion.return_value = MagicMock(
            choices=[MagicMock(
                message=MagicMock(
                    content='{"action": "reflection", "item": "AAPL", "price": 0.0, "reasoning": "Waiting for better price"}'
                )
            )]
        )
        
        trader = Trader("agent_1", PersonaStrategy.VALUE, "groq/llama-3.1-8b-instant")
        decision = await trader.act(
            market_state=mock_market_state,
            focused_item="AAPL",
            all_current_prices={"AAPL": 10.0}
        )
        
        assert decision is not None
        assert decision["action"] == AgentAction.REFLECTION

    @pytest.mark.asyncio
    @patch('src.agents.trader.acompletion', new_callable=AsyncMock)
    async def test_act_handles_dict_content(self, mock_acompletion, mock_market_state):
        """Test that act() handles already-parsed dict content"""
        mock_acompletion.return_value = MagicMock(
            choices=[MagicMock(
                message=MagicMock(
                    content={"action": "buy", "item": "AAPL", "price": 10.0, "reasoning": "Parsed dict"}
                )
            )]
        )

        trader = Trader("agent_1", PersonaStrategy.MOMENTUM, "groq/llama-3.1-8b-instant")
        decision = await trader.act(
            market_state=mock_market_state,
            focused_item="AAPL",
            all_current_prices={"AAPL": 10.0}
        )

        assert decision is not None
        assert decision["action"] == AgentAction.BUY
