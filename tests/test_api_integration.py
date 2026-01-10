from fastapi.testclient import TestClient
from src.api.server import app
import pytest
from unittest.mock import patch, MagicMock, AsyncMock

def test_websocket_connection():
    # Use context manager to trigger lifespan
    # We mock sim.start to avoid hitting real APIs during tests
    with patch("src.simulation.runner.SimulationRunner.start", new_callable=AsyncMock):
        # We need to ensure sim.engine is set so the broadcast loop doesn't fail
        with patch("src.api.server.sim") as mock_sim:
            mock_sim.running = True
            mock_sim.engine = MagicMock()
            mock_sim.engine.current_prices = {"AAPL": 150.0}
            mock_sim.latest_news = None
            mock_sim.start = AsyncMock() # Ensure start is awaitable
            mock_sim.stop = AsyncMock()  # Ensure stop is awaitable
            
            with TestClient(app) as client:
                with client.websocket_connect("/ws") as websocket:
                    # The server sends a ticker update immediately upon connection
                    data = websocket.receive_json()
                    assert "type" in data
                    assert data["type"] == "ticker"
                    assert "data" in data