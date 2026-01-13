# AI Task Planning Template - Starter Framework

> **About This Template:** This is a systematic framework for planning and executing technical projects with AI assistance. Use this structure to break down complex features, improvements, or fixes into manageable, trackable tasks that AI agents can execute effectively.

---

## 1. Task Overview

### Task Title
**Title:** Five-Star Readiness: Distinct Personas + Memory Retrieval

### Goal Statement
**Goal:** Improve persona distinctiveness and memory retrieval so the simulation meets five-star rubric expectations, and update documentation to clearly describe the demo flow and evidence artifacts.

---

## 2. Project Analysis & Current State

### Technology & Architecture
- **Frameworks & Versions:** Python 3.12, litellm, sqlmodel, chromadb, rich
- **Language:** Python
- **Database & ORM:** SQLite + SQLModel
- **UI & Styling:** Rich terminal UI, Next.js dashboard
- **Authentication:** N/A
- **Key Architectural Patterns:** Facade engine, multi-agent loop, RAG memory

### Current State
- Personas are defined but assigned with replacement, so distinctness is not guaranteed.
- Memory retrieval is generic and does not filter by asset or interaction type.
- README describes how to run, but demo flow is not explicitly labeled.

## 3. Context & Problem Definition

### Problem Statement
The project needs guaranteed distinct personas and richer memory retrieval signals to align with the multi-agent rubric, and a clearer demo guide to reach five-star readiness.

### Success Criteria
- [x] Agent selection assigns distinct personas for standard 12-agent runs.
- [x] Memory retrieval filters by item/interaction type and stores richer metadata.
- [x] README explicitly documents a Demo Guide section with end-to-end commands and evidence outputs.

---

## 4. Development Mode Context

### Development Mode Context
- **🚨 Project Stage:** Active development
- **Breaking Changes:** Avoid
- **Data Handling:** Preserve existing DB/log artifacts
- **User Base:** Evaluators and reviewers
- **Priority:** Clarity and correctness

---

## 5. Technical Requirements

### Functional Requirements
- System automatically assigns distinct persona strategies when agent count <= available strategies.
- System stores decision/trade memories with metadata and retrieves relevant memories per asset.
- Documentation describes demo flow and evidence artifacts.

### Non-Functional Requirements
- **Performance:** Keep memory queries bounded (n_results <= 5)
- **Security:** N/A
- **Usability:** Clear demo instructions
- **Responsive Design:** N/A
- **Theme Support:** N/A

### Technical Constraints
- Must use existing agent/memory/engine architecture.
- Avoid schema migrations.

---

## 6. Data & Database Changes

### Database Schema Changes
None.

### Data Model Updates
None.

### Data Migration Plan
None.

---

## 7. API & Backend Changes

### Data Access Pattern Rules
Keep logic inside existing modules (`src/utils/personas.py`, `src/memory/memory.py`, agent runners).

### Server Actions
None.

### Database Queries
None (Chroma metadata filters only).

---

## 8. Frontend Changes

No frontend changes.

---

## 9. Implementation Plan

1) Add distinct persona selection helper and use it in `main.py` and `src/simulation/runner.py`.
2) Extend memory to store metadata and query with filters; add trade memories.
3) Update README with a labeled Demo Guide section.

---

## 10. Task Completion Tracking

### Real-Time Progress Tracking
Update checklist items when implemented.

---

## 11. File Structure & Organization

- Modify `src/utils/personas.py`, `src/memory/memory.py`, `src/agents/base.py`, `src/agents/trader.py`, `main.py`, `src/simulation/runner.py`, `README.md`.

---

## 12. AI Agent Instructions

### Implementation Workflow
🎯 **MANDATORY PROCESS:**
Use Context7 for any library usage and cite in code comments.

### Communication Preferences
Concise progress updates.

### Code Quality Standards
Preserve existing style; avoid unnecessary refactors.

---

## 13. Second-Order Impact Analysis

### Impact Assessment
Changes affect agent initialization and memory prompts; ensure no regressions to simulation flow.

---
