# Gemini Context for Agent Market

This file provides context for the Gemini CLI agent interacting with the `agent-market` repository.

## 1. Project Overview

**Agent Market** is a multi-agent economic simulation where distinct AI personalities trade assets in a real-time marketplace.
*   **Goal:** Simulate emergent market behavior using a population of heterogeneous agents (Whales, Scalpers, Value Investors).
*   **Core Mechanic:** A double-auction order book matched by a central engine, with agents powered by various LLMs (Llama 3, Gemini, GPT-4o) via `litellm`.
*   **Interface:** A TUI dashboard powered by `rich`.

## 2. Tech Stack

*   **Language:** Python 3.12+
*   **Manager:** `uv` (Project manager & resolver)
*   **LLM Interface:** `litellm` (Unified API for Groq, Gemini, OpenAI)
*   **Database:**
    *   `sqlite` + `sqlmodel` (Transactional Ledger)
    *   `chromadb` (Vector Memory for Agents)
*   **Visualization:** `rich` (Live TUI), `matplotlib`/`seaborn` (Post-hoc analysis)

## 3. Agent Operating Rules (CRITICAL)

**These rules are mandatory for any AI agent working in this repository (derived from `AGENTS.md`).**

### A. Context & Documentation
*   **Context7 MCP:** Use it for library/API documentation. Do not guess API methods.
*   **Dependencies:** Resolve library versions via `pyproject.toml` or `uv`.

### B. Task-Driven Workflow
*   **Task Files:** All non-trivial work must be tracked in a task file in `.agent/tasks/` (or similar).
*   **Template:** Create new tasks by copying `ai-task-templates-main/ai_task_template_skeleton.md`.
    *   *Do not modify the skeleton itself.*
*   **Reuse:** Prefer updating an existing active task over creating a new one if the scope overlaps.

### C. Token Discipline
*   Be concise.
*   Prefer checklists and diffs over long explanations.

## 4. Architecture & Key Files

### Source Layout (`src/`)
*   **`src/market/`**:
    *   `engine.py`: The simulation controller (Facade).
    *   `order_book.py`: Matching logic (Price-Time priority using Heaps).
    *   `ledger.py`: SQLite persistence.
*   **`src/agents/`**:
    *   `trader.py`: Main agent logic (Sense -> Think -> Act).
    *   `base.py`: Abstract base class.
*   **`main.py`**: Entry point. Runs the "Tick" loop and handles the TUI.

### Hybrid LLM Strategy
*   **Whales:** `llama-3.3-70b-versatile` (Deep reasoning)
*   **Value Investors:** `gemini-1.5-flash` (Long context)
*   **Algos:** `gpt-4o-mini` (Structured output)
*   **Retail:** `llama-3.1-8b-instant` (Speed)

## 5. Development & Running

### Prerequisites
*   `.env` file configured (see `.env.example`).
*   `uv` installed.

### Common Commands
*   **Run Simulation:**
    ```bash
    uv run main.py
    ```
*   **Run Analysis:**
    ```bash
    uv run src/analysis/chart.py
    ```
*   **Docker:**
    ```bash
    docker-compose up --build
    ```
