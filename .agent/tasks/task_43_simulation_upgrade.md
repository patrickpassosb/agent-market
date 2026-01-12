# Task 43: Simulation Upgrade - Generative Social Layer & Dashboard

## 1. Task Overview

### Task Title
**Title:** Simulation Upgrade - Generative Social Layer & Rich Dashboard

### Goal Statement
**Goal:** Upgrade the existing market simulation to meet the "Generative Agents" and "Agent Laboratory" standards requested in the challenge. This involves adding a "Social Network" layer where agents can communicate publicly, enhancing the agent's decision loop to include this social context, and creating a professional CLI dashboard using `rich` to visualize the market and social dynamics in real-time. Finally, generate post-run artifacts (plots, reports).

---

## 2. Project Analysis & Current State

### Technology & Architecture
- **Frameworks:** Python 3.12, FastAPI, LiteLLM, ChromaDB.
- **UI:** Currently `print()` statements. Target: `rich` library.
- **Agent:** `Trader` class using LLM for `act`.
- **Market:** `MarketEngine` with `OrderBook` and `Ledger`.

### Current State
- The simulation runs a basic loop where agents randomly pick an asset and trade.
- Agents have "Memory" but no "Social" awareness (cannot see what others are saying/doing other than price).
- The output is a scrolling log of text, hard to parse visually.
- No post-simulation visualization is generated automatically.

## 3. Context & Problem Definition

### Problem Statement
The current simulation is a functional "Market" but lacks the "Generative Agent" feel. Agents are isolated traders. To simulate a "Marketplace", there needs to be a social layer (news, rumors, public sentiment) that feeds into the price discovery. Additionally, the user experience of running the simulation is poor (text logs).

### Success Criteria
- [ ] **Social Layer:** A `SocialPlatform` exists where agents can post messages.
- [ ] **Agent Awareness:** Agents consider the "Public Sentiment" (recent posts) when making decisions.
- [ ] **Rich Dashboard:** A TUI (Text User Interface) showing Price Ticker, Order Book, Last Trades, and Social Feed.
- [ ] **Artifacts:** A script generates a price history plot and a summary report after the run.

---

## 5. Technical Requirements

### Functional Requirements
- **SocialPlatform:** A singleton or engine-attached component to store "Posts" (Agent ID, Content, Timestamp).
- **Agent Update:** `Trader.act` must accept `social_feed` as input and potentially produce a `post` as output (or separate action).
- **Dashboard:** Use `rich.layout` to split the screen. Live update using `Live` context manager.

### Non-Functional Requirements
- **Performance:** Rendering the TUI shouldn't slow down the simulation tick significantly.
- **Robustness:** LLM failures in generating "Social Posts" shouldn't crash the market.

---

## 9. Implementation Plan

### Phase 1: Social Layer Backend
- Create `src/market/social.py` with `SocialPlatform` class.
- Update `MarketEngine` to hold an instance of `SocialPlatform`.
- Update `Trader` to optionally generate a "thought/tweet" when acting.

### Phase 2: Agent Logic Update
- Update `src/prompts/trader.py` to include "Recent Social Posts" in the system prompt.
- Update `Trader.act` to fetch recent posts from `MarketEngine.social`.

### Phase 3: Rich Dashboard
- Rewrite `src/simulation/runner.py` loop.
- Use `rich.layout.Layout` with sections: Header, Market (Left), Social (Right), Log (Bottom).
- Implement a `render()` function that builds the view from `MarketEngine` state.

### Phase 4: Analysis & Reporting
- Add `generate_report()` method to `SimulationRunner` (or separate script).
- Use `matplotlib` or `analysis/chart.py` to save plots to `plots/`.

---

## 11. File Structure & Organization

- `src/market/social.py`: New file.
- `src/simulation/dashboard.py`: New file (optional, or keep in runner).
- `src/prompts/trader.py`: Modify.
- `src/agents/trader.py`: Modify.
- `src/simulation/runner.py`: Major refactor.

---
