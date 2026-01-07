# Task 1: Project Scaffolding

## 1. Task Overview

### Task Title
**Title:** Project Scaffolding and Initialization

### Goal Statement
**Goal:** Initialize the `agent-market` project structure, configure dependencies using `uv`, and establish the core data models (`schema.py`). This sets the foundation for the multi-agent market simulation.

---

## 2. Project Analysis & Current State

### Technology & Architecture
- **Language:** Python 3.12+ (managed by `uv`)
- **Database & ORM:** SQLite + SQLModel
- **Libraries:**
    - `pydantic`: Data validation
    - `litellm`: LLM API management
    - `chromadb`: Vector memory
    - `tenacity`: Retry logic
    - `rich`: CLI output
    - `python-dotenv`: Environment variables
- **Architecture:** Directory structure separating market engine, agents, memory, and utils.

### Current State
- `pyproject.toml` exists (basic init).
- `main.py` exists (basic hello world).
- Directory is largely empty.

## 3. Context & Problem Definition

### Problem Statement
The project needs a standard structure and installed dependencies to begin development of the market engine and agents.

### Success Criteria
- [ ] Directory tree created: `src/agents`, `src/market`, `src/memory`, `src/utils`, `logs`.
- [ ] `pyproject.toml` updated with required dependencies.
- [ ] `src/market/schema.py` created with `AgentAction` (Enum), `Transaction` (SQLModel), and `MarketState` (Pydantic).
- [ ] Dependencies install successfully.

---

## 4. Development Mode Context

- **Project Stage:** New Development
- **Priority:** Accuracy and clean structure.

---

## 5. Technical Requirements

### Functional Requirements
- System must have `src` based layout.
- `schema.py` must define the core types for the simulation.

### Technical Constraints
- Use `uv` for dependency management.

---

## 6. Data & Database Changes

### Database Schema Changes
- `Transaction` model defined in `schema.py` will serve as the table definition for SQLite.

---

## 9. Implementation Plan

- Step 1: Install dependencies using `uv`.
- Step 2: Create directory structure.
- Step 3: Create `src/market/schema.py`.
- Step 4: Verify installation and imports.

---

## 12. AI Agent Instructions

### Implementation Workflow
1. Run `uv add ...`
2. Run `mkdir -p ...`
3. Write `src/market/schema.py`
