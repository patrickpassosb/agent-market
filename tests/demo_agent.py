import sys
import os
import json
from unittest.mock import MagicMock, patch

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), "../src"))

from agents.trader import Trader
from market.schema import MarketState, AgentAction

def mock_completion(**kwargs):
    """
    Mock litellm completion to avoid needing real API key for basic verification.
    """
    model = kwargs.get("model")
    print(f"[Mock] Calling model {model}...")
    
    # Return a dummy response in the structure expected by the Agent
    class MockMessage:
        content = json.dumps({
            "action": "sell",
            "item": "apple",
            "price": 9.5,
            "reasoning": "Price is high, taking profit."
        })
    
    class MockChoice:
        message = MockMessage()
        
    class MockResponse:
        choices = [MockChoice()]
        
    return MockResponse()

def main():
    print("--- Starting Agent Demo (Mocked) ---")
    
    # 1. Initialize Trader
    # We use a mocked completion to simulate LLM
    with patch('agents.trader.completion', side_effect=mock_completion):
        agent = Trader(agent_id="test_trader_1", persona="Panic Seller")
        print(f"Agent Initialized: {agent.id} ({agent.persona})")

        # 2. visual Market State
        market_state = MarketState(
            current_price=10.0,
            order_book_summary={"best_bid": 9.0, "best_ask": 11.0}
        )
        print(f"Market State: Price={market_state.current_price}")

        # 3. Agent Acts
        print("Agent is thinking...")
        decision = agent.act(market_state)
        
        # 4. output
        print(f"Agent Decision: {decision}")
        
        # Verify result structure
        if decision:
            assert decision["action"] == AgentAction.SELL
            assert decision["price"] == 9.5
            assert decision["item"] == "apple"
            print("✅ Decision structure verified valid.")
            
        # 5. verify memory
        memories = agent.memory.retrieve_memory("profit")
        # Note: Chroma might need time or valid text, but here we just check no crash
        print(f"Memory check (no crash): {memories is not None}")

if __name__ == "__main__":
    main()
