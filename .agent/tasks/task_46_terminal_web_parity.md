# AI Task Planning Template - Starter Framework

> **About This Template:** This is a systematic framework for planning and executing technical projects with AI assistance. Use this structure to break down complex features, improvements, or fixes into manageable, trackable tasks that AI agents can execute effectively.

---

## 1. Task Overview

### Task Title
**Title:** Terminal/Web Feature Parity

### Goal Statement
**Goal:** Ensure the web simulation flow (API + dashboard) exposes the same functional capabilities and evidence outputs as the terminal simulation.

---

## 2. Project Analysis & Current State

### Technology & Architecture
- **Frameworks & Versions:** Python 3.12, FastAPI, litellm, sqlmodel, chromadb, rich
- **Language:** Python
- **Database & ORM:** SQLite + SQLModel
- **UI & Styling:** Rich terminal UI, Next.js dashboard
- **Authentication:** N/A
- **Key Architectural Patterns:** Facade engine, multi-agent loop, RAG memory

### Current State
- Terminal runner (`main.py`) supports reports, checkpoints, and richer logging.
- Web runner (`src/simulation/runner.py`) lacks report generation and CLI-equivalent controls.

## 3. Context & Problem Definition

### Problem Statement
The web/API simulation does not provide full parity with the terminal simulation, which limits evaluation and demo completeness for reviewers using the dashboard.

### Success Criteria
- [x] Web/API flow can trigger report generation equivalent to terminal runs.
- [x] Web/API flow supports checkpoint generation (configurable).
- [x] Web/API flow exposes similar run metadata (run_id, ticks, summary metrics) for UI/logging.
- [x] README documents how to access parity features in the web flow.
- [x] Control deck inputs align visually with the dashboard design (no misaligned spinners).
- [x] Start/Stop buttons have clear hover/focus feedback consistent with the UI theme.
- [x] Start button hover shifts to a darker primary shade for clearer feedback.
- [x] Market activity chart advances on live ticks even before the first trade.

---

## 4. Development Mode Context

### Development Mode Context
- **🚨 Project Stage:** Active development
- **Breaking Changes:** Avoid
- **Data Handling:** Preserve existing DB/log artifacts
- **User Base:** Evaluators and reviewers
- **Priority:** Consistency and completeness

---

## 5. Technical Requirements

### Functional Requirements
- Provide API endpoints or config to enable reports/checkpoints in the web runner.
- Ensure parity outputs are stored under `reports/`, `checkpoints/`, and `logs/` similarly to terminal runs.
- Keep existing terminal flow unchanged.

### Non-Functional Requirements
- **Performance:** Avoid blocking the event loop during report generation.
- **Security:** N/A
- **Usability:** Clear configuration for enabling parity features.
- **Responsive Design:** N/A
- **Theme Support:** N/A

### Technical Constraints
- Must use existing runner and reporting utilities.
- Avoid new schema migrations.

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
Use `src/api/server.py` and `src/simulation/runner.py` for web flow controls.

### Server Actions
Add endpoints or controls to start/stop runs with report/checkpoint settings.

### Database Queries
Use existing ledger queries for report generation.

---

## 8. Frontend Changes

No new UI required unless needed for parity controls.

---

## 9. Implementation Plan

1) Audit terminal-only features and map to API runner gaps.
2) Add report generation hooks to web runner.
3) Add checkpoint controls for web runner.
4) Update README with web parity instructions.
5) Refine control deck input styles to match the UI.
6) Add hover/focus styles for Start/Stop buttons.

---

## 10. Task Completion Tracking

### Real-Time Progress Tracking
Checklist of parity features implemented.

---

## 11. File Structure & Organization

- Modify `src/simulation/runner.py`, `src/api/server.py`, `README.md`.

---

## 12. AI Agent Instructions

### Implementation Workflow
🎯 **MANDATORY PROCESS:**
Use Context7 for any library usage and cite in code comments.

### Communication Preferences
Concise updates.

### Code Quality Standards
Preserve existing style and patterns.

---

## 13. Second-Order Impact Analysis

### Impact Assessment
Ensure web runner changes do not block the event loop or impact stability.

---
