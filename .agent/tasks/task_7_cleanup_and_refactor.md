# Task 7: Cleanup and Refactor Tests

## 1. Task Overview

### Task Title
**Title:** Codebase Cleanup and Refactoring

### Goal Statement
**Goal:** Remove redundancy, enforce project structure conventions, and improve code quality by converting ad-hoc demo scripts into a proper `unittest` suite, ignoring generated data directories, and refactoring business logic (model mapping, data structures) out of `main.py`.

---

## 2. Project Analysis & Current State

### Technology & Architecture
- **Frameworks & Versions:** Python 3.12+, `unittest` (std lib), `rich` for UI.
- **Language:** Python.
- **Database & ORM:** SQLite (SQLModel), ChromaDB.
- **UI & Styling:** Rich CLI.
- **Key Architectural Patterns:** Agent-based simulation.

### Current State
- `plots/` directory is not gitignored.
- `tests/` contains executable demo scripts (`demo_agent.py`, `demo_market.py`) which are now redundant.
- `main.py` contains hardcoded model mapping logic and loose dictionary structures for logging.
- `ai-task-templates-main` contains the mandatory task skeleton (**DO NOT TOUCH**).

---

## 3. Context & Problem Definition

### Problem Statement
The codebase has generated artifacts tracked by git, uses ad-hoc scripts for testing, and mixes configuration/logic in the entry point `main.py`.

### Success Criteria
- [ ] `plots/` is added to `.gitignore`.
- [ ] `tests/demo_agent.py` and `tests/demo_market.py` are removed.
- [ ] `get_model_for_persona` and keywords moved to `src/utils/personas.py`.
- [ ] `ActionLog` class defined in `src/market/schema.py`.
- [ ] `main.py` uses `ActionLog` and imports persona logic.
- [ ] `ai-task-templates-main` remains **EXACTLY** as is.

---

## 4. Development Mode Context

### Development Mode Context
- **🚨 Project Stage:** Early development/Refactoring.
- **Breaking Changes:** Internal refactoring only.
- **Priority:** Cleanup and Standardization.

---

## 5. Technical Requirements

### Functional Requirements
- System must behave exactly as before, just with cleaner code structure.

### Non-Functional Requirements
- Tests must pass after refactoring.

---

## 9. Implementation Plan

1.  **Modify `.gitignore`**: Append `plots/`.
2.  **Remove Legacy**: Delete `demo_agent.py` and `demo_market.py`.
3.  **Refactor Personas**: Move `SMART_GROQ_KEYWORDS` etc. and `get_model_for_persona` to `src/utils/personas.py`.
4.  **Refactor Schema**: Add `ActionLog` model to `src/market/schema.py`.
5.  **Update Main**: Update `main.py` to use new imports and class.
6.  **Verify**: Run tests.

---

## 10. Task Completion Tracking

- [ ] `.gitignore` updated.
- [ ] Old demo files removed.
- [ ] Personas refactored.
- [ ] Schema refactored.
- [ ] Main updated.
- [ ] Tests passed.
