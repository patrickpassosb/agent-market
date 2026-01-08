"""
Checkpoint utilities for saving simulation state snapshots.
"""

from __future__ import annotations

from typing import Any, Iterable, Dict
import json
import os
from datetime import datetime, timezone

from pydantic import BaseModel

from src.market.schema import SUPPORTED_ASSETS


def _model_to_json_dict(model: BaseModel) -> dict:
    """
    Serialize a Pydantic/SQLModel instance to a JSON-ready dict.
    """
    return model.model_dump(mode="json")  # https://docs.pydantic.dev/latest/api/base_model (Context7 /websites/pydantic_dev)


def build_checkpoint(
    tick: int,
    current_prices: Dict[str, float],
    agents: Iterable[Any],
    transactions: Iterable[BaseModel],
    interactions: Iterable[BaseModel],
) -> dict:
    """
    Build a JSON-serializable checkpoint payload.
    """
    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),  # https://github.com/python/cpython/blob/main/Doc/library/datetime.rst (Context7 /python/cpython)
        "tick": tick,
        "market_state": {
            "current_prices": current_prices,
        },
        "agents": [
            {
                "id": agent.id,
                "persona": agent.persona,
                "model": getattr(agent, "model_name", None),
                "portfolio": agent.portfolio.get_metrics(current_prices),
            }
            for agent in agents
        ],
        "transactions": [_model_to_json_dict(tx) for tx in transactions],
        "interactions": [_model_to_json_dict(interaction) for interaction in interactions],
    }


def write_checkpoint(payload: dict, checkpoint_dir: str, filename: str) -> str:
    """
    Write a checkpoint payload to disk and return the path.
    """
    os.makedirs(checkpoint_dir, exist_ok=True)  # https://github.com/python/cpython/blob/main/Doc/faq/library.rst (Context7 /python/cpython)
    path = os.path.join(checkpoint_dir, filename)
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, sort_keys=True)  # https://github.com/python/cpython/blob/main/Doc/library/json.rst (Context7 /python/cpython)
    return path