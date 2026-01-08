# AI Task Planning Template - Starter Framework

> **About This Template:** This is a systematic framework for planning and executing technical projects with AI assistance. Use this structure to break down complex features, improvements, or fixes into manageable, trackable tasks that AI agents can execute effectively.

---

## 1. Task Overview

### Task Title
**Title:** Codebase Review for Quality, Performance, and Risk

### Goal Statement
**Goal:** Analyze the current codebase and deliver a prioritized review of issues and improvements across quality, performance, best practices, potential bugs, security, and maintainability, with concrete examples or changes where relevant.

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
The user requests a senior-level code review with prioritized findings and actionable recommendations, focusing on quality, performance, best practices, bugs/edge cases, security, and maintainability.

### Success Criteria
- [ ] Fix item-aware matching, LLM structured output parsing, trend direction, ledger init error handling, action log growth, and input validation.
- [ ] Add tests covering multi-item matching, dict content parsing, trend ordering, and invalid prices.
- [ ] All High/Medium/Low findings addressed without breaking core behavior.

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
- Review existing code; do not add new features.

### Non-Functional Requirements
- **Performance:** Highlight hotspots or avoidable inefficiencies.
- **Security:** Identify vulnerabilities or unsafe patterns.
- **Usability:** Note confusing APIs or sharp edges.
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

1. Update OrderBook structure for item-aware matching and summary.
2. Harden LLM structured output parsing in Trader and Journalist.
3. Fix trend ordering and ledger init error handling.
4. Add validation + bounded action log storage.
5. Add tests for new edge cases.

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
