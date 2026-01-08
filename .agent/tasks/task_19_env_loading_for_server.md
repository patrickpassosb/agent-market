# AI Task Planning Template - Starter Framework

> **About This Template:** This is a systematic framework for planning and executing technical projects with AI assistance. Use this structure to break down complex features, improvements, or fixes into manageable, trackable tasks that AI agents can execute effectively.

---

## 1. Task Overview

### Task Title
<!-- Give your task a clear, specific name that describes what you're building or fixing -->
**Title:** Load .env for FastAPI Server to Enable Local Provider Routing

### Goal Statement
<!-- Write one paragraph explaining what you want to achieve and why it matters for your project -->
**Goal:** Ensure the FastAPI server loads `.env` so provider order and local Ollama settings are honored, allowing the simulation to progress without external rate-limit failures.

---

## 2. Project Analysis & Current State

### Technology & Architecture
<!-- This is where you document your current tech stack so the AI understands your environment -->
- **Frameworks & Versions:** FastAPI, python-dotenv
- **Language:** Python
- **Database & ORM:** SQLite via MarketEngine
- **UI & Styling:** N/A
- **Authentication:** Provider API keys via env
- **Key Architectural Patterns:** FastAPI lifespan startup

### Current State
<!-- Describe what exists today - what's working, what's broken, what's missing -->
`src/api/server.py` does not load `.env`, so provider config defaults are used. This causes the simulation loop to hit external LLM rate limits and stop advancing.

## 3. Context & Problem Definition

### Problem Statement
<!-- This is where you clearly define the specific problem you're solving -->
The server starts without `.env` variables, ignoring `MODEL_PROVIDER_ORDER=ollama` and Ollama settings, leading to rate-limit failures and a stalled live feed.

### Success Criteria
<!-- Define exactly how you'll know when this task is complete and successful -->
- [x] `src/api/server.py` loads `.env` on startup using python-dotenv.
- [x] Provider routing uses `.env` values (verified by running server and checking tick progression).
- [x] Add Context7 citation comment for python-dotenv usage.

---

## 4. Development Mode Context

### Development Mode Context
<!-- This is where you tell the AI agent about your project's constraints and priorities -->
- **🚨 Project Stage:** New development
- **Breaking Changes:** Avoid
- **Data Handling:** No data changes
- **User Base:** Internal demo/dev
- **Priority:** Restore live simulation updates

---

## 5. Technical Requirements

### Functional Requirements
<!-- This is where the AI will understand exactly what the system should do - be specific about user actions and system behaviors -->
- Load `.env` during FastAPI startup.
- Do not override already-set environment variables by default.

### Non-Functional Requirements
<!-- This is where you define performance, security, and usability standards -->
- **Performance:** No measurable impact
- **Security:** No changes
- **Usability:** Live feed updates reliably
- **Responsive Design:** N/A
- **Theme Support:** N/A

### Technical Constraints
<!-- This is where you list limitations the AI agent must work within -->
- Use python-dotenv `load_dotenv()`.
- Keep changes minimal.

---

## 6. Data & Database Changes

### Database Schema Changes
<!-- This is where you specify any database modifications needed -->
None.

### Data Model Updates
<!-- This is where you define TypeScript types, schema updates, or data structure changes -->
None.

### Data Migration Plan
<!-- This is where you plan how to handle existing data during changes -->
None.

---

## 7. API & Backend Changes

### Data Access Pattern Rules
<!-- This is where you tell the AI agent how to structure backend code in your project -->
No API changes.

### Server Actions
<!-- List the backend mutation operations you need -->
None.

### Database Queries
<!-- Specify how you'll fetch data -->
N/A.

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

1. Load `.env` at server startup using python-dotenv.
2. Confirm provider routing uses `.env` by observing advancing tick count.
3. Update success criteria checklist.

---

## 10. Task Completion Tracking

### Real-Time Progress Tracking
<!-- This is where you tell the AI agent to update progress as work is completed -->
Update checklist when done.

---

## 11. File Structure & Organization

- `src/api/server.py`

---

## 12. AI Agent Instructions

### Implementation Workflow
<!-- This is where you give specific instructions to your AI agent -->
🎯 **MANDATORY PROCESS:**
- Use Context7 for python-dotenv usage
- Add Context7 citation in code comments
- Keep changes minimal

### Communication Preferences
<!-- This is where you set expectations for how the AI should communicate -->
Concise updates with file paths.

### Code Quality Standards
<!-- This is where you define your coding standards for the AI to follow -->
Readable, minimal changes.

---

## 13. Second-Order Impact Analysis

### Impact Assessment
<!-- This is where you think through broader consequences of your changes -->
Low risk; `.env` loading affects runtime configuration only.

---

**🎯 Ready to Plan Your Next Project?**

This template gives you the framework - now fill it out with your specific project details!

*Want the complete version with detailed examples, advanced strategies, and full AI agent workflows? [Watch the full tutorial video here]*

---

*This template is part of ShipKit - AI-powered development workflows and templates*  
*Get the complete toolkit at: https://shipkit.ai* 
