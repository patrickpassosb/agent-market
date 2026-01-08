# AI Task Planning Template - Starter Framework

> **About This Template:** This is a systematic framework for planning and executing technical projects with AI assistance. Use this structure to break down complex features, improvements, or fixes into manageable, trackable tasks that AI agents can execute effectively.

---

## 1. Task Overview

### Task Title
<!-- Give your task a clear, specific name that describes what you're building or fixing -->
**Title:** Build Next.js Bloomberg-Style Dashboard Frontend

### Goal Statement
<!-- Write one paragraph explaining what you want to achieve and why it matters for your project -->
**Goal:** Stand up a Next.js 14 + Tailwind + lightweight-charts frontend in `frontend/` that renders a real-time market dashboard with WebSocket updates and a dark glassmorphism aesthetic, aligning with the backend API contract.

---

## 2. Project Analysis & Current State

### Technology & Architecture
<!-- This is where you document your current tech stack so the AI understands your environment -->
- **Frameworks & Versions:** Next.js 14 (new), Tailwind CSS (new), lightweight-charts (new)
- **Language:** TypeScript (frontend)
- **Database & ORM:** N/A (frontend)
- **UI & Styling:** Tailwind CSS, custom UI components
- **Authentication:** None
- **Key Architectural Patterns:** App Router, component-driven UI, client-side WebSocket data flow

### Current State
<!-- Describe what exists today - what's working, what's broken, what's missing -->
Backend exists separately. No frontend in this repo yet. Need to initialize and build dashboard UI + WebSocket integration.

## 3. Context & Problem Definition

### Problem Statement
<!-- This is where you clearly define the specific problem you're solving -->
There is no frontend UI to visualize the market simulation in real time. Users need a Bloomberg-terminal-style dashboard with live ticker updates, charts, and an agent activity feed that consumes the backend WebSocket and REST endpoints.

### Success Criteria
<!-- Define exactly how you'll know when this task is complete and successful -->
- [x] `frontend/` Next.js 14 project scaffolding created with Tailwind configured
- [x] Market Watch, Real-time Chart, and Agent Feed components render in a single dashboard page
- [x] WebSocket at `ws://localhost:8000/ws` updates tickers and chart data
- [x] UI uses dark glassmorphism aesthetic and is responsive

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
- Must use Next.js 14 App Router
- Must use Tailwind CSS
- Must use lightweight-charts for the chart
- Must match backend message shape: `{ "type": "ticker", "data": { "AAPL": 0.005 } }`

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
Frontend uses WebSocket for live updates and REST for initial state and agent list.

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
- MarketWatch
- RealtimeChart
- AgentFeed
- Layout shell / dashboard page

### Page Updates
<!-- This is where you list pages that need modifications -->
- `frontend/app/page.tsx` for dashboard layout

### State Management
<!-- This is where you plan how data flows through your frontend -->
Local component state with hooks; shared WebSocket state via context or lifted state in page.

---

## 9. Implementation Plan

1. Scaffold Next.js 14 app in `frontend/` with Tailwind and TypeScript.
2. Add shared UI shell with glassmorphism theme and layout.
3. Implement MarketWatch component and state wiring.
4. Implement RealtimeChart with lightweight-charts and WebSocket stream.
5. Implement AgentFeed with placeholder fetch (REST) and data types.
6. Wire WebSocket and initial data fetch; ensure responsive design.

---

## 10. Task Completion Tracking

### Real-Time Progress Tracking
<!-- This is where you tell the AI agent to update progress as work is completed -->
Track progress by updating this task checklist as each phase completes.

---

## 11. File Structure & Organization

- `frontend/` (new Next.js app)
- `frontend/app/page.tsx`
- `frontend/components/MarketWatch.tsx`
- `frontend/components/RealtimeChart.tsx`
- `frontend/components/AgentFeed.tsx`
- `frontend/styles/globals.css` or Tailwind base styles

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
Low risk; new frontend only. Ensure WebSocket reconnect logic does not overload backend.

---

**🎯 Ready to Plan Your Next Project?**

This template gives you the framework - now fill it out with your specific project details!

*Want the complete version with detailed examples, advanced strategies, and full AI agent workflows? [Watch the full tutorial video here]*

---

*This template is part of ShipKit - AI-powered development workflows and templates*  
*Get the complete toolkit at: https://shipkit.ai* 
