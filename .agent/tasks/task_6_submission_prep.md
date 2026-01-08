# Task 6: Submission Preparation

## 1. Task Overview

### Task Title
**Title:** Submission Compliance (README & Logging)

### Goal Statement
**Goal:** Finalize the project for submission by ensuring all "Minimum Expected Submission" criteria are met. This involves writing a comprehensive `README.md` and adding persistent file-based logging to the simulation.

---

## 2. Project Analysis & Current State

### Current State
- `src/` code is complete and functional.
- `main.py` runs a live dashboard.
- `Dockerfile` and `docker-compose.yml` exist.
- `README.md` is empty.
- `logs/` directory exists but is empty; no file logging is implemented.

## 3. Context & Problem Definition

### Problem Statement
The project fails the "Minimum Expected Submission" criteria because:
1.  `README.md` is missing required sections (Overview, Architecture, How to Run, Demo).
2.  There are no persistent traces/logs of the system behavior.

### Success Criteria
- [ ] `README.md` created with:
    - [ ] Project Overview
    - [ ] Architecture Description
    - [ ] Setup & Run Instructions (Local + Docker)
    - [ ] Demo Guide
- [ ] `main.py` updated to write structured logs to `logs/simulation_<timestamp>.log`.
- [ ] Log file captures Agent Actions and Market Updates.

---

## 9. Implementation Plan

- Step 1: Update `main.py` to configure a file logger in addition to the Rich console.
- Step 2: Write `README.md` reflecting the actual codebase structure and usage.
- Step 3: Run a short test to verify log generation.

## 12. AI Agent Instructions

### Implementation Workflow
1.  Modify `main.py`:
    - Import `logging`.
    - Configure logging to write to `logs/`.
    - Add `logger.info(...)` calls where `recent_actions` are currently updated.
2.  Draft `README.md`.
