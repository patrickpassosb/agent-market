"""
Agent Personas.

This module defines the diverse set of personalities/strategies assigned to agents.
Using a predefined list ensures a heterogeneous market environment with conflicting interests,
which is necessary for liquidity and price discovery.
"""

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

# Keywords used to map text personas to appropriate underlying models.
SMART_GROQ_KEYWORDS = ["whale", "market maker"]
GEMINI_KEYWORDS = ["value", "patient", "long-term", "conservative"]
OPENAI_KEYWORDS = ["algorithmic", "disciplined", "contrarian"]

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
    p_lower = persona.lower()
    
    if any(k in p_lower for k in SMART_GROQ_KEYWORDS):
        return "groq/llama-3.3-70b-versatile"
    
    if any(k in p_lower for k in GEMINI_KEYWORDS):
        return "gemini/gemini-1.5-flash"
        
    if any(k in p_lower for k in OPENAI_KEYWORDS):
        return "openai/gpt-4o-mini"
        
    return "groq/llama-3.1-8b-instant"