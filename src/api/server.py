"""
FastAPI Server for Agent Market Simulation.

This module exposes the internal MarketEngine state via:
1. REST API: For initial state fetching and control.
2. WebSockets: For real-time streaming of prices and agent actions.
"""

import os
import asyncio
from typing import List, Optional
from contextlib import asynccontextmanager, suppress

from dotenv import load_dotenv

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends, HTTPException, status, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.security import APIKeyHeader
from starlette.middleware.base import BaseHTTPMiddleware

# --- Configuration ---

# Load .env early
load_dotenv()

API_KEY_NAME = "X-API-Key"
API_KEY = os.getenv("API_KEY")
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000").split(",")

from src.simulation.runner import SimulationRunner
from src.market.schema import SUPPORTED_ASSETS, QUOTE_CURRENCY

# --- Global State ---

sim = SimulationRunner()

# --- Security Dependency ---

async def get_api_key(api_key: Optional[str] = Depends(api_key_header)):
    if API_KEY and api_key != API_KEY:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        )
    return api_key

# --- Custom Security Headers ---

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Content-Security-Policy"] = "default-src 'self'; script-src 'self'; object-src 'none';"
        return response

# --- FastAPI App ---

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Use await sim.start() as it is now an async method
    await sim.start()
    broadcast_task = asyncio.create_task(broadcast_loop())
    try:
        yield
    finally:
        broadcast_task.cancel()
        with suppress(asyncio.CancelledError):
            await broadcast_task
        await sim.stop()

app = FastAPI(
    title="Agent Market API", 
    lifespan=lifespan,
    docs_url="/docs" if os.getenv("ENV") != "production" else None,
    redoc_url=None
)

# Security & Performance Middlewares
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(
    TrustedHostMiddleware, 
    allowed_hosts=os.getenv("ALLOWED_HOSTS", "localhost,127.0.0.1").split(",")
)
app.add_middleware(GZipMiddleware, minimum_size=1000)

# CORS (Restricted)
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
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
        for connection in list(self.active_connections):
            try:
                await connection.send_json(message)
            except Exception:
                self.disconnect(connection)

manager = ConnectionManager()

# --- Background Broadcaster ---

async def broadcast_loop():
    last_news_tick = -1
    while True:
        if sim.running and sim.engine:
            await manager.broadcast({
                "type": "ticker",
                "data": dict(sim.engine.current_prices),
            })
            
            if sim.latest_news and sim.latest_news.get("tick", 0) > last_news_tick:
                last_news_tick = sim.latest_news["tick"]
                await manager.broadcast({
                    "type": "news",
                    "data": sim.latest_news
                })
        
        await asyncio.sleep(0.5)

# --- Endpoints ---

@app.get("/health")
def get_health():
    return {"status": "ok", "running": sim.running}

@app.get("/state", dependencies=[Depends(get_api_key)])
def get_state():
    if not sim.engine:
        return {"error": "Simulation not ready"}
    
    return {
        "prices": sim.engine.current_prices,
        "tickers": sim.engine.current_prices,
        "assets": SUPPORTED_ASSETS,
        "quote_currency": QUOTE_CURRENCY,
        "tick": sim.tick_count
    }

@app.get("/agents", dependencies=[Depends(get_api_key)])
def get_agents():
    if not sim.agents:
        return []
    
    return [
        {
            "id": a.id,
            "persona": a.persona,
            "model": a.model_name,
            "portfolio": a.portfolio.get_metrics(sim.engine.current_prices)
        }
        for a in sim.agents
    ]

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, api_key: Optional[str] = None):
    # For WebSockets, we can check the API key via query param or subprotocol
    # Here we check an optional query param 'token'
    token = websocket.query_params.get("token")
    if API_KEY and token != API_KEY:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)
