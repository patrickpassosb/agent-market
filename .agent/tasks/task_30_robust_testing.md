# Task: Improve Robustness and Coverage of Tests

## 1. Task Overview
**Goal:** Increase project test coverage to >80% and fix existing test failures to ensure system stability.

## 2. Project Analysis & Current State
- **Current Coverage:** 54%
- **Failing Tests:** `tests/test_api_integration.py::test_websocket_connection`
- **Critical Gaps:**
    - `src/market/engine.py` (27%)
    - `src/simulation/runner.py` (27%)
    - `src/analysis/` (0%)

## 3. Success Criteria
- [x] Fix `test_websocket_connection` failure.
- [x] Increase `src/market/engine.py` coverage to >70%. (Currently 90%)
- [x] Increase `src/simulation/runner.py` coverage to >70%. (Currently 86%)
- [x] Add basic tests for `src/analysis/chart.py` and `src/analysis/report.py`. (Currently 91%)
- [x] Resolve Pydantic deprecation warnings in tests.
- [x] All tests pass in the CI-like environment (`uv run pytest`). (Total coverage 88%)

## 4. Implementation Plan
1. **Fix WebSocket Test:** Update `TestClient` initialization in `tests/test_api_integration.py` to handle `TrustedHostMiddleware`.
2. **Engine Tests:** Add unit tests for `MarketEngine` methods: `place_order`, `cancel_order`, `execute_trades`, and edge cases like insufficient funds.
3. **Runner Tests:** Mock agent interactions and market engine to test simulation loop orchestration.
4. **Analysis Tests:** Add simple validation tests for report and chart generation (can mock file writing/plotting).
5. **Clean up Warnings:** Update `model_fields` access to use class-level access as recommended by Pydantic V2.11.

## 5. AI Agent Instructions
- Use `uv run pytest` for verification.
- Mock external LLM calls (litellm) consistently.
- Ensure tests are deterministic where possible.
