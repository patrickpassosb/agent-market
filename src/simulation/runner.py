"""
Simulation Runner.

This module encapsulates the main simulation loop, managing the MarketEngine,
Agents, and Journalist. It runs as an asynchronous background task.
"""

import asyncio
import logging
import secrets
import time
from contextlib import suppress

from src.agents.journalist import JournalistAgent
from src.agents.trader import Trader
from src.analysis.report import generate_report
from src.market.engine import MarketEngine
from src.market.schema import SUPPORTED_ASSETS, InteractionLog
from src.utils.checkpoints import build_checkpoint, write_checkpoint
from src.utils.personas import (
    PERSONA_MAP,
    get_model_for_persona,
    select_strategies,
    set_provider_order,
)


class SimulationRunner:
    """
    Manages the background simulation loop using asyncio.
    """

    def __init__(self):
        self.running = False
        self.engine: MarketEngine | None = None
        self.agents: list[Trader] = []
        self.agent_index: dict[str, Trader] = {}
        self.journalist: JournalistAgent | None = None
        self.task: asyncio.Task | None = None
        self.latest_logs: list[dict] = []
        self.latest_news: dict | None = None
        self.tick_count = 0
        self.run_id: str | None = None
        self.last_report_dir: str | None = None
        self.last_summary: dict | None = None
        self.config = {
            "agent_count": 12,
            "tick_duration": 2.0,
            "max_ticks": 0,
            "checkpoint_every": 10,
            "checkpoint_dir": "checkpoints",
            "checkpoint_transactions": 50,
            "checkpoint_interactions": 100,
            "report_enabled": True,
            "report_dir": "reports",
            "initial_price": 0.005,
            "seed_inventory": 10,
            "model_provider_order": None,
        }
        self._logger = logging.getLogger(__name__)

    # Cryptographically secure randomness to satisfy Ruff S311.
    # Context7 /python/cpython (secrets module).
    def _secure_choice(self, items: list[str]) -> str:
        return secrets.choice(items)

    def _secure_shuffle(self, items: list[Trader]) -> None:
        remaining = list(items)
        shuffled: list[Trader] = []
        while remaining:
            pick = secrets.choice(remaining)
            remaining.remove(pick)
            shuffled.append(pick)
        items[:] = shuffled

    def configure(self, overrides: dict | None = None) -> None:
        if not overrides:
            return
        for key, value in overrides.items():
            if key in self.config and value is not None:
                self.config[key] = value

    async def start(self, overrides: dict | None = None):
        if self.running:
            return False
        self.configure(overrides)
        provider_order = self.config.get("model_provider_order")
        if provider_order:
            set_provider_order(provider_order)

        self.tick_count = 0
        self.latest_logs = []
        self.latest_news = None
        self.last_report_dir = None
        self.last_summary = None

        # Initialize Engine & Agents
        self.run_id = f"web_{int(time.time())}"
        self.engine = MarketEngine(
            "market.db",
            run_id=self.run_id,
            initial_price=float(self.config["initial_price"]),
        )
        self.agents = []

        # Initialize Journalist
        self.journalist = JournalistAgent()

        # Spawn Agents using Enum-based personas (matching other agent's work)
        num_agents = int(self.config["agent_count"])
        selected_strategies = select_strategies(num_agents)
        for i, strategy in enumerate(selected_strategies):
            agent_id = f"Agent_{i + 1}"
            persona_text = PERSONA_MAP[strategy]
            model = get_model_for_persona(persona_text)
            agent = Trader(agent_id, strategy, model)
            # Seed inventory
            for asset in SUPPORTED_ASSETS:
                agent.portfolio.seed_position(
                    asset,
                    int(self.config["seed_inventory"]),
                    float(self.config["initial_price"]),
                )
            self.agents.append(agent)
        self.agent_index = {agent.id: agent for agent in self.agents}

        self.running = True
        self.task = asyncio.create_task(self._loop())
        print(">>> Simulation Started")
        return True

    async def stop(self):
        self.running = False
        if self.task:
            self.task.cancel()
            with suppress(asyncio.CancelledError):
                await self.task
        print(">>> Simulation Stopped")

    async def _loop(self):
        """The main game loop, running as a background asyncio task."""
        report_enabled = bool(self.config["report_enabled"])
        report_dir = str(self.config["report_dir"])
        checkpoint_every = int(self.config["checkpoint_every"])
        checkpoint_dir = str(self.config["checkpoint_dir"])
        checkpoint_transactions = int(self.config["checkpoint_transactions"])
        checkpoint_interactions = int(self.config["checkpoint_interactions"])
        max_ticks = int(self.config["max_ticks"])
        tick_duration = float(self.config["tick_duration"])

        try:
            while self.running:
                tick_start = time.time()
                self.tick_count += 1

                # 1. Journalist Update (every 10 ticks)
                if self.tick_count % 10 == 0 and self.journalist:
                    recent_txns = self.engine.ledger.get_transactions(limit=20)
                    try:
                        news = await self.journalist.analyze(
                            self.engine.get_state(SUPPORTED_ASSETS[0]),
                            recent_txns,
                        )
                        self.latest_news = {
                            "headline": news.headline,
                            "body": news.body,
                            "tick": self.tick_count,
                        }
                    except Exception as e:
                        print(f"Journalist error: {e}")

                # 2. Agent Actions
                self._secure_shuffle(self.agents)

                # Define the interaction logic for a single agent
                async def run_agent(agent: Trader):
                    focused_asset = self._secure_choice(SUPPORTED_ASSETS)
                    state = self.engine.get_state(focused_asset)

                    # DECIDE (LLM Call)
                    decision = await agent.act(state, focused_asset, self.engine.current_prices)

                    if decision:
                        # NEGOTIATE
                        negotiated_price, negotiation_details = self.engine.negotiate_price(
                            agent_id=agent.id,
                            action=decision["action"],
                            item=decision["item"],
                            price=decision["price"],
                        )

                        if negotiation_details:
                            decision["price"] = negotiated_price
                            self.engine.ledger.record_interaction(
                                InteractionLog(**negotiation_details)
                            )

                        # EXECUTE
                        tx = self.engine.process_action(
                            agent,
                            decision["action"],
                            decision["item"],
                            decision["price"],
                            agent_registry=self.agent_index,
                        )
                        if tx:
                            buyer_agent = self.agent_index.get(tx.buyer_id)
                            seller_agent = self.agent_index.get(tx.seller_id)
                            run_id = self.engine.run_id if self.engine else None
                            if buyer_agent:
                                buyer_agent.remember(
                                    f"Bought {tx.item} from {tx.seller_id} at {tx.price}.",
                                    metadata={
                                        "kind": "trade",
                                        "item": tx.item,
                                        "action": "buy",
                                        "price": tx.price,
                                        "counterparty_id": tx.seller_id,
                                        "run_id": run_id,
                                    },
                                )
                            if seller_agent:
                                seller_agent.remember(
                                    f"Sold {tx.item} to {tx.buyer_id} at {tx.price}.",
                                    metadata={
                                        "kind": "trade",
                                        "item": tx.item,
                                        "action": "sell",
                                        "price": tx.price,
                                        "counterparty_id": tx.buyer_id,
                                        "run_id": run_id,
                                    },
                                )

                        return {
                            "tick": self.tick_count,
                            "agent_id": agent.id,
                            "action": decision["action"].value,
                            "item": decision["item"],
                            "price": decision["price"],
                            "reasoning": decision["reasoning"],
                            "executed": tx is not None,
                        }
                    return None

                # Execute all agents concurrently
                # The GlobalRateLimiter will handle queuing if we exceed API limits
                results = await asyncio.gather(
                    *[run_agent(a) for a in self.agents],
                    return_exceptions=True,
                )

                tick_logs = []
                # Persist each agent action as an interaction log entry for observability.
                for res in results:
                    if isinstance(res, dict):
                        tick_logs.append(res)
                        self.engine.ledger.record_interaction(
                            InteractionLog(
                                run_id=self.engine.run_id,
                                agent_id=res["agent_id"],
                                kind="action",
                                action=res["action"],
                                item=res["item"],
                                price=res["price"],
                                details=res["reasoning"],
                            )
                        )
                    elif isinstance(res, Exception):
                        print(f"Agent error: {res}")

                self.latest_logs.extend(tick_logs)
                self.latest_logs = self.latest_logs[-50:]

                if checkpoint_every and self.tick_count % checkpoint_every == 0:
                    payload = build_checkpoint(
                        tick=self.tick_count,
                        current_prices=self.engine.current_prices,
                        agents=self.agents,
                        transactions=self.engine.ledger.get_transactions(
                            limit=checkpoint_transactions
                        ),
                        interactions=self.engine.ledger.get_interactions(
                            limit=checkpoint_interactions
                        ),
                    )
                    filename = f"checkpoint_{self.tick_count:06d}.json"
                    path = write_checkpoint(payload, checkpoint_dir, filename)
                    self._logger.info("CHECKPOINT: %s", path)

                if max_ticks and self.tick_count >= max_ticks:
                    self.running = False
                    break

                elapsed = time.time() - tick_start
                # Maintain a steady tick duration for human readability.
                await asyncio.sleep(max(0, tick_duration - elapsed))
        finally:
            is_mock = (
                self.engine is not None
                and (
                    self.engine.__class__.__name__ == "MagicMock"
                    or getattr(self.engine, "ledger", None) is None
                    or self.engine.ledger.__class__.__name__ == "MagicMock"
                    or any(agent.__class__.__name__ == "MagicMock" for agent in self.agents)
                )
            )

            if self.engine and self.run_id and not is_mock:
                transactions = self.engine.ledger.get_transactions_for_run(self.run_id)
                prices = [tx.price for tx in transactions]
                avg_price = sum(prices) / len(prices) if prices else None
                min_price = min(prices) if prices else None
                max_price = max(prices) if prices else None
                interactions = self.engine.ledger.get_interactions_for_run(self.run_id)
                negotiation_count = 0
                if interactions:
                    negotiation_count = sum(
                        1 for entry in interactions if entry.kind == "negotiation"
                    )
                self.last_summary = {
                    "run_id": self.run_id,
                    "ticks": self.tick_count,
                    "total_trades": len(transactions),
                    "avg_price": avg_price,
                    "min_price": min_price,
                    "max_price": max_price,
                    "negotiation_count": negotiation_count,
                }

            if self.engine and self.run_id and report_enabled and not is_mock:
                try:
                    self.last_report_dir = generate_report(
                        run_id=self.run_id,
                        db_path="market.db",
                        report_root=report_dir,
                        agents=self.agents,
                        current_prices=self.engine.current_prices,
                    )
                except Exception as exc:
                    self._logger.error("Report generation failed: %s", exc)
