"""
Agent Personas.

This module defines the diverse set of personalities/strategies assigned to agents.
Using a predefined list ensures a heterogeneous market environment with conflicting interests,
which is necessary for liquidity and price discovery.
"""

from __future__ import annotations

import os
import secrets
from enum import Enum


class PersonaStrategy(Enum):
    CONSERVATIVE = "conservative"
    MOMENTUM = "momentum"
    PANIC = "panic"
    VALUE = "value"
    CONTRARIAN = "contrarian"
    FOMO = "fomo"
    ALGORITHMIC = "algorithmic"
    DAY_TRADER = "day_trader"
    WHALE = "whale"
    MARKET_MAKER = "market_maker"
    RUMOR_MONGER = "rumor_monger"
    DCA = "dca"


PERSONA_MAP = {
    PersonaStrategy.CONSERVATIVE: (
        "A conservative long-term investor who only buys when prices are historically "
        "low and holds for long periods."
    ),
    PersonaStrategy.MOMENTUM: (
        "A high-frequency momentum trader who buys when prices are rising and sells "
        "quickly when they dip."
    ),
    PersonaStrategy.PANIC: (
        "A panic seller who gets anxious when prices drop even slightly and sells "
        "immediately to cut losses."
    ),
    PersonaStrategy.VALUE: (
        "A patient value investor who calculates intrinsic value and buys undervalued "
        "assets, ignoring short-term noise."
    ),
    PersonaStrategy.CONTRARIAN: (
        "A contrarian who always bets against the current market trend; selling when "
        "everyone buys and buying when everyone sells."
    ),
    PersonaStrategy.FOMO: (
        "A FOMO (Fear Of Missing Out) buyer who jumps in whenever they see a price "
        "spike, regardless of fundamentals."
    ),
    PersonaStrategy.ALGORITHMIC: (
        "A disciplined algorithmic trader who follows strict rules: buy at X% drop, "
        "sell at Y% gain."
    ),
    PersonaStrategy.DAY_TRADER: (
        "A skittish day trader who makes many small trades but exits positions at the "
        "end of every day."
    ),
    PersonaStrategy.WHALE: (
        "A whale who accumulates massive quantities slowly to not disturb the price, then holds."
    ),
    PersonaStrategy.MARKET_MAKER: (
        "A market maker who tries to profit from the spread, placing both buy and "
        "sell orders around the current price."
    ),
    PersonaStrategy.RUMOR_MONGER: (
        "A rumor monger who trades based on 'news' (random fluctuations) rather than price trends."
    ),
    PersonaStrategy.DCA: (
        "A DCA (Dollar Cost Average) buyer who buys a fixed amount every tick regardless of price."
    ),
}

PERSONAS = list(PERSONA_MAP.values())

# Keywords used to map text personas to tiers.
STRATEGIC_KEYWORDS = ["whale", "market maker"]
ANALYTICAL_KEYWORDS = ["value", "patient", "long-term", "conservative"]
RULE_BASED_KEYWORDS = ["algorithmic", "disciplined", "contrarian"]

PROVIDER_ORDER = os.getenv(
    "MODEL_PROVIDER_ORDER",
    "cerebras,groq,gemini,openrouter,ollama",
).split(",")

# Cerebras models use the cerebras/ prefix.
# Context7 /berriai/litellm.
CEREBRAS_MODELS = {
    "strategic": "cerebras/llama3.1-70b",
    "analytical": "cerebras/llama3.1-70b",
    "rule": "cerebras/llama3.1-8b",
    "fast": "cerebras/llama3.1-8b",
}

# SambaNova models use the sambanova/ prefix.
# Context7 /berriai/litellm.
SAMBANOVA_MODELS = {
    "strategic": "sambanova/llama3-70b",
    "analytical": "sambanova/llama3-70b",
    "rule": "sambanova/llama3-8b",
    "fast": "sambanova/llama3-8b",
}

# OpenRouter uses OPENROUTER_API_KEY and optional OPENROUTER_API_BASE/OR_* envs.
# Context7 /berriai/litellm (OpenRouter docs).
OPENROUTER_MODELS = {
    "strategic": os.getenv("OPENROUTER_MODEL_STRATEGIC"),
    "analytical": os.getenv("OPENROUTER_MODEL_ANALYTICAL"),
    "rule": os.getenv("OPENROUTER_MODEL_RULE"),
    "fast": os.getenv("OPENROUTER_MODEL_FAST"),
}

GROQ_MODELS = {
    "strategic": "groq/llama-3.3-70b-versatile",
    "analytical": "groq/llama-3.1-8b-instant",
    "rule": "groq/llama-3.1-8b-instant",
    "fast": "groq/llama-3.1-8b-instant",
}

# Gemini models use the gemini/ prefix.
# Context7 /websites/litellm_ai.
GEMINI_MODELS = {
    "strategic": "gemini/gemini-2.5-flash-preview-09-2025",
    "analytical": "gemini/gemini-2.5-flash-preview-09-2025",
    "rule": "gemini/gemini-2.5-flash-preview-09-2025",
    "fast": "gemini/gemini-2.5-flash-preview-09-2025",
}

# Vertex AI models use the vertex_ai/ prefix.
# Context7 /berriai/litellm.
# We use Pro for strategic/analytical tasks to leverage the robust quota.
VERTEX_MODELS = {
    "strategic": "vertex_ai/gemini-1.5-pro",
    "analytical": "vertex_ai/gemini-1.5-pro",
    "rule": "vertex_ai/gemini-1.5-flash",
    "fast": "vertex_ai/gemini-1.5-flash",
}


def _ollama_enabled() -> bool:
    """
    Detect whether Ollama should be considered as a provider.
    Ollama can be activated explicitly via OLLAMA_ENABLED or by configuring
    any of the OLLAMA_MODEL_* variables.
    """
    if os.getenv("OLLAMA_ENABLED", "").lower() in {"1", "true", "yes"}:
        return True
    return any(
        os.getenv(name)
        for name in (
            "OLLAMA_MODEL_STRATEGIC",
            "OLLAMA_MODEL_ANALYTICAL",
            "OLLAMA_MODEL_RULE",
            "OLLAMA_MODEL_FAST",
        )
    )


# Ollama models use the ollama_chat/ prefix.
# Context7 /websites/litellm_ai.
OLLAMA_MODELS = {
    "strategic": os.getenv("OLLAMA_MODEL_STRATEGIC", "ollama_chat/phi3"),
    "analytical": os.getenv("OLLAMA_MODEL_ANALYTICAL", "ollama_chat/phi3"),
    "rule": os.getenv("OLLAMA_MODEL_RULE", "ollama_chat/tinyllama"),
    "fast": os.getenv("OLLAMA_MODEL_FAST", "ollama_chat/tinyllama"),
}

_ROUND_ROBIN = {"strategic": 0, "analytical": 0, "rule": 0, "fast": 0}


def _secure_shuffle(items: list[PersonaStrategy]) -> list[PersonaStrategy]:
    remaining = list(items)
    shuffled: list[PersonaStrategy] = []
    while remaining:
        pick = secrets.choice(remaining)
        remaining.remove(pick)
        shuffled.append(pick)
    return shuffled


def select_strategies(count: int) -> list[PersonaStrategy]:
    """
    Choose strategies with distinct coverage before sampling with replacement.
    """
    strategies = _secure_shuffle(list(PersonaStrategy))
    if count <= len(strategies):
        return strategies[:count]
    extra = [secrets.choice(list(PersonaStrategy)) for _ in range(count - len(strategies))]
    return strategies + extra


def set_provider_order(order: str | None) -> None:
    """
    Update provider order at runtime to support UI-configured simulation runs.
    """
    if not order:
        return
    providers = [item.strip() for item in order.split(",") if item.strip()]
    if not providers:
        return
    global PROVIDER_ORDER
    PROVIDER_ORDER = providers
    for key in _ROUND_ROBIN:
        _ROUND_ROBIN[key] = 0


def _available_models(tier: str) -> list[str]:
    """
    Enumerate the configured models for a tier respecting the preferred provider order.

    This method checks the environment for provider credentials before adding them.
    """
    models: list[str] = []
    for provider in PROVIDER_ORDER:
        provider = provider.strip()
        if provider == "cerebras" and os.getenv("CEREBRAS_API_KEY"):
            models.append(CEREBRAS_MODELS[tier])
        elif provider == "sambanova" and os.getenv("SAMBANOVA_API_KEY"):
            models.append(SAMBANOVA_MODELS[tier])
        elif provider == "ollama" and _ollama_enabled():
            models.append(OLLAMA_MODELS[tier])
        elif provider == "openrouter":
            model = OPENROUTER_MODELS.get(tier) or OPENROUTER_MODELS.get("fast")
            if model and os.getenv("OPENROUTER_API_KEY"):
                models.append(model)
        elif provider == "groq" and os.getenv("GROQ_API_KEY"):
            models.append(GROQ_MODELS[tier])
        elif provider == "gemini" and os.getenv("GEMINI_API_KEY"):
            models.append(GEMINI_MODELS[tier])
        elif provider == "vertex_ai" and os.getenv("VERTEXAI_PROJECT"):
            models.append(VERTEX_MODELS[tier])
    return models


def get_models_for_tier(tier: str) -> list[str]:
    """Expose ordered models for a tier to support fallback retries."""
    return _available_models(tier)


def _choose_model(tier: str) -> str:
    """
    Round-robin through available providers for a tier.

    Falls back to the Groq fast tier if no configured provider is available.
    """
    candidates = _available_models(tier)
    if not candidates:
        return GROQ_MODELS["fast"]
    index = _ROUND_ROBIN[tier] % len(candidates)
    _ROUND_ROBIN[tier] = _ROUND_ROBIN[tier] + 1
    return candidates[index]


def _persona_tier(persona: str) -> str:
    """
    Map a textual persona description to a routing tier.

    Keywords are used to bias decision-making: strategic, analytical, rule-based, or fast.
    """
    p_lower = persona.lower()
    if any(k in p_lower for k in STRATEGIC_KEYWORDS):
        return "strategic"
    if any(k in p_lower for k in ANALYTICAL_KEYWORDS):
        return "analytical"
    if any(k in p_lower for k in RULE_BASED_KEYWORDS):
        return "rule"
    return "fast"


def get_persona_tier(persona: str) -> str:
    """Public wrapper for persona tier classification."""
    return _persona_tier(persona)


def get_model_for_persona(persona: str) -> str:
    """
    Intelligently assigns an LLM model based on the complexity/archetype of the persona.

    Strategy:
    - Complex/Strategic roles -> Llama 70B (High reasoning)
    - Analytical roles -> Gemini Flash (Long context/analytical)
    - Strict/Rule-based roles -> GPT-4o Mini (Instruction following)
    - Default/Reactive roles -> Llama 8B (Speed)

    Args:
        persona (str): The agent's persona description.

    Returns:
        str: The model identifier string for `litellm`.
    """
    tier = _persona_tier(persona)
    return _choose_model(tier)
