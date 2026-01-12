"""
Tests for SimulationRunner orchestration.
"""

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.market.schema import AgentAction, Transaction
from src.simulation.runner import SimulationRunner


class TestSimulationRunner:
    @pytest.fixture
    def runner(self):
        return SimulationRunner()

    @pytest.mark.asyncio
    async def test_start_stop(self, runner):
        with (
            patch("src.simulation.runner.MarketEngine"),
            patch("src.simulation.runner.Trader"),
            patch("src.simulation.runner.JournalistAgent"),
        ):
            await runner.start()
            assert runner.running is True
            assert runner.engine is not None
            assert len(runner.agents) > 0
            assert runner.task is not None

            await runner.stop()
            assert runner.running is False
            assert runner.task.cancelled()

    @pytest.mark.asyncio
    async def test_loop_iteration(self, runner):
        """Test a single iteration of the loop by mocking dependencies."""
        mock_engine = MagicMock()
        mock_engine.run_id = "test_run"
        mock_engine.ledger = MagicMock()
        mock_engine.current_prices = {"AAPL": 1.0}

        mock_agent = AsyncMock()
        mock_agent.id = "Agent_1"
        mock_agent.act.return_value = {
            "action": AgentAction.BUY,
            "item": "AAPL",
            "price": 1.1,
            "reasoning": "Test",
        }

        runner.engine = mock_engine
        runner.agents = [mock_agent]
        runner.running = True

        # We want to test the logic inside the loop without running it forever
        # So we can manually trigger the logic or mock the sleep to exit

        with (
            patch("asyncio.sleep", side_effect=asyncio.CancelledError),
            patch("src.simulation.runner.random.shuffle"),
            patch("src.simulation.runner.random.choice", return_value="AAPL"),
        ):
            # Mock negotiate_price to return the same price
            mock_engine.negotiate_price.return_value = (1.1, None)
            mock_engine.process_action.return_value = MagicMock(spec=Transaction)

            try:
                await runner._loop()
            except asyncio.CancelledError:
                pass

            assert runner.tick_count == 1
            mock_agent.act.assert_called_once()
            mock_engine.process_action.assert_called_once()
            assert len(runner.latest_logs) == 1
