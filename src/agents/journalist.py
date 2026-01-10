"""
Journalist Agent Implementation.

This module defines the `JournalistAgent`, a specialized observer agent that 
monitors the market state and generates "Breaking News" headlines. 
It adds narrative flavor to the simulation by converting raw data (price, volume, sentiment) 
into human-readable financial news.
"""

from pydantic import BaseModel, Field
import litellm
from litellm import completion, acompletion
from typing import List, Optional
import os

from src.market.schema import MarketState, Transaction, QUOTE_CURRENCY
from src.utils.personas import get_models_for_tier
from src.utils.concurrency import GlobalRateLimiter

litellm.enable_json_schema_validation = True

import re

def _sanitize_string(text: str) -> str:
    """Strip HTML tags and excessive whitespace."""
    if not text:
        return ""
    # Remove HTML tags
    text = re.sub(r"<[^>]*>", "", text)
    # Normalize whitespace
    return " ".join(text.split())

def _parse_structured_response(model_cls: type[BaseModel], content):
    """Normalize structured LLM output into a Pydantic model with sanitization."""
    if isinstance(content, model_cls):
        obj = content
    elif isinstance(content, dict):
        obj = model_cls.model_validate(content)
    else:
        obj = model_cls.model_validate_json(content)
        
    # Sanitize all string fields
    for field in obj.model_fields:
        val = getattr(obj, field)
        if isinstance(val, str):
            setattr(obj, field, _sanitize_string(val))
    return obj

class JournalistHeadline(BaseModel):
    """Structured output format for journalist responses."""
    headline: str = Field(description="A short, catchy news headline about the market state.")
    body: str = Field(description="A 2-sentence summary of the market sentiment.")

class JournalistAgent:
    """
    An AI-powered observer that narrates the market.
    
    This agent does not trade. Instead, it consumes the global `MarketState` and 
    a list of recent `Transaction`s to generate a `JournalistHeadline`.
    
    Attributes:
        model_name (str): The LLM model used for generation (default: Gemini 2.5 Flash).
        api_key (str): API key for the model provider.
    """

    def __init__(self, model_name: str = "gemini/gemini-2.5-flash"):
        """Initialize the journalist with a specific model identifier."""
        # Gemini models use the gemini/ prefix per LiteLLM docs (Context7 /websites/litellm_ai).
        self.model_name = model_name
        self.api_key = os.getenv("GEMINI_API_KEY")

    async def analyze(self, market_state: MarketState, recent_transactions: List[Transaction]) -> JournalistHeadline:
        """
        Analyzes the market state and recent history to generate a news headline.
        """
        
        # Summarize context
        price = market_state.current_price
        bid_count = market_state.order_book_summary["bids_count"]
        ask_count = market_state.order_book_summary["asks_count"]
        
        # Determine asset from transactions or generic
        asset = recent_transactions[0].item if recent_transactions else "Market"
        
        volume = len(recent_transactions)
        trend = "stable"
        if recent_transactions:
            # Sort by timestamp to find movement
            sorted_txs = sorted(recent_transactions, key=lambda x: x.timestamp)
            first_price = sorted_txs[0].price
            last_price = sorted_txs[-1].price
            if last_price > first_price: trend = "rising"
            elif last_price < first_price: trend = "falling"

        prompt = f"""
        You are a financial news journalist reporting on a Bitcoin-denominated Stock Exchange.
        
        Current Market Data for {asset}:
        - Price: {price:.6f} {QUOTE_CURRENCY}
        - Trend: {trend}
        - Volume: {volume} trades in the last period.
        - Sentiment: {bid_count} buyers vs {ask_count} sellers.
        
        Write a short, sensational "Breaking News" headline and a brief body explaining the movement.
        Be dramatic but accurate to the data. Remember all assets are priced in {QUOTE_CURRENCY}.
        """

        try:
            # Rate limiting
            await GlobalRateLimiter.get_instance().wait()

            fallback_models = get_models_for_tier("analytical")
            if self.model_name not in fallback_models:
                fallback_models.insert(0, self.model_name)

            response = None
            last_error: Exception | None = None
            # LiteLLM fallbacks per Context7 docs: /berriai/litellm (async acompletion).
            for model in fallback_models:
                try:
                    response = await acompletion(
                        model=model,
                        messages=[{"role": "user", "content": prompt}],
                        response_format=JournalistHeadline,
                        num_retries=2,
                    )
                    last_error = None
                    break
                except Exception as error:
                    last_error = error

            if response is None:
                raise last_error or RuntimeError("LLM completion failed across fallback models.")

            content = response.choices[0].message.content
            return _parse_structured_response(JournalistHeadline, content)
        except Exception as e:
            # Fallback if LLM fails
            return JournalistHeadline(headline=f"{asset} Activity Recorded", body=f"Trading volume remains steady in the {asset} market.")
