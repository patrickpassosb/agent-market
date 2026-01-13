# AI Task Planning Template - Critical Review Fixes

## 1. Task Overview

### Task Title
**Title:** Critical Review Fixes (Security, Atomicity, & Robustness)

### Goal Statement
**Goal:** Address high-priority findings from the code review: secure the API against unauthorized access, ensure transaction atomicity in the Market Engine to prevent state corruption, and fix edge-case logic in the Trader agent.

---

## 2. Project Analysis & Current State

### Technology & Architecture
- **Frameworks:** FastAPI, Python 3.12, AsyncIO.
- **Key Components:** `Trader` (Agent), `MarketEngine` (Logic), `SimulationRunner` (Loop), `FastAPI` (Server).

### Current State
- **Security:** `src/api/server.py` allows open access if `API_KEY` is not set in environment variables.
- **Reliability:** `src/market/engine.py` uses an "optimistic execution" pattern (match order -> execute portfolio -> rollback if failed) which is prone to state inconsistency if the rollback fails.
- **Logic:** `src/agents/trader.py` has a fallback for zero prices that might mask actual zero-price market conditions.

## 3. Context & Problem Definition

### Problem Statement
1.  **Security Vulnerability:** If the server is deployed without an `API_KEY`, it defaults to open access, potentially exposing the simulation to the public internet.
2.  **Data Integrity Risk:** The "pop and re-insert" logic in `MarketEngine` breaks transaction atomicity. If an error occurs during re-insertion, the order is lost (user loses money/asset without trade).
3.  **Market Distortion:** Forcing a `0.001` price when the market is `0` prevents agents from reacting to a true collapse.
4.  **Liquidity Loss Bug:** If a taker fails validation after a maker order is popped, the maker order is lost and liquidity disappears.

### Success Criteria
- [ ] API rejects requests if `API_KEY` is invalid, AND fails securely (or warns heavily) if `API_KEY` is missing.
- [ ] `MarketEngine` verifies portfolio feasibility *before* matching orders (Pre-check pattern).
- [ ] `Trader` logic handles zero/negative prices gracefully without hardcoded magic numbers if possible, or logs them clearly.
- [ ] Maker orders are restored (or never removed) when taker validation fails post-match.

---

## 4. Development Mode Context
- **Priority:** Immediate / Critical.
- **Breaking Changes:** Minimal.
- **Constraints:** Must maintain the `async` improvements from Task 23.

---

## 9. Implementation Plan

### Phase 1: Security Hardening (`src/api/server.py`)
- [ ] Modify `get_api_key` dependency.
- [ ] Logic: If `API_KEY` env var is missing, either defaults to a secure reject state OR logs a critical warning (dev mode).
- [ ] Enforce `API_KEY` check properly: `if expected_key and supplied_key != expected_key: raise 403`.

### Phase 2: Transaction Atomicity (`src/market/engine.py`)
- [ ] Add `check_funds` / `check_inventory` methods to `Portfolio` (or use existing).
- [ ] Refactor `process_action`:
    1.  Validate inputs.
    2.  **Check Portfolio** (Dry Run).
    3.  If valid, **Execute Order** in `OrderBook`.
    4.  If matched, **Execute Portfolio** (Commit).
- [ ] Remove "Re-insert" logic.
 - [ ] Restore maker order when taker validation fails after a match.

### Phase 3: Edge Case Fixes (`src/agents/trader.py`)
- [ ] Review `decision.price` logic.
- [ ] Allow price `0` if that's the genuine market price, or handle it as "Market Order" (if implemented).

---

## 10. Task Completion Tracking

- [x] Security Hardening
- [x] Transaction Atomicity
- [x] Edge Case Fixes

---

## 12. AI Agent Instructions

- **Safe Mode:** Do not break the existing async loop.
- **Verify:** Run a manual test or script to verify API rejection.
