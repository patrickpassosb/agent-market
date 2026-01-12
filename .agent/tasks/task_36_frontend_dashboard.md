# AI Task Planning Template - Starter Framework

> **About This Template:** This is a systematic framework for planning and executing technical projects with AI assistance. Use this structure to break down complex features, improvements, or fixes into manageable, trackable tasks that AI agents can execute effectively.

---

## 1. Task Overview

### Task Title
<!-- Give your task a clear, specific name that describes what you're building or fixing -->
**Title:** Improve Agent Roster Realtime Metrics + Persona Visibility

### Goal Statement
<!-- Write one paragraph explaining what you want to achieve and why it matters for your project -->
**Goal:** Ensure agent total value and ROI update in real time and make agent personas clearly readable in the roster UI, while keeping the existing dashboard aesthetic and API contract.

---

## 2. Project Analysis & Current State

### Technology & Architecture
<!-- This is where you document your current tech stack so the AI understands your environment -->
- **Frameworks & Versions:** Next.js 16, Tailwind CSS, lightweight-charts
- **Language:** TypeScript (frontend)
- **Database & ORM:** N/A (frontend)
- **UI & Styling:** Tailwind CSS, custom UI components
- **Authentication:** None
- **Key Architectural Patterns:** App Router, component-driven UI, client-side WebSocket data flow

### Current State
<!-- Describe what exists today - what's working, what's broken, what's missing -->
Frontend already exists with WebSocket market updates. Agent roster metrics are only refreshed on initial fetch, and persona text is truncated in cards.

## 3. Context & Problem Definition

### Problem Statement
<!-- This is where you clearly define the specific problem you're solving -->
Agent total value/ROI remains static after initial load, and persona text is truncated to a single line, making it hard to read. Users need real-time metric updates and clearer persona visibility.

### Success Criteria
<!-- Define exactly how you'll know when this task is complete and successful -->
- [x] Agent total value and ROI update in real time (WebSocket or polling).
- [x] Persona text is readable without truncation blocking key info.
- [x] UI remains aligned with the existing glassmorphism aesthetic.

---

## 4. Development Mode Context

### Development Mode Context
<!-- This is where you tell the AI agent about your project's constraints and priorities -->
- **🚨 Project Stage:** New development
- **Breaking Changes:** Acceptable (no existing frontend)
- **Data Handling:** No persistence required on the frontend
- **User Base:** Internal demo and development users
- **Priority:** Visual polish + real-time UX, acceptable to iterate

---

## 5. Technical Requirements

### Functional Requirements
<!-- This is where the AI will understand exactly what the system should do - be specific about user actions and system behaviors -->
- User can view market tickers (AAPL, TSLA, NVDA, MSFT) with latest values
- System automatically connects to WebSocket and applies updates to UI
- User can view a real-time chart that updates as messages arrive
- User can view a list of recent agent actions/logs

### Non-Functional Requirements
<!-- This is where you define performance, security, and usability standards -->
- **Performance:** Smooth updates; avoid blocking UI
- **Security:** No auth required in MVP
- **Usability:** Clear, terminal-inspired layout with readable typography
- **Responsive Design:** Works on mobile and desktop
- **Theme Support:** Dark mode only, glassmorphism aesthetic

### Technical Constraints
<!-- This is where you list limitations the AI agent must work within -->
- Must use current Next.js App Router setup
- Must use Tailwind CSS
- Must use lightweight-charts for the chart
- Must preserve existing ticker message shape; can extend with agent roster payloads.

---

## 6. Data & Database Changes

### Database Schema Changes
<!-- This is where you specify any database modifications needed -->
None.

### Data Model Updates
<!-- This is where you define TypeScript types, schema updates, or data structure changes -->
Frontend types for ticker updates, chart points, and agent activity records.

### Data Migration Plan
<!-- This is where you plan how to handle existing data during changes -->
None.

---

## 7. API & Backend Changes

### Data Access Pattern Rules
<!-- This is where you tell the AI agent how to structure backend code in your project -->
Frontend uses WebSocket for live updates and REST for initial state and agent list; may extend WS payload to include agent metrics.

### Server Actions
<!-- List the backend mutation operations you need -->
None.

### Database Queries
<!-- Specify how you'll fetch data -->
- REST: `GET /market/state`
- REST: `GET /agents`
- WS: `ws://localhost:8000/ws`

---

## 8. Frontend Changes

### New Components
<!-- This is where you specify UI components to be created -->
- AgentRoster persona display (improve readability)
- Dashboard WebSocket handling for live agent metrics

### Page Updates
<!-- This is where you list pages that need modifications -->
- `frontend/components/AgentRoster.tsx`
- `frontend/components/Dashboard.tsx`
- `src/api/server.py` (optional: include agent roster in WS payload)

### State Management
<!-- This is where you plan how data flows through your frontend -->
Local component state with hooks; update agent roster on WS tick events or controlled polling.

---

## 9. Implementation Plan

1. Update backend WS payload or add frontend polling for agent roster metrics.
2. Wire `Dashboard` to refresh agent metrics in real time.
3. Improve persona visibility in `AgentRoster` (expandable or multi-line).
4. Validate UI still fits within existing layout constraints.

---

## 10. Task Completion Tracking

### Real-Time Progress Tracking
<!-- This is where you tell the AI agent to update progress as work is completed -->
- [x] Include live agent snapshot data in WebSocket ticker payloads.
- [x] Consume WebSocket agent updates in `Dashboard`.
- [x] Improve persona readability with expandable details in `AgentRoster`.
- [x] Remove persona toggle UI and render full persona text inline.
- [x] Normalize agent card spacing and align total-value/footer blocks.

---

## 11. File Structure & Organization

- `frontend/components/AgentRoster.tsx`
- `frontend/components/Dashboard.tsx`
- `src/api/server.py`

---

## 12. AI Agent Instructions

### Implementation Workflow
<!-- This is where you give specific instructions to your AI agent -->
🎯 **MANDATORY PROCESS:**
- Use Context7 before any library or CLI usage
- Follow plan steps and update progress
- Keep changes minimal and aligned with success criteria

### Communication Preferences
<!-- This is where you set expectations for how the AI should communicate -->
Concise updates with file paths and next steps.

### Code Quality Standards
<!-- This is where you define your coding standards for the AI to follow -->
Type-safe components, minimal abstractions, Tailwind for styling.

---

## 13. Second-Order Impact Analysis

### Impact Assessment
<!-- This is where you think through broader consequences of your changes -->
Ensure added agent updates do not overload the WebSocket or UI rendering.

---

**🎯 Ready to Plan Your Next Project?**

This template gives you the framework - now fill it out with your specific project details!

*Want the complete version with detailed examples, advanced strategies, and full AI agent workflows? [Watch the full tutorial video here]*

---

*This template is part of ShipKit - AI-powered development workflows and templates*  
*Get the complete toolkit at: https://shipkit.ai* 
