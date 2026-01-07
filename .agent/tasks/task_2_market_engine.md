# Task 2: Market Engine Implementation

## 1. Task Overview

### Task Title
**Title:** Market Engine Core Implementation

### Goal Statement
**Goal:** Implement the core trading logic of the simulation, including the `OrderBook` for matching orders, the `Ledger` for transaction persistence, and the central `Market` engine to coordinate ticks and agent actions.

---

## 2. Project Analysis & Current State

### Technology & Architecture
- **Language:** Python 3.12+
- **Database:** SQLite + SQLModel
- **Classes:**
    - `OrderBook`: In-memory matching engine.
    - `Ledger`: Database interface for transactions.
    - `Market`: Central controller.

### Current State
- `src/market/schema.py` defines `AgentAction`, `Transaction`, `MarketState`.
- No logic implementations yet.

## 3. Context & Problem Definition

### Problem Statement
The simulation needs a central mechanism to process agent orders, determine market prices, and record history.

### Success Criteria
- [ ] `OrderBook` correctly matches buy/sell orders based on price.
- [ ] `Ledger` successfully saves transactions to SQLite.
- [ ] `Market` engine runs a "step", collecting actions and executing trades.
- [ ] Basic unit tests/demonstration in `main.py` or a test script verifies matching logic.

---

## 5. Technical Requirements

### Functional Requirements
- **Order Matching:**
    - Buy orders at $X match Sell orders at <= $X.
    - Execution price is typically the generic crossing price or specific logic (e.g., midpoint or older order's price). *Decision: Use older order's price (maker-taker style) or simple crossover.*
- **Persistence:** All matched trades must be saved.

---

## 9. Implementation Plan

- Step 1: Implement `src/market/ledger.py` (Database setup & writes).
- Step 2: Implement `src/market/order_book.py` (Matching logic).
- Step 3: Implement `src/market/engine.py` (Orchestrator).
- Step 4: Verify with a script.
