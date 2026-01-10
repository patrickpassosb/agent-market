# AI Task Planning Template - Code Review Fixes

> **About This Template:** This is a systematic framework for planning and executing technical projects with AI assistance. Use this structure to break down complex features, improvements, or fixes into manageable, trackable tasks that AI agents can execute effectively.

---

## 1. Task Overview

### Task Title
**Title:** Comprehensive Code Review Fixes & Performance Optimization

### Goal Statement
**Goal:** Address critical performance bottlenecks, concurrency issues, and logical bugs identified in the code review to verify the system is scalable, thread-safe, and robust.

---

## 2. Project Analysis & Current State

### Technology & Architecture
- **Frameworks & Versions:** Python 3.12, FastAPI, LiteLLM, Rich, Pydantic v2.
- **Key Patterns:** Facade (MarketEngine), Multi-Agent Loop, Async API (FastAPI) vs Sync Simulation Loop.

### Current State
The system functions as a prototype but suffers from blocking LLM calls (destroying tick rate performance), thread-safety risks in the API, and several hardcoded logic fragilities.

## 3. Context & Problem Definition

### Problem Statement
1. **Blocking I/O:** `Trader.act` calls `litellm.completion` synchronously, pausing the entire simulation for seconds per agent.
2. **Race Conditions:** `src/api/server.py` reads shared simulation state (`agents`, `engine`) without locks while a background thread modifies it.
3. **Logic Bugs:** Portfolio ROI calculation uses a hardcoded `1.5` initial capital, ignoring actual seed inventory.
4. **Fragility:** Personas use string matching; Prompts are hardcoded strings.

### Success Criteria
- [ ] `Trader.act` and the main simulation loop are asynchronous (`asyncio`).
- [ ] Simulation loop runs concurrent agent actions (`asyncio.gather`).
- [ ] API Server runs simulation on the main event loop (removing threading/locking complexity).
- [ ] Portfolio `initial_capital` is dynamic and accurate.
- [ ] Personas use an `Enum` based approach.
- [ ] `OrderBook` usage is refactored to remove redundant dictionaries.

---

## 4. Development Mode Context

- **Project Stage:** Prototype -> Production Refactor
- **Breaking Changes:** Internal API changes are expected (Sync -> Async).
- **Priority:** High (Performance & Correctness)

---

## 5. Technical Requirements

### Functional Requirements
- System must support >1 tick per second effectively (dependent on LLM latency, but not blocked serially).
- API endpoints must return consistent data without race conditions.

### Non-Functional Requirements
- **Performance:** Asynchronous execution of IO-bound tasks.
- **Code Quality:** Type hints, distinct separation of concerns.

---

## 6. Data & Database Changes

N/A - Schema remains mostly same, though `Ledger` interactions might need to ensure they are async-friendly or thread-safe if SQLite is accessed concurrently (though typically serialized).

---

## 7. API & Backend Changes

- **Server:** Refactor `SimulationRunner` to be fully async. Remove `threading` entirely. Use FastAPI's main event loop for both API requests and the simulation tick loop.

---

## 8. Frontend Changes

N/A

---

## 9. Implementation Plan

### Phase 1: Async Conversion (High Impact)
1.  **Refactor `Trader.act`**:
    -   Modify `src/agents/trader.py` to make `act` an `async def`.
    -   Use `litellm.acompletion` instead of `completion`.
2.  **Refactor `MarketEngine`**:
    -   Ensure `process_action` is thread-safe or async-compatible if needed (mostly CPU bound, so sync is fine, but needs to be called from async context).
3.  **Refactor `main.py` Loop**:
    -   Use `asyncio.run(main())`.
    -   Use `await asyncio.gather(*[agent.act(...) for agent in agents])` for concurrency.

### Phase 2: Event Loop Integration (No Locks)
1.  **Update `src/api/server.py`**:
    -   Remove `threading.Thread` usage.
    -   Launch simulation loop as a background `asyncio.Task` using `asyncio.create_task` within FastAPI's `lifespan`.
    -   Since everything runs on the single main event loop, race conditions between API reads and simulation writes are eliminated (as long as we don't `await` during critical state updates, which is the default in Python async).

### Phase 3: Logic Fixes
1.  **Portfolio Fix (`src/agents/portfolio.py`)**:
    -   Add `initial_capital` field to `Portfolio` model.
    -   Set it correctly during initialization or `seed_position`.
2.  **OrderBook Refactor (`src/market/engine.py`)**:
    -   Simplify initialization to avoid `OrderBook` per asset if `OrderBook` handles multiple assets internally.

### Phase 4: Code Hygiene
1.  **Personas (`src/utils/personas.py`)**:
    -   Create `PersonaStrategy(Enum)`.
    -   Update `Trader` to check Enum instead of string matching.
2.  **Prompts**:
    -   Extract hardcoded prompts in `Trader` to a `src/prompts/` module.

---

## 10. Task Completion Tracking

- [x] Async Refactor Complete
- [x] Thread Safety Implemented
- [x] Portfolio Bug Fixed
- [x] Code Hygiene Improvements

---

## 12. AI Agent Instructions

### Implementation Workflow
- Start with `src/agents/trader.py` to enable async.
- Move to `main.py` to prove the speedup.
- Then address the API server safety.
- Finally apply the logic/hygiene fixes.

### Code Quality Standards
- Use `asyncio` best practices.
- Ensure `pyproject.toml` dependencies support async (FastAPI does, Litellm does).

---