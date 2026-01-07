# CloudWalk AI Engineer Technical Challenge - Agent Market

## Project Overview
**Project Name:** `agent-market` (or `cloudwalk-agent-market`)
**Goal:** Build an autonomous multi-agent marketplace simulation where AI agents with distinct personalities buy, sell, and interact in real-time. The project leverages **Google Antigravity** and the **Gemini 3** model family to create a "social" simulation with emergent behavior.

## Technology Stack
*   **IDE/Foundation:** Google Antigravity (Agent-First IDE)
*   **Core Language:** Python 3.12+
*   **Package Manager:** `uv`
*   **AI Models:**
    *   **Gemini 3 Deep Think:** Architectural logic, Pydantic schemas, Complex Reasoning.
    *   **Gemini 3 Flash:** High-frequency trading agents (Speed/Cost efficiency).
    *   **GPT-5.2 (via API) / Gemini 3 Pro:** "Journalist" Agent (Creative narrative generation).
*   **Data Validation:** `Pydantic` (Strict JSON schemas for agent actions)
*   **Memory:** `ChromaDB` (Local Vector Store for agent history)
*   **Ledger:** `SQLite` (Transactional history) + `SQLModel` (ORM)
*   **Visualization:** `Rich` (CLI Dashboard) & `Streamlit` (Web Dashboard)

## Directory Structure
```text
/
├── src/
│   ├── agents/
│   │   ├── base.py         # Abstract Agent class (Memory + LLM connection)
│   │   ├── trader.py       # Buying/Selling logic
│   │   └── journalist.py   # Narrative generation
│   ├── market/
│   │   ├── engine.py       # The Simulation Loop (Time, Order Matching)
│   │   ├── ledger.py       # SQLModel definitions (Transactions, Wallets)
│   │   └── orderbook.py    # In-memory matching engine
│   ├── memory/
│   │   └── vector_store.py # ChromaDB wrapper
│   └── utils/
│       └── llm.py          # LiteLLM wrapper for Gemini/GPT
├── logs/                   # Simulation execution logs
├── tests/                  # Unit tests
├── main.py                 # CLI Entry point
├── app.py                  # Streamlit Dashboard Entry point
├── pyproject.toml          # uv configuration
├── .env                    # API Keys (GEMINI_API_KEY, OPENAI_API_KEY)
└── README.md
```

## Setup & Running
1.  **Install Dependencies:**
    ```bash
    uv sync
    ```
2.  **Environment:**
    Create a `.env` file:
    ```bash
    GEMINI_API_KEY=...
    OPENAI_API_KEY=...
    ```
3.  **Run Simulation (CLI):**
    ```bash
    uv run main.py
    ```
4.  **Run Dashboard (Web):**
    ```bash
    uv run streamlit run app.py
    ```

## Development Roadmap
1.  **Phase 1: Scaffolding (Day 1)** - Setup project, Pydantic Models (`AgentAction`, `MarketState`).
2.  **Phase 2: The Engine (Day 2)** - Implement `Market`, `Ledger`, and `OrderBook`.
3.  **Phase 3: The Brains (Day 3-4)** - Connect `LiteLLM`, implement `MemoryStream` (ChromaDB), and basic Trading Agents.
4.  **Phase 4: Social Layer (Day 5)** - Implement the `Journalist` agent and feedback loop.
5.  **Phase 5: Visualization (Day 6)** - Build the `Streamlit` dashboard.
6.  **Phase 6: Polish (Day 7)** - Documentation, Dockerfile, and Demo Video.

## Key Files for Context
*   `multi-agent-marketplace-simulation.md`: Official Challenge Requirements.
*   `global-guidelines.md`: Submission Standards.
