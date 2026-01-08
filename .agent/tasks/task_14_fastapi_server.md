# AI Task Planning Template - Starter Framework

> **About This Template:** This is a systematic framework for planning and executing technical projects with AI assistance. Use this structure to break down complex features, improvements, or fixes into manageable, trackable tasks that AI agents can execute effectively.

---

## 1. Task Overview

### Task Title
<!-- Give your task a clear, specific name that describes what you're building or fixing -->
**Title:** Implement Real-Time FastAPI Server for Market Simulation

### Goal Statement
<!-- Write one paragraph explaining what you want to achieve and why it matters for your project -->
**Goal:** Provide a FastAPI server in `src/api/server.py` that runs the simulation loop in a background thread, exposes market state over REST, and streams live price updates via WebSocket for the frontend dashboard.

---

## 2. Project Analysis & Current State

### Technology & Architecture
<!-- This is where you document your current tech stack so the AI understands your environment -->
- **Frameworks & Versions:** FastAPI, Uvicorn
- **Language:** Python
- **Database & ORM:** SQLite via existing MarketEngine
- **UI & Styling:** N/A
- **Authentication:** None
- **Key Architectural Patterns:** Background simulation thread, REST + WebSocket API

### Current State
<!-- Describe what exists today - what's working, what's broken, what's missing -->
`src/api/server.py` exists with a simulation loop and WebSocket broadcaster, but endpoints and payloads need to align with frontend expectations and the task success criteria.

## 3. Context & Problem Definition

### Problem Statement
<!-- This is where you clearly define the specific problem you're solving -->
Frontend expects `/market/state` and WebSocket `type: ticker` updates, while the server currently provides `/state` and `type: update`. Align the API surface to avoid integration errors.

### Success Criteria
<!-- Define exactly how you'll know when this task is complete and successful -->
- [x] `src/api/server.py` runs under Uvicorn and starts/stops the simulation cleanly.
- [x] `GET /health` returns 200 OK with running status.
- [x] `GET /state` and `GET /market/state` return current prices, assets, and tick count.
- [x] `WebSocket /ws` streams `{"type": "ticker", "data": { ... }}` updates.
- [x] Simulation runs continuously in a background thread without blocking API handlers.

---

## 4. Development Mode Context

### Development Mode Context
<!-- This is where you tell the AI agent about your project's constraints and priorities -->
- **🚨 Project Stage:** New development
- **Breaking Changes:** Acceptable if needed for frontend alignment
- **Data Handling:** No data migration required
- **User Base:** Internal demo and development users
- **Priority:** Correctness and compatibility with frontend

---

## 5. Technical Requirements

### Functional Requirements
<!-- This is where the AI will understand exactly what the system should do - be specific about user actions and system behaviors -->
- System automatically starts simulation on app startup and stops on shutdown.
- System broadcasts ticker updates via WebSocket at a steady cadence.
- Users can retrieve current market state via REST.

### Non-Functional Requirements
<!-- This is where you define performance, security, and usability standards -->
- **Performance:** Non-blocking API, background simulation thread
- **Security:** No auth required
- **Usability:** Simple payloads for frontend consumption
- **Responsive Design:** N/A
- **Theme Support:** N/A

### Technical Constraints
<!-- This is where you list limitations the AI agent must work within -->
- Must use existing `MarketEngine` and agents
- Must keep FastAPI best practices
- Must align with frontend payload expectations

---

## 6. Data & Database Changes

### Database Schema Changes
<!-- This is where you specify any database modifications needed -->
None.

### Data Model Updates
<!-- This is where you define TypeScript types, schema updates, or data structure changes -->
N/A (Python only).

### Data Migration Plan
<!-- This is where you plan how to handle existing data during changes -->
None.

---

## 7. API & Backend Changes

### Data Access Pattern Rules
<!-- This is where you tell the AI agent how to structure backend code in your project -->
Use FastAPI endpoints for REST and WebSocket broadcaster for real-time updates. Keep payloads simple and consistent.

### Server Actions
<!-- List the backend mutation operations you need -->
None.

### Database Queries
<!-- Specify how you'll fetch data -->
Use `MarketEngine` state access methods and current prices in memory.

---

## 8. Frontend Changes

### New Components
<!-- This is where you specify UI components to be created -->
None.

### Page Updates
<!-- This is where you list pages that need modifications -->
None.

### State Management
<!-- This is where you plan how data flows through your frontend -->
N/A.

---

## 9. Implementation Plan

1. Align REST endpoints to support `/state` and `/market/state`.
2. Adjust WebSocket payloads to `type: ticker` with `data` map of prices.
3. Confirm lifespan handling and background thread start/stop.
4. Update success criteria checklist.

---

## 10. Task Completion Tracking

### Real-Time Progress Tracking
<!-- This is where you tell the AI agent to update progress as work is completed -->
Update the success criteria checklist as each item is completed.

---

## 11. File Structure & Organization

- `src/api/server.py`

---

## 12. AI Agent Instructions

### Implementation Workflow
<!-- This is where you give specific instructions to your AI agent -->
🎯 **MANDATORY PROCESS:**
- Use Context7 before FastAPI/Uvicorn API usage
- Keep changes minimal and aligned with frontend requirements
- Update checklist as items complete

### Communication Preferences
<!-- This is where you set expectations for how the AI should communicate -->
Concise updates with file paths and next steps.

### Code Quality Standards
<!-- This is where you define your coding standards for the AI to follow -->
Type-safe, minimal, readable; avoid over-engineering.

---

## 13. Second-Order Impact Analysis

### Impact Assessment
<!-- This is where you think through broader consequences of your changes -->
Low risk; changes are confined to API surface and WebSocket payloads.

---

**🎯 Ready to Plan Your Next Project?**

This template gives you the framework - now fill it out with your specific project details!

*Want the complete version with detailed examples, advanced strategies, and full AI agent workflows? [Watch the full tutorial video here]*

---

*This template is part of ShipKit - AI-powered development workflows and templates*  
*Get the complete toolkit at: https://shipkit.ai* 
