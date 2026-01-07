# Task 4: Main Simulation Loop

## 1. Task Overview

### Task Title
**Title:** Main Simulation Loop and CLI Dashboard

### Goal Statement
**Goal:** Implement the entry point `main.py` to run the market simulation. It will initialize the market, spawn a population of diverse agents, and run the simulation loop where agents react to market conditions in real-time, visualized by a `Rich` dashboard.

---

## 2. Project Analysis & Current State

### Technology & Architecture
- **Orchestration:** `main.py`
- **UI:** `rich.live.Live`, `rich.table.Table`, `rich.layout.Layout`.
- **Agents:** `Trader` class (10-20 instances).
- **Market:** `MarketEngine`.

### Current State
- `MarketEngine` and `Trader` are implemented and verified.
- `.env` keys logic is ready.

## 3. Context & Problem Definition

### Problem Statement
We have the components but no "runner". We need a loop that drives time forward and displays what is happening.

### Success Criteria
- [ ] `main.py` runs without error.
- [ ] 10+ Agents are initialized with different personas (e.g., "Bull", "Bear", "HODLer").
- [ ] Simulation Loop processes rounds ("ticks") where every agent gets a valid chance to act.
- [ ] `Rich` UI shows: Current Price, Recent Trades, Order Book, Agent Status.
- [ ] Simulation can be stopped gracefully (Ctrl+C).

---

## 9. Implementation Plan

- Step 1: Implement `src/utils/personas.py` (Helper to generate random agent personas).
- Step 2: Implement `main.py` with `rich` layout.
- Step 3: Integrate the loop: `Market -> Agent -> Action -> Market Update -> UI Update`.
- Step 4: Run full simulation.

## 12. AI Agent Instructions

### Implementation Workflow
1.  Create `src/utils/personas.py` list.
2.  Refactor `main.py` to be the simulation runner.
3.  Use `dotenv` to load keys.
