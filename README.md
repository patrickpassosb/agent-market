# Agent Market Simulation

A multi-agent market simulation where autonomous AI agents (powered by different LLMs) trade assets based on unique personas.

## 📖 Overview

This project simulates a dynamic, autonomous marketplace populated by AI agents. Each agent acts as an independent trader with a specific psychological profile (e.g., "Whale", "Value Investor", "Day Trader"). These agents utilize Large Language Models (LLMs)—including Llama 3, Gemini Flash, and GPT-4o—to analyze market conditions, retrieve past memories, and make trading decisions.

The system is designed to demonstrate:
- **Emergent Behavior**: How complex market dynamics arise from individual agent decisions.
- **Heterogeneous Intelligence**: The interaction between different LLM capabilities (e.g., speed vs. reasoning depth).
- **Autonomous Economics**: A self-contained economic system with order matching, price discovery, and persistence.

---

## 🏗️ Architecture

The system follows a modular, event-driven architecture centered around a "tick" loop.

```
+----------------+       +----------------------+       +----------------+
|                |       |                      |       |                |
|  Agent (LLM)   | <---> |    Market Engine     | <---> |   Database     |
|                |       |                      |       |                |
+----------------+       +----------------------+       +----------------+
       ^                         ^                             ^
       |                         |                             |
  Decides Action           Matches Orders               Persists Data
  (Buy/Sell/Hold)         (Order Book Heap)             (SQLite/SQLModel)
```

### Key Components

1.  **Simulation Loop (`main.py`)**:
    - The central orchestrator. It advances time ("ticks"), queries agents, executes their actions against the engine, and updates the visualization.
    - Implements a **Facade Pattern** via the `MarketEngine` to simplify interactions.

2.  **Market Engine (`src/market/`)**:
    - **`engine.py`**: The API surface for the market.
    - **`order_book.py`**: A **Limit Order Book** implemented using **Binary Heaps**.
        - *Bids* (Buys) are stored in a Max-Heap.
        - *Asks* (Sells) are stored in a Min-Heap.
        - Matching logic follows **Price-Time Priority**.
    - **`ledger.py`**: Handles transactional integrity and persistence using **SQLModel** (SQLAlchemy).

3.  **Agents (`src/agents/`)**:
    - **`trader.py`**: The concrete agent implementation.
    - **Logic Flow**:
        1.  **Observe**: Read `MarketState` (Price, Order Book).
        2.  **Recall**: Query `Vector Memory` for relevant past strategies.
        3.  **Reason**: Construct a prompt with Persona + Context.
        4.  **Decide**: Call LLM API (via `litellm`) for a structured JSON decision.

---

## 🚀 Setup & Installation

### Prerequisites

- **Python 3.12+**
- **Docker** (Optional, for containerized execution)
- **API Keys**: You need access to at least one LLM provider (Groq, Google Gemini, or OpenAI).

### 1. Clone the Repository
```bash
git clone https://github.com/your-username/agent-market.git
cd agent-market
```

### 2. Configure Environment
Copy the example configuration and add your API keys.
```bash
cp .env.example .env
# Edit .env with your favorite editor
# nano .env
```

### 3. Install Dependencies
We use `uv` for ultra-fast dependency management.

```bash
# Install uv if you don't have it
pip install uv

# Sync dependencies
uv sync
```

---

## 🏃 Usage

### Option 1: Local Execution (CLI)

Run the simulation directly in your terminal.
```bash
uv run main.py
```

### Option 2: Docker

Run the simulation in a container.
```bash
docker-compose up --build
```

---

## 📊 Dashboard & Visualization

The simulation features a real-time TUI (Text User Interface) powered by `Rich`.

### Panels
1.  **Market Status**:
    - Displays the current **Last Traded Price**.
    - Shows the **Best Bid** and **Best Ask** (the spread).
    - Metrics on market depth (number of active orders).

2.  **Live Feed**:
    - A scrolling log of agent decisions.
    - **Color Coded**: Green (Buy), Red (Sell), Yellow (Hold).
    - **Details**: Shows the exact model used (e.g., `Llama 70B`) and the agent's internal reasoning (e.g., *"Price is too high relative to moving average"*).

### Controls
- Press `Ctrl+C` to gracefully stop the simulation and exit.

---

## 📁 Project Structure

```bash
/
├── main.py              # Entry point & Simulation Loop
├── src/
│   ├── agents/          # Agent logic
│   │   ├── base.py      # Abstract base class
│   │   └── trader.py    # LLM-based implementation
│   ├── market/          # Market mechanics
│   │   ├── engine.py    # Facade
│   │   ├── order_book.py# Matching logic (Heaps)
│   │   ├── ledger.py    # Database adapter
│   │   └── schema.py    # Data models (Pydantic/SQLModel)
│   └── utils/           # Helpers (Personas)
├── logs/                # Execution logs (generated at runtime)
├── Dockerfile           # Container config
└── pyproject.toml       # Dependencies
```

## 🛠️ Development

- **Adding a new Agent**: Inherit from `src.agents.base.BaseAgent` and implement the `act` method.
- **Changing Personas**: Edit `src/utils/personas.py`.
- **Database**: The simulation uses a local `market.db` SQLite file. You can inspect it with any SQLite viewer.

## 📝 License

[MIT License](LICENSE)