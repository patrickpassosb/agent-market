# AI Task Planning Template - Pre-Commit Code Review (Task 28)

## 1. Task Overview

### Task Title
**Title:** Comprehensive Pre-Commit Code Review & Quality Assurance

### Goal Statement
**Goal:** Conduct a thorough audit of the current codebase to identify logic bugs, performance bottlenecks, security vulnerabilities, and code style violations before final commit, ensuring the system is stable, efficient, and maintainable.

---

## 2. Project Analysis & Current State

### Technology & Architecture
- **Frameworks & Versions:** Python 3.12, FastAPI, LiteLLM, SQLModel.
- **Key Patterns:** Asynchronous Event Loop, Multi-Agent Simulation, Persistent Ledger.

### Current State
The project has undergone significant refactoring to move to an async architecture and has had a security hardening pass. Recent changes includes moving to a singleton `OrderBook` and adding API authentication.

## 3. Context & Problem Definition

### Problem Statement
Rapid refactoring can introduce subtle bugs, especially in complex areas like order matching and async concurrency. A final critical review is needed to ensure:
- The single `OrderBook` instance handles multiple assets correctly.
- Error handling is robust across all async boundaries.
- Variable naming is consistent and clear.
- Performance is optimized for parallel LLM calls.

### Success Criteria
- [ ] Logic Audit: No visible bugs in trade matching or portfolio calculations.
- [ ] Performance: Verified efficient use of `asyncio.gather` and rate limiting.
- [ ] Security: No regressions in API key enforcement or sanitization.
- [ ] Style: PEP8 compliance and clear variable naming.
- [ ] Error Handling: No unhandled exceptions that could crash the simulation.

---

## 4. Development Mode Context
- **🚨 Project Stage:** Pre-Release / Final Polish
- **Priority:** Accuracy & Stability

---

## 5. Technical Requirements

### Functional Requirements
- Correct trade execution and P&L tracking.
- Stable API and WebSocket streaming.

### Non-Functional Requirements
- **Maintainability:** Clear code structure.
- **Resilience:** Graceful handling of LLM timeouts or failures.

---

## 9. Implementation Plan

### Phase 1: Logic & Performance Fixes
- [ ] Fix redundant `import math` in `src/market/engine.py` <!-- id: 1 -->
- [ ] Update `MarketEngine` docstrings to reflect the single `OrderBook` refactor <!-- id: 2 -->
- [ ] Increase agent utilization in `SimulationRunner` (execute more than 4 agents per tick) <!-- id: 3 -->
- [ ] Fix "lost order" bug: Implement a mechanism to re-insert orders if portfolio validation fails in `process_action` <!-- id: 4 -->
- [ ] Ensure `initial_capital` is accurately tracked in `Portfolio` post-seeding <!-- id: 5 -->

### Phase 2: Async & Concurrency Audit
- [ ] Verify `SimulationRunner` tick handling and concurrency <!-- id: 6 -->
- [ ] Ensure `process_action` (sync) is safe when called from concurrent coroutines (it is, due to single event loop, but worth documenting) <!-- id: 7 -->

### Phase 3: Cleanup & Refinement
- [ ] Consistent docstrings and variable names.
- [ ] Remove any leftover debugging code or hardcoded defaults.

---

## 10. Task Completion Tracking
- [/] Phase 1: Logic Audit
- [ ] Phase 2: Async Audit
- [ ] Phase 3: Cleanup
