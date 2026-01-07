# Task 5: Observability & Documentation

## 1. Task Overview

### Task Title
**Title:** Observability, Journalist Agent, and Documentation

### Goal Statement
**Goal:** Enhance the simulation with "proof of work" artifacts (plots), a narrative layer (Journalist Agent), and professional documentation (README/Docs) to meet all hackathon submission requirements.

---

## 2. Project Analysis & Current State

### Technology & Architecture
- **Plots:** `matplotlib` + `sqlite3`.
- **Journalist:** New `Journalist` agent class interacting with `Ledger`.
- **Docs:** Markdown.

### Current State
- `main.py` runs a 12-agent loop.
- `Ledger` records transactions.
- **Missing:** Visual analysis and user-facing docs.

## 3. Context & Problem Definition

### Problem Statement
The project works but lacks the "polish" and "evidence" required for a winning submission. We need to show *what happened* during the simulation, not just that it ran.

### Success Criteria
- [ ] `analyze_market.py` generates a price history chart from `market.db`.
- [ ] `Journalist` agent prints a "Breaking News" headline to the UI every N ticks.
- [ ] `README.md` is updated with setup instructions and architecture overview.

---

## 9. Implementation Plan

- Step 1: Create `src/analysis/chart.py` (or similar) to plot data.
- Step 2: Implement `src/agents/journalist.py`.
- Step 3: Integrate Journalist into `main.py`.
- Step 4: Write `README.md`.

## 12. AI Agent Instructions

### Implementation Workflow
1.  **Analysis:** Write script to query DB and plot price/volume.
2.  **Journalist:** Simple agent that takes market state + recent trades -> LLM -> Headline.
3.  **Docs:** Clean up the repo.
