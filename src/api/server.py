"""
FastAPI Server for Agent Market Simulation.

This module exposes the internal MarketEngine state via:
1. REST API: For initial state fetching and control.
2. WebSockets: For real-time streaming of prices and agent actions.

It runs the simulation loop in a background thread to prevent blocking the API.
"""

import asyncio
import threading
import time
import random
from typing import List, Dict
from contextlib import asynccontextmanager

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from src.market.engine import MarketEngine
from src.agents.trader import Trader
from src.agents.journalist import JournalistAgent
from src.market.schema import SUPPORTED_ASSETS, QUOTE_CURRENCY, AgentAction, InteractionLog
from src.utils.personas import PERSONAS, get_model_for_persona

# --- Global State ---

class SimulationRunner:
    """
    Manages the background simulation loop.
    """
    def __init__(self):
        self.running = False
        self.engine: MarketEngine = None
        self.agents: List[Trader] = []
        self.journalist: JournalistAgent = None
        self.thread: threading.Thread = None
        self.latest_logs: List[dict] = []
        self.latest_news: dict = None
        self.tick_count = 0

    def start(self):
        if self.running:
            return
        
        # Initialize Engine & Agents
        self.engine = MarketEngine("market.db", run_id=f"web_{int(time.time())}")
        self.agents = []
        
        # Initialize Journalist
        self.journalist = JournalistAgent()
        
        # Spawn Agents
        num_agents = 12
        selected_personas = random.sample(PERSONAS, min(num_agents, len(PERSONAS)))
        for i, persona in enumerate(selected_personas):
            agent_id = f"Agent_{i+1}"
            model = get_model_for_persona(persona)
            agent = Trader(agent_id, persona, model)
            # Seed inventory
            for asset in SUPPORTED_ASSETS:
                agent.portfolio.seed_position(asset, 10, 0.005)
            self.agents.append(agent)

        self.running = True
        self.thread = threading.Thread(target=self._loop, daemon=True)
        self.thread.start()
        print(">>> Simulation Started")

    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join()
        print(">>> Simulation Stopped")

    def _loop(self):
        """The main game loop, running in a separate thread."""
        while self.running:
            tick_start = time.time()
            self.tick_count += 1
            
            # 1. Journalist Update (every 10 ticks)
            if self.tick_count % 10 == 0 and self.journalist:
                recent_txns = self.engine.ledger.get_transactions(limit=20)
                # Pick an asset to focus on (e.g., first supported or most active)
                try:
                    news = self.journalist.analyze(
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
            
            # Limit agents per tick to avoid overwhelming the API rate limits in demo
            # Let's say 4 agents act per tick
            active_agents = self.agents[:4] 
            
            tick_logs = []
            
            for agent in active_agents:
                focused_asset = random.choice(SUPPORTED_ASSETS)
                state = self.engine.get_state(focused_asset)
                
                # DECIDE
                decision = agent.act(state, focused_asset, self.engine.current_prices)
                
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
                    
                    # LOG
                    log_entry = {
                        "tick": self.tick_count,
                        "agent_id": agent.id,
                        "action": decision["action"].value,
                        "item": decision["item"],
                        "price": decision["price"],
                        "reasoning": decision["reasoning"],
                        "executed": tx is not None
                    }
                    tick_logs.append(log_entry)
                    
                    # Record interaction in ledger
                    self.engine.ledger.record_interaction(
                        InteractionLog(
                            run_id=self.engine.run_id,
                            agent_id=agent.id,
                            kind="action",
                            action=decision["action"].value,
                            item=decision["item"],
                            price=decision["price"],
                            details=decision["reasoning"],
                        )
                    )
            
            # Update global logs buffer
            self.latest_logs.extend(tick_logs)
            self.latest_logs = self.latest_logs[-50:] # Keep last 50
            
            # Sleep to maintain tick rate
            elapsed = time.time() - tick_start
            time.sleep(max(0, 2.0 - elapsed))

sim = SimulationRunner()

# --- FastAPI App ---

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Lifespan handler per Context7 FastAPI docs: /websites/fastapi_tiangolo (lifespan events).
    # Startup
    sim.start()
    yield
    # Shutdown
    sim.stop()

app = FastAPI(title="Agent Market API", lifespan=lifespan)

# Allow CORS for local frontend dev
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- WebSocket Manager ---

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        # Clean out dead connections
        for connection in list(self.active_connections):
            try:
                await connection.send_json(message)
            except Exception:
                self.disconnect(connection)

manager = ConnectionManager()

# --- Background Broadcaster ---

async def broadcast_loop():
    """Reads state from the simulation runner and pushes to WebSocket clients."""
    while True:
        if sim.running and sim.engine:
            # Construct payload aligned with frontend expectations.
            payload = {
                "type": "ticker",
                "data": dict(sim.engine.current_prices),
            }
            await manager.broadcast(payload)
        
        await asyncio.sleep(0.5) # Update frontend every 500ms

@app.on_event("startup")
async def start_broadcast():
    asyncio.create_task(broadcast_loop())

# --- Endpoints ---

@app.get("/health")
def get_health():
    return {"status": "ok", "running": sim.running}

@app.get("/state")
def get_state():
    """Return full market snapshot."""
    if not sim.engine:
        return {"error": "Simulation not ready"}
    
    return {
        "prices": sim.engine.current_prices,
        "tickers": sim.engine.current_prices,
        "assets": SUPPORTED_ASSETS,
        "quote_currency": QUOTE_CURRENCY,
        "tick": sim.tick_count
    }

@app.get("/market/state")
def get_market_state():
    return get_state()

@app.get("/agents")
def get_agents():
    if not sim.agents:
        return []
    
    return [
        {
            "id": a.id,
            "persona": a.persona,
            "portfolio": a.portfolio.get_metrics(sim.engine.current_prices)
        }
        for a in sim.agents
    ]

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    # WebSocket endpoint per Context7 FastAPI docs: /websites/fastapi_tiangolo (websocket decorator usage).
    await manager.connect(websocket)
    try:
        while True:
            # Keep connection alive, maybe handle client messages later
            data = await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)
