# 🛠 Technical Documentation

## Hybrid LLM Strategy

To maximize performance within rate limits and budget, we employ a tiered model strategy:

| Agent Archetype | Model | Reasoning |
| :--- | :--- | :--- |
| **Whales / Market Makers** | `llama-3.3-70b-versatile` | Requires high reasoning to manipulate markets and manage large capital. |
| **Value Investors** | `gemini-1.5-flash` | Needs large context window to analyze price history and trends effectively. |
| **Algorithmic Traders** | `gpt-4o-mini` | Best at following strict structured output (JSON) rules for high-frequency logic. |
| **Retail / FOMO** | `llama-3.1-8b-instant` | Needs speed and low latency; "vibes based" trading doesn't require deep reasoning. |

*Implemented in `main.py:get_model_for_persona()`*

## Data Persistence

### 1. Vector Memory (ChromaDB)
Located in `src/memory/memory.py`.
-   **What is stored:** Natural language summaries of past trading decisions ("I sold at $10 because I felt bearish").
-   **Retrieval:** Before every action, agents query "relevant past mistakes/wins" to avoid repeating errors.

### 2. Transaction Ledger (SQLite/SQLModel)
Located in `src/market/ledger.py`.
-   **Schema:** `Transaction` table (id, timestamp, buyer_id, seller_id, price).
-   **Purpose:** The source of truth for the `JournalistAgent` and `chart.py` analysis.

## Project Structure

```
.
├── src/
│   ├── agents/
│   │   ├── base.py       # Abstract Agent Class
│   │   ├── trader.py     # The Main Trading Agent
│   │   └── journalist.py # Narrative Generator
│   ├── market/
│   │   ├── engine.py     # Simulation Controller
│   │   ├── ledger.py     # Database Handler
│   │   └── order_book.py # Matching Engine
│   └── analysis/
│       └── chart.py      # Post-simulation plotting
├── main.py               # Entry Point (UI + Loop)
└── market.db             # Local SQLite DB (Gitignored)
```
