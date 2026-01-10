"""
Simulation Runner.

This module encapsulates the main simulation loop, managing the MarketEngine,
Agents, and Journalist. It runs as an asynchronous background task.
"""

import asyncio
import time
import random
from typing import List, Dict, Optional
from contextlib import suppress

from src.market.engine import MarketEngine
from src.agents.trader import Trader
from src.agents.journalist import JournalistAgent
from src.market.schema import SUPPORTED_ASSETS, QUOTE_CURRENCY, InteractionLog
from src.utils.personas import PERSONA_MAP, PersonaStrategy, get_model_for_persona

class SimulationRunner:
    """
    Manages the background simulation loop using asyncio.
    """
    def __init__(self):
        self.running = False
        self.engine: Optional[MarketEngine] = None
        self.agents: List[Trader] = []
        self.journalist: Optional[JournalistAgent] = None
        self.task: Optional[asyncio.Task] = None
        self.latest_logs: List[dict] = []
        self.latest_news: Optional[dict] = None
        self.tick_count = 0

    async def start(self):
        if self.running:
            return
        
        # Initialize Engine & Agents
        self.engine = MarketEngine("market.db", run_id=f"web_{int(time.time())}")
        self.agents = []
        
        # Initialize Journalist
        self.journalist = JournalistAgent()
        
        # Spawn Agents using Enum-based personas (matching other agent's work)
        num_agents = 20
        available_strategies = list(PersonaStrategy)
        # Handle cases where num_agents > available_strategies by sampling with replacement if needed
        # But here we have 12 strategies, so let's just use all 12 and then double up some
        selected_strategies = random.choices(available_strategies, k=num_agents)
        for i, strategy in enumerate(selected_strategies):
            agent_id = f"Agent_{i+1}"
            persona_text = PERSONA_MAP[strategy]
            model = get_model_for_persona(persona_text)
            agent = Trader(agent_id, strategy, model)
            # Seed inventory
            for asset in SUPPORTED_ASSETS:
                agent.portfolio.seed_position(asset, 10, 0.005)
            self.agents.append(agent)

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
                        recent_txns
                    )
                    self.latest_news = {
                        "headline": news.headline,
                        "body": news.body,
                        "tick": self.tick_count
                    }
                except Exception as e:
                    print(f"Journalist error: {e}")
            
            # 2. Agent Actions
            random.shuffle(self.agents)
            
            # Concurrent execution of agent actions (as implemented by other agent)
            active_agents = self.agents[:4] 
            
            async def run_agent(agent: Trader):
                focused_asset = random.choice(SUPPORTED_ASSETS)
                state = self.engine.get_state(focused_asset)
                
                # DECIDE
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
                        agent,
                        decision["action"],
                        decision["item"],
                        decision["price"]
                    )
                    
                    return {
                        "tick": self.tick_count,
                        "agent_id": agent.id,
                        "action": decision["action"].value,
                        "item": decision["item"],
                        "price": decision["price"],
                        "reasoning": decision["reasoning"],
                        "executed": tx is not None
                    }
                return None

            # Execute concurrently
            results = await asyncio.gather(*[run_agent(a) for a in active_agents], return_exceptions=True)
            
            tick_logs = []
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
            await asyncio.sleep(max(0, 2.0 - elapsed))