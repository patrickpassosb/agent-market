# Task 8: Cleanup and Refactor Tests

## 1. Task Overview

### Task Title
**Title:** Codebase Cleanup and Refactoring

### Goal Statement
**Goal:** Remove redundancy, enforce project structure conventions, and improve code quality by consolidating docs, archiving completed tasks, untracking runtime artifacts, and refactoring duplicated logic/config out of `main.py`.

---

## 2. Project Analysis & Current State

### Technology & Architecture
- **Frameworks & Versions:** Python 3.12+, `unittest` (std lib), `rich` for UI.
- **Language:** Python.
- **Database & ORM:** SQLite (SQLModel), ChromaDB.
- **UI & Styling:** Rich CLI.
- **Key Architectural Patterns:** Agent-based simulation.

### Current State
- Redundant documentation files overlap (`DEPLOYMENT.md`, `docs/ARCHITECTURE.md`, `TECHNICAL_DOCS.md`).
- Runtime data artifacts are tracked (`chroma_db/`, `market.db`, `demo_market.db`, `.coverage`).
- `main.py` duplicates model mapping logic from `src/utils/personas.py`.
- Hardcoded default item name is duplicated across files.

---

## 3. Context & Problem Definition

### Problem Statement
The codebase has generated artifacts tracked by git, uses ad-hoc scripts for testing, and mixes configuration/logic in the entry point `main.py`.

### Success Criteria
- [ ] `DEPLOYMENT.md`, `docs/ARCHITECTURE.md`, `SUBMISSION_CHECKLIST.md` removed with content merged into `README.md`/`TECHNICAL_DOCS.md`.
- [ ] Runtime artifacts untracked and gitignored (`chroma_db/`, `market.db`, `demo_market.db`, `.coverage`).
- [ ] Duplicate `get_model_for_persona` removed from `main.py` in favor of `src/utils/personas.py`.
- [ ] Default item constant defined and used consistently.
- [ ] Unused imports removed.
- [ ] Missing `__init__.py` files added where required.

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

1.  **Docs Consolidation**: Merge `DEPLOYMENT.md` into `README.md`; merge `docs/ARCHITECTURE.md` into `TECHNICAL_DOCS.md`; delete `SUBMISSION_CHECKLIST.md`.
2.  **Untrack Artifacts**: Remove `chroma_db/`, `market.db`, `demo_market.db`, `.coverage` from git and ensure ignored.
3.  **Refactor Code**: Remove duplicate `get_model_for_persona` from `main.py`, introduce default item constant, clean imports.
4.  **Package Hygiene**: Add missing `__init__.py` files.
5.  **Verify**: Run tests as needed.

---

## 10. Task Completion Tracking

- [ ] Docs consolidated and redundant files removed.
- [ ] Runtime artifacts untracked.
- [ ] Code redundancy removed and constants added.
- [ ] Missing `__init__.py` added.
- [ ] Tests passed (if run).
