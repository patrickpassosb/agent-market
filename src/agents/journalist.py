from pydantic import BaseModel, Field
import litellm
from litellm import completion
from typing import List, Optional
import os

from src.market.schema import MarketState, Transaction

litellm.enable_json_schema_validation = True

def _parse_structured_response(model_cls: type[BaseModel], content):
    if isinstance(content, model_cls):
        return content
    if isinstance(content, dict):
        return model_cls.model_validate(content)
    return model_cls.model_validate_json(content)

class JournalistHeadline(BaseModel):
    headline: str = Field(description="A short, catchy news headline about the market state.")
    body: str = Field(description="A 2-sentence summary of the market sentiment.")

class JournalistAgent:
    def __init__(self, model_name: str = "gemini/gemini-1.5-flash"):
        self.model_name = model_name
        self.api_key = os.getenv("GEMINI_API_KEY")

    def analyze(self, market_state: MarketState, recent_transactions: List[Transaction]) -> JournalistHeadline:
        """
        Analyzes the market state and recent history to generate a news headline.
        """
        
        # Summarize context
        price = market_state.current_price
        bid_count = market_state.order_book_summary["bids_count"]
        ask_count = market_state.order_book_summary["asks_count"]
        
        volume = len(recent_transactions)
        trend = "stable"
        if recent_transactions:
            oldest_first = list(reversed(recent_transactions))
            first_price = oldest_first[0].price
            last_price = oldest_first[-1].price
            if last_price > first_price: trend = "rising"
            elif last_price < first_price: trend = "falling"

        prompt = f"""
        You are a financial news journalist reporting on a fast-paced market.
        
        Current Market Data:
        - Price: ${price:.2f}
        - Trend: {trend}
        - Volume: {volume} trades in the last period.
        - Sentiment: {bid_count} buyers vs {ask_count} sellers.
        
        Write a short, sensational "Breaking News" headline and a brief body explaining the movement.
        Be dramatic but accurate to the data.
        """

        try:
            response = completion(
                model=self.model_name,
                messages=[{"role": "user", "content": prompt}],
                response_format=JournalistHeadline
            )
            content = response.choices[0].message.content
            return _parse_structured_response(JournalistHeadline, content)
        except Exception as e:
            # Fallback if LLM fails
            return JournalistHeadline(headline="Market Stays Calm", body="Trading continues as usual.")
