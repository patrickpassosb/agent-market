"""
Agent Personas.

This module defines the diverse set of personalities/strategies assigned to agents.
Using a predefined list ensures a heterogeneous market environment with conflicting interests,
which is necessary for liquidity and price discovery.
"""

from __future__ import annotations

import os

PERSONAS = [
    "A conservative long-term investor who only buys when prices are historically low and holds for long periods.",
    "A high-frequency momentum trader who buys when prices are rising and sells quickly when they dip.",
    "A panic seller who gets anxious when prices drop even slightly and sells immediately to cut losses.",
    "A patient value investor who calculates intrinsic value and buys undervalued assets, ignoring short-term noise.",
    "A contrarian who always bets against the current market trend; selling when everyone buys and buying when everyone sells.",
    "A FOMO (Fear Of Missing Out) buyer who jumps in whenever they see a price spike, regardless of fundamentals.",
    "A disciplined algorithmic trader who follows strict rules: buy at X% drop, sell at Y% gain.",
    "A skittish day trader who makes many small trades but exits positions at the end of every day.",
    "A whale who accumulates massive quantities slowly to not disturb the price, then holds.",
    "A market maker who tries to profit from the spread, placing both buy and sell orders around the current price.",
    "A rumor monger who trades based on 'news' (random fluctuations) rather than price trends.",
    "A DCA (Dollar Cost Average) buyer who buys a fixed amount every tick regardless of price."
]

# Keywords used to map text personas to tiers.
STRATEGIC_KEYWORDS = ["whale", "market maker"]
ANALYTICAL_KEYWORDS = ["value", "patient", "long-term", "conservative"]
RULE_BASED_KEYWORDS = ["algorithmic", "disciplined", "contrarian"]

PROVIDER_ORDER = os.getenv("MODEL_PROVIDER_ORDER", "openrouter,groq,gemini").split(",")

# OpenRouter uses OPENROUTER_API_KEY and optional OPENROUTER_API_BASE/OR_* envs.
# https://github.com/berriai/litellm/blob/main/docs/my-website/docs/providers/openrouter.md (Context7 /berriai/litellm)
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

GEMINI_MODELS = {
    "strategic": "gemini/gemini-1.5-flash",
    "analytical": "gemini/gemini-1.5-flash",
    "rule": "gemini/gemini-1.5-flash",
    "fast": "gemini/gemini-1.5-flash",
}

_ROUND_ROBIN = {"strategic": 0, "analytical": 0, "rule": 0, "fast": 0}


def _available_models(tier: str) -> list[str]:
    models: list[str] = []
    for provider in PROVIDER_ORDER:
        provider = provider.strip()
        if provider == "openrouter":
            model = OPENROUTER_MODELS.get(tier) or OPENROUTER_MODELS.get("fast")
            if model and os.getenv("OPENROUTER_API_KEY"):
                models.append(model)
        elif provider == "groq" and os.getenv("GROQ_API_KEY"):
            models.append(GROQ_MODELS[tier])
        elif provider == "gemini" and os.getenv("GEMINI_API_KEY"):
            models.append(GEMINI_MODELS[tier])
    return models


def _choose_model(tier: str) -> str:
    candidates = _available_models(tier)
    if not candidates:
        return GROQ_MODELS["fast"]
    index = _ROUND_ROBIN[tier] % len(candidates)
    _ROUND_ROBIN[tier] = _ROUND_ROBIN[tier] + 1
    return candidates[index]


def _persona_tier(persona: str) -> str:
    p_lower = persona.lower()
    if any(k in p_lower for k in STRATEGIC_KEYWORDS):
        return "strategic"
    if any(k in p_lower for k in ANALYTICAL_KEYWORDS):
        return "analytical"
    if any(k in p_lower for k in RULE_BASED_KEYWORDS):
        return "rule"
    return "fast"

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
