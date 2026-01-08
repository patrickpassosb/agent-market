# Task 9: Repo Cleanup Review for Unnecessary Files and Redundancy

> **About This Template:** This is a systematic framework for planning and executing technical projects with AI assistance. Use this structure to break down complex features, improvements, or fixes into manageable, trackable tasks that AI agents can execute effectively.

---

## 1. Task Overview

### Task Title
**Title:** Repo Cleanup Review for Unnecessary Files and Redundancy

### Goal Statement
**Goal:** Identify unnecessary or redundant files, suggest removals or consolidations, and propose project-structure improvements that reduce clutter and improve maintainability without breaking core behavior.

---

## 2. Project Analysis & Current State

### Technology & Architecture
- **Frameworks & Versions:** Rich, Streamlit (not in deps), LiteLLM, ChromaDB, SQLModel, Pydantic
- **Language:** Python 3.12+
- **Database & ORM:** SQLite + SQLModel
- **UI & Styling:** Rich TUI (CLI), matplotlib/seaborn for plots
- **Authentication:** None
- **Key Architectural Patterns:** Facade (MarketEngine), LOB matching with heaps

### Current State
Core simulation loop in `main.py` with agents calling LiteLLM; in-memory order book; SQLite ledger; ChromaDB memory; minimal test demos.

## 3. Context & Problem Definition

### Problem Statement
The user requests a focused review to spot unnecessary files and redundancy, plus suggestions for pruning and organizing the project for better structure and code quality.

### Success Criteria
- [ ] Provide a prioritized list of files/directories that are likely artifacts or redundant, with evidence or reasoning.
- [ ] Recommend safe removals, consolidations, or moves, including any required updates to docs or config.
- [ ] Suggest structural improvements to reduce duplication and improve maintainability.

---

## 4. Development Mode Context

### Development Mode Context
- **🚨 Project Stage:** Prototype / challenge project
- **Breaking Changes:** Avoid unless clearly justified
- **Data Handling:** Do not propose destructive changes without alternatives
- **User Base:** Developers/evaluators running local simulation
- **Priority:** Stability and correctness over speed

---

## 5. Technical Requirements

### Functional Requirements
- Review repository contents to identify unnecessary files and redundancy.

### Non-Functional Requirements
- **Performance:** Optional if any redundancy impacts performance or startup time.
- **Security:** Flag sensitive artifacts committed accidentally.
- **Usability:** Identify confusing structure or duplicated docs.
- **Responsive Design:** N/A unless frontend present.
- **Theme Support:** N/A unless frontend present.

### Technical Constraints
- Must work within existing codebase and patterns.
- No external network access unless approved.

---

## 6. Data & Database Changes

### Database Schema Changes
None. Review only.

### Data Model Updates
None. Review only.

### Data Migration Plan
None.

---

## 7. API & Backend Changes

### Data Access Pattern Rules
Review only; no changes unless requested.

### Server Actions
N/A

### Database Queries
Review query safety and performance.

---

## 8. Frontend Changes

### New Components
N/A

### Page Updates
N/A

### State Management
N/A

---

## 9. Implementation Plan

1. Inventory repo files and identify generated artifacts, caches, logs, and outputs.
2. Cross-check references in code/docs/config to avoid false positives.
3. Deliver prioritized cleanup recommendations with rationale and any needed updates.

---

## 10. Task Completion Tracking

### Real-Time Progress Tracking
- Update this task after completing each scan phase.

---

## 11. File Structure & Organization

- Existing files only; no new files expected.

---

## 12. AI Agent Instructions

### Implementation Workflow
🎯 **MANDATORY PROCESS:**
1. Use Context7 for any library/framework usage referenced in findings.
2. Prefer precise file references and minimal tokens.
3. Do not change code unless requested.

### Communication Preferences
Concise, prioritized findings with file references.

### Code Quality Standards
Follow repo conventions; highlight deviations.

---

## 13. Second-Order Impact Analysis

### Impact Assessment
Highlight only if a finding could cascade (e.g., data corruption, auth bypass, systemic perf issues).

---

**🎯 Ready to Plan Your Next Project?**

This template gives you the framework - now fill it out with your specific project details! 

*Want the complete version with detailed examples, advanced strategies, and full AI agent workflows? [Watch the full tutorial video here]*

---

*This template is part of ShipKit - AI-powered development workflows and templates*  
*Get the complete toolkit at: https://shipkit.ai* 
