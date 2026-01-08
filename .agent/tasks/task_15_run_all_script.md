# AI Task Planning Template - Starter Framework

> **About This Template:** This is a systematic framework for planning and executing technical projects with AI assistance. Use this structure to break down complex features, improvements, or fixes into manageable, trackable tasks that AI agents can execute effectively.

---

## 1. Task Overview

### Task Title
<!-- Give your task a clear, specific name that describes what you're building or fixing -->
**Title:** Add a Script to Run Backend + Frontend Together

### Goal Statement
<!-- Write one paragraph explaining what you want to achieve and why it matters for your project -->
**Goal:** Provide a single script that starts the FastAPI server and the Next.js frontend together, with clean shutdown handling and sensible defaults for local development.

---

## 2. Project Analysis & Current State

### Technology & Architecture
<!-- This is where you document your current tech stack so the AI understands your environment -->
- **Frameworks & Versions:** FastAPI, Uvicorn, Next.js
- **Language:** Python, TypeScript
- **Database & ORM:** SQLite via MarketEngine
- **UI & Styling:** Tailwind CSS
- **Authentication:** None
- **Key Architectural Patterns:** Background simulation thread + WebSocket + App Router

### Current State
<!-- Describe what exists today - what's working, what's broken, what's missing -->
Backend and frontend run separately. There is no single script to launch both for local dev.

## 3. Context & Problem Definition

### Problem Statement
<!-- This is where you clearly define the specific problem you're solving -->
Developers must start the backend and frontend in separate terminals. This adds friction and makes demoing harder.

### Success Criteria
<!-- Define exactly how you'll know when this task is complete and successful -->
- [x] A script exists to start both services from repo root.
- [x] The script sets frontend env vars for API and WebSocket URLs.
- [x] Ctrl+C stops both processes cleanly.

---

## 4. Development Mode Context

### Development Mode Context
<!-- This is where you tell the AI agent about your project's constraints and priorities -->
- **🚨 Project Stage:** New development
- **Breaking Changes:** Avoid
- **Data Handling:** No persistence changes
- **User Base:** Internal demo/dev
- **Priority:** Developer experience

---

## 5. Technical Requirements

### Functional Requirements
<!-- This is where the AI will understand exactly what the system should do - be specific about user actions and system behaviors -->
- Start FastAPI server with Uvicorn
- Start Next.js dev server
- Forward environment variables to frontend

### Non-Functional Requirements
<!-- This is where you define performance, security, and usability standards -->
- **Performance:** Must not block on startup
- **Security:** No changes
- **Usability:** Simple, one-command run
- **Responsive Design:** N/A
- **Theme Support:** N/A

### Technical Constraints
<!-- This is where you list limitations the AI agent must work within -->
- Use existing backend entry point `src/api/server.py`
- Use existing `frontend/` app

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

1. Create a `scripts/run_all.sh` script that starts backend and frontend.
2. Add environment variables for frontend API/WS URLs.
3. Ensure clean shutdown with traps.

---

## 10. Task Completion Tracking

### Real-Time Progress Tracking
<!-- This is where you tell the AI agent to update progress as work is completed -->
Update the checklist when script is added.

---

## 11. File Structure & Organization

- `scripts/run_all.sh`

---

## 12. AI Agent Instructions

### Implementation Workflow
<!-- This is where you give specific instructions to your AI agent -->
🎯 **MANDATORY PROCESS:**
- Use Context7 for CLI usage info
- Keep script concise and readable
- Update checklist

### Communication Preferences
<!-- This is where you set expectations for how the AI should communicate -->
Concise updates with file paths and usage command.

### Code Quality Standards
<!-- This is where you define your coding standards for the AI to follow -->
Shell script with strict mode and clean shutdown.

---

## 13. Second-Order Impact Analysis

### Impact Assessment
<!-- This is where you think through broader consequences of your changes -->
Low risk. Only dev workflow convenience.

---

**🎯 Ready to Plan Your Next Project?**

This template gives you the framework - now fill it out with your specific project details!

*Want the complete version with detailed examples, advanced strategies, and full AI agent workflows? [Watch the full tutorial video here]*

---

*This template is part of ShipKit - AI-powered development workflows and templates*  
*Get the complete toolkit at: https://shipkit.ai* 
