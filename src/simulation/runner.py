"""
Simulation Runner.

This module encapsulates the main simulation loop, managing the MarketEngine,
Agents, and Journalist. It runs as an asynchronous background task.
"""

import asyncio
import secrets
import time
from contextlib import suppress

from src.agents.journalist import JournalistAgent
from src.agents.trader import Trader
from src.market.engine import MarketEngine
from src.market.schema import SUPPORTED_ASSETS, InteractionLog
from src.utils.personas import PERSONA_MAP, get_model_for_persona, select_strategies


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

    async def start(self):
        if self.running:
            return

        # Initialize Engine & Agents
        self.engine = MarketEngine("market.db", run_id=f"web_{int(time.time())}")
        self.agents = []

        # Initialize Journalist
        self.journalist = JournalistAgent()

        # Spawn Agents using Enum-based personas (matching other agent's work)
        num_agents = 12
        selected_strategies = select_strategies(num_agents)
        for i, strategy in enumerate(selected_strategies):
            agent_id = f"Agent_{i + 1}"
            persona_text = PERSONA_MAP[strategy]
            model = get_model_for_persona(persona_text)
            agent = Trader(agent_id, strategy, model)
            # Seed inventory
            for asset in SUPPORTED_ASSETS:
                agent.portfolio.seed_position(asset, 10, 0.005)
            self.agents.append(agent)
        self.agent_index = {agent.id: agent for agent in self.agents}

        self.running = True
        self.task = asyncio.create_task(self._loop())
        print(">>> Simulation Started")

    async def stop(self):
        self.running = False
        if self.task:
            self.task.cancel()
            with suppress(asyncio.CancelledError):
                await self.task
        print(">>> Simulation Stopped")

    async def _loop(self):
        """The main game loop, running as a background asyncio task."""
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
                        self.engine.ledger.record_interaction(InteractionLog(**negotiation_details))

                    # EXECUTE
                    tx = self.engine.process_action(
                        agent, decision["action"], decision["item"], decision["price"]
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

            elapsed = time.time() - tick_start
            # Maintain a steady tick duration for human readability.
            await asyncio.sleep(max(0, 2.0 - elapsed))
