# AI Task Planning Template - Health Check and Bug Fixes

## 1. Task Overview

### Task Title
**Title:** Project Health Check and Bug Fixes

### Goal Statement
**Goal:** Verify the project's overall health, fix identified bugs in the API and simulation engine, and improve test coverage for analysis modules.

---

## 2. Project Analysis & Current State

### Technology & Architecture
- **Frameworks & Versions:** FastAPI, SQLModel, LiteLLM, Next.js
- **Language:** Python 3.12, TypeScript
- **Database & ORM:** SQLite, SQLModel
- **UI & Styling:** React, Tailwind CSS
- **Key Architectural Patterns:** Multi-agent simulation, Event-driven (WebSockets)

### Current State
The project was mostly functional but had several critical bugs:
1. WebSocket tests were failing due to `TrustedHostMiddleware` configuration.
2. Pydantic deprecation warnings were cluttering test output.
3. `main.py` had a syntax error preventing startup.
4. Analysis modules had 0% test coverage.

## 3. Context & Problem Definition

### Problem Statement
The codebase had accumulated minor technical debt and regressions that hindered automated testing and manual execution.

### Success Criteria
- [x] All automated tests pass.
- [x] WebSocket integration tests pass.
- [x] Pydantic deprecation warnings are resolved.
- [x] `main.py` starts without syntax errors.
- [x] Analysis and chart modules have unit tests.
- [x] Frontend builds successfully.

---

## 4. Development Mode Context
- **🚨 Project Stage:** Development/Stabilization
- **Priority:** High (Stability)

---

## 5. Technical Requirements

### Functional Requirements
- API must allow WebSocket connections from `testserver` during testing.
- Simulation must run for a specified number of ticks and exit gracefully.
- Analysis reports and charts must be generated correctly from market data.

---

## 6. Implementation Plan

### Phase 1: Bug Fixes
- [x] Update `src/api/server.py` to allow `testserver` in `TrustedHostMiddleware`.
- [x] Fix Pydantic V2.11+ deprecation warnings in `src/agents/journalist.py` and `src/agents/trader.py`.
- [x] Fix triple-quote docstring in `main.py`.

### Phase 2: Testing & Coverage
- [x] Create `tests/test_analysis.py` to test `src/analysis/report.py` and `src/analysis/chart.py`.
- [x] Fix `Ledger` initialization and `timestamp` types in tests.
- [x] Resolve Seaborn future warnings in `src/analysis/chart.py`.

### Phase 3: Verification
- [x] Run `uv run pytest --cov=src` (Achieved 88% coverage).
- [x] Verify frontend build with `npm run build`.
- [x] Verify `main.py` execution.

---

## 12. AI Agent Instructions

### Implementation Workflow
1. Identify failing tests and warnings.
2. Apply targeted fixes.
3. Add missing tests for uncovered modules.
4. Run full suite to verify.
