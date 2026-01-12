"""
Checkpoint utilities for saving simulation state snapshots.
"""

from __future__ import annotations

import json
import os
from collections.abc import Iterable
from datetime import UTC, datetime
from typing import Any

from pydantic import BaseModel


def _model_to_json_dict(model: BaseModel) -> dict:
    """
    Serialize a Pydantic/SQLModel instance to a JSON-ready dict.
    """
    # Context7 /websites/pydantic_dev (BaseModel model_dump).
    return model.model_dump(mode="json")


def build_checkpoint(
    tick: int,
    current_prices: dict[str, float],
    agents: Iterable[Any],
    transactions: Iterable[BaseModel],
    interactions: Iterable[BaseModel],
) -> dict:
    """
    Build a JSON-serializable checkpoint payload.
    """
    return {
        # Context7 /python/cpython (datetime docs).
        "timestamp": datetime.now(UTC).isoformat(),
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
    # Context7 /python/cpython (os.makedirs docs).
    os.makedirs(checkpoint_dir, exist_ok=True)
    path = os.path.join(checkpoint_dir, filename)
    with open(path, "w", encoding="utf-8") as handle:
        # Context7 /python/cpython (json docs).
        json.dump(payload, handle, indent=2, sort_keys=True)
    return path
