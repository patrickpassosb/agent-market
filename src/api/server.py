"""
FastAPI Server for Agent Market Simulation.

This module exposes the internal MarketEngine state via:
1. REST API: For initial state fetching and control.
2. WebSockets: For real-time streaming of prices and agent actions.
"""

import asyncio
import logging
import os
from contextlib import asynccontextmanager, suppress

from dotenv import load_dotenv
from fastapi import (
    Depends,
    FastAPI,
    HTTPException,
    Request,
    WebSocket,
    WebSocketDisconnect,
    status,
)
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.security import APIKeyHeader
from pydantic import BaseModel
from starlette.middleware.base import BaseHTTPMiddleware

from src.market.schema import QUOTE_CURRENCY, SUPPORTED_ASSETS, Transaction
from src.simulation.runner import SimulationRunner

logger = logging.getLogger(__name__)

# --- Configuration ---

# Load .env early
load_dotenv()

API_KEY_NAME = "X-API-Key"
API_KEY = os.getenv("API_KEY")
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

ALLOWED_ORIGINS = os.getenv(
    "ALLOWED_ORIGINS",
    "http://localhost:3000,http://127.0.0.1:3000",
).split(",")

# --- Global State ---

sim = SimulationRunner()


def _transaction_to_dict(tx: Transaction | None) -> dict | None:
    if not tx:
        return None
    return {
        "item": tx.item,
        "price": tx.price,
        "timestamp": tx.timestamp.isoformat(),
        "buyer_id": tx.buyer_id,
        "seller_id": tx.seller_id,
        "run_id": tx.run_id,
    }


def _agent_to_dict(agent) -> dict:
    return {
        "id": agent.id,
        "persona": agent.persona,
        "model": agent.model_name,
        "portfolio": agent.portfolio.get_metrics(sim.engine.current_prices) if sim.engine else None,
    }


def _build_agent_snapshot() -> list[dict]:
    if not sim.engine or not isinstance(sim.agents, list):
        return []
    return [_agent_to_dict(agent) for agent in sim.agents]


def _build_ticker_payload() -> dict | None:
    if not sim.engine:
        return None
    prices = sim.engine.current_prices
    data = dict(prices) if isinstance(prices, dict) else {}
    sentiment = sim.engine.get_global_sentiment()
    if not isinstance(sentiment, dict):
        sentiment = None
    metrics = sim.engine.get_market_metrics()
    if not isinstance(metrics, dict):
        metrics = None
    latest_tx = sim.engine.get_latest_transaction()
    latest_tx_payload = (
        _transaction_to_dict(latest_tx) if isinstance(latest_tx, Transaction) else None
    )
    tick = sim.tick_count if isinstance(sim.tick_count, int) else 0
    return {
        "type": "ticker",
        "data": data,
        "sentiment": sentiment,
        "metrics": metrics,
        "tick": tick,
        "latest_transaction": latest_tx_payload,
        "agents": _build_agent_snapshot(),
    }


def _build_run_summary() -> dict | None:
    if not sim.engine or not sim.run_id:
        return None
    transactions = sim.engine.ledger.get_transactions_for_run(sim.run_id)
    prices = [tx.price for tx in transactions]
    avg_price = sum(prices) / len(prices) if prices else None
    min_price = min(prices) if prices else None
    max_price = max(prices) if prices else None
    interactions = sim.engine.ledger.get_interactions_for_run(sim.run_id)
    negotiation_count = 0
    if interactions:
        negotiation_count = sum(1 for entry in interactions if entry.kind == "negotiation")
    return {
        "run_id": sim.run_id,
        "ticks": sim.tick_count,
        "total_trades": len(transactions),
        "avg_price": avg_price,
        "min_price": min_price,
        "max_price": max_price,
        "negotiation_count": negotiation_count,
        "report_dir": sim.last_report_dir,
    }


# --- Security Dependency ---


async def get_api_key(api_key: str | None = Depends(api_key_header)):
    """
    FastAPI dependency that validates the configured API key.
    
    Security:
    - If API_KEY is not set in environment, ALL protected requests are rejected (Fail Secure).
    - Requests that do not supply the correct key receive a 403 response.
    """
    if not API_KEY:
        logger.critical(
            "SECURITY ALERT: API_KEY is not set in environment variables. Access denied."
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Server security configuration error",
        )
        
    if api_key != API_KEY:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        )
    return api_key


# --- Custom Security Headers ---


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Injects security headers to harden the HTTP responses."""

    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; script-src 'self'; object-src 'none';"
        )
        return response


# --- FastAPI App ---


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    FastAPI lifespan manager.

    - Starts the simulation runner before the app accepts requests.
    - Spins up a background broadcast task to push market updates.
    - Ensures graceful shutdown by cancelling tasks and stopping the simulation.
    """
    broadcast_task = asyncio.create_task(broadcast_loop())
    try:
        yield
    finally:
        broadcast_task.cancel()
        with suppress(asyncio.CancelledError):
            await broadcast_task
        if sim.running:
            await sim.stop()


app = FastAPI(
    title="Agent Market API",
    lifespan=lifespan,
    docs_url="/docs" if os.getenv("ENV") != "production" else None,
    redoc_url=None,
)

# Security & Performance Middlewares
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=os.getenv(
        "ALLOWED_HOSTS",
        "localhost,127.0.0.1,testserver",
    ).split(","),
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
    """Tracks active WebSocket clients and provides a simple broadcast helper."""

    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        """
        Remove the websocket if still tracked. This guard prevents intermittent
        ValueError when the connection has already been removed (e.g., from broadcast errors).
        """
        try:
            self.active_connections.remove(websocket)
        except ValueError:
            pass

    async def broadcast(self, message: dict):
        """Send a dict payload to every connected WebSocket, pruning failures."""
        for connection in list(self.active_connections):
            try:
                # Context7 /websites/fastapi_tiangolo (WebSocket send_json).
                await connection.send_json(message)
            except Exception:
                self.disconnect(connection)


manager = ConnectionManager()

# --- Background Broadcaster ---


async def broadcast_loop():
    """
    Periodically reads market state from the SimulationRunner and broadcasts
    ticker updates, sentiment, and news events to all connected WebSocket clients.
    """
    last_news_tick = -1
    while True:
        if sim.running and sim.engine:
            payload = _build_ticker_payload()
            if payload:
                await manager.broadcast(payload)
            if sim.latest_news and sim.latest_news.get("tick", 0) > last_news_tick:
                last_news_tick = sim.latest_news["tick"]
                await manager.broadcast(
                    {
                        "type": "news",
                        "data": sim.latest_news,
                    }
                )
        await asyncio.sleep(0.5)


# --- Endpoints ---


@app.get("/health")
def get_health():
    """Simple health check endpoint consumed by load balancers or readiness scripts."""
    return {"status": "ok", "running": sim.running}


class SimulationStartRequest(BaseModel):
    # Context7 /websites/fastapi_tiangolo (request body models for POST endpoints).
    max_ticks: int | None = None
    checkpoint_every: int | None = None
    checkpoint_dir: str | None = None
    checkpoint_transactions: int | None = None
    checkpoint_interactions: int | None = None
    report_enabled: bool | None = None
    report_dir: str | None = None
    initial_price: float | None = None
    seed_inventory: int | None = None
    agent_count: int | None = None
    tick_duration: float | None = None
    model_provider_order: str | None = None


@app.get("/simulation/status", dependencies=[Depends(get_api_key)])
def get_simulation_status():
    """Returns run status and the active configuration for UI control panels."""
    return {
        "running": sim.running,
        "run_id": sim.run_id,
        "config": sim.config,
        "summary": sim.last_summary,
        "report_dir": sim.last_report_dir,
    }


@app.post("/simulation/start", dependencies=[Depends(get_api_key)])
async def start_simulation(payload: SimulationStartRequest):
    """Start the simulation with optional configuration overrides."""
    if sim.running:
        raise HTTPException(status_code=409, detail="Simulation already running")
    overrides = payload.model_dump(exclude_none=True)
    started = await sim.start(overrides)
    if not started:
        raise HTTPException(status_code=500, detail="Simulation failed to start")
    return {"status": "started", "run_id": sim.run_id, "config": sim.config}


@app.post("/simulation/stop", dependencies=[Depends(get_api_key)])
async def stop_simulation():
    """Stop the simulation and finalize reports/checkpoints if enabled."""
    if not sim.running:
        raise HTTPException(status_code=409, detail="Simulation is not running")
    await sim.stop()
    return {
        "status": "stopped",
        "summary": sim.last_summary,
        "report_dir": sim.last_report_dir,
    }


@app.get("/state", dependencies=[Depends(get_api_key)])
def get_state():
    """
    REST endpoint that returns the latest snapshot of the simulation.
    Includes prices, asset list, sentiment, and aggregated metrics.
    """
    if not sim.engine:
        return {"error": "Simulation not ready"}
    history_payload: list[dict] = []
    for tx in reversed(sim.engine.get_recent_transactions(limit=200)):
        payload = _transaction_to_dict(tx)
        if payload:
            history_payload.append(payload)
    return {
        "prices": sim.engine.current_prices,
        "tickers": sim.engine.current_prices,
        "assets": SUPPORTED_ASSETS,
        "quote_currency": QUOTE_CURRENCY,
        "tick": sim.tick_count,
        "sentiment": sim.engine.get_global_sentiment(),
        "metrics": sim.engine.get_market_metrics(),
        "summary": _build_run_summary(),
        "history": history_payload,
    }


@app.get("/agents", dependencies=[Depends(get_api_key)])
def get_agents():
    """
    Returns the roster of active agents, their persona, model, and live portfolio metrics.
    """
    return _build_agent_snapshot()


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, api_key: str | None = None):
    """
    WebSocket endpoint for streaming live ticker data and news.

    The optional `token` query parameter must match the configured API key (if any)
    before the connection is accepted.
    """
    token = websocket.query_params.get("token")
    if API_KEY and token != API_KEY:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return
    await manager.connect(websocket)
    logger.debug("websocket %s connected", websocket.client)
    # Push an initial ticker snapshot so clients don't wait for the next broadcast.
    payload = _build_ticker_payload()
    if payload:
        try:
            await websocket.send_json(payload)
            logger.debug("initial websocket payload sent to %s", websocket.client)
        except Exception as exc:
            logger.debug("initial websocket payload failed: %s", exc)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        logger.debug("websocket %s disconnected", websocket.client)
        manager.disconnect(websocket)
