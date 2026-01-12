# AI Task Planning Template - Starter Framework

> **About This Template:** This is a systematic framework for planning and executing technical projects with AI assistance. Use this structure to break down complex features, improvements, or fixes into manageable, trackable tasks that AI agents can execute effectively.

---

## 1. Task Overview

### Task Title
<!-- Give your task a clear, specific name that describes what you're building or fixing -->
**Title:** Replace Real-Time Chart Panel with Terminal Feed

### Goal Statement
<!-- Write one paragraph explaining what you want to achieve and why it matters for your project -->
**Goal:** Swap the non-functional real-time chart with a terminal-style live feed that shows incoming WebSocket updates so the dashboard remains informative even when chart rendering fails.

---

## 2. Project Analysis & Current State

### Technology & Architecture
<!-- This is where you document your current tech stack so the AI understands your environment -->
- **Frameworks & Versions:** Next.js (React)
- **Language:** TypeScript
- **UI & Styling:** Tailwind CSS
- **Key Architectural Patterns:** Client component dashboard with WebSocket updates

### Current State
<!-- Describe what exists today - what's working, what's broken, what's missing -->
`frontend/components/RealtimeChart.tsx` is rendered in the dashboard but shows an empty panel. The WebSocket data arrives and updates market cards, but the chart area does not provide visible feedback.

## 3. Context & Problem Definition

### Problem Statement
<!-- This is where you clearly define the specific problem you're solving -->
The chart panel does not show useful data, leaving a large blank area. A terminal-style feed is more reliable and better conveys live activity.

### Success Criteria
<!-- Define exactly how you'll know when this task is complete and successful -->
- [x] Replace the chart panel with a terminal-style feed component.
- [x] Terminal feed appends new lines on WebSocket ticker messages.
- [x] Terminal feed keeps a bounded history for performance.
- [x] Add Context7 citation comment for React hook usage.

---

## 4. Development Mode Context

### Development Mode Context
<!-- This is where you tell the AI agent about your project's constraints and priorities -->
- **🚨 Project Stage:** New development
- **Breaking Changes:** Avoid
- **Data Handling:** No data changes
- **User Base:** Internal demo/dev
- **Priority:** Clear live feedback in UI

---

## 5. Technical Requirements

### Functional Requirements
<!-- This is where the AI will understand exactly what the system should do - be specific about user actions and system behaviors -->
- Terminal panel shows timestamped updates from WebSocket data.
- Panel remains scrollable and readable.

### Non-Functional Requirements
<!-- This is where you define performance, security, and usability standards -->
- **Performance:** Keep log buffer small.
- **Security:** No changes.
- **Usability:** Always show something even if chart fails.
- **Responsive Design:** Must remain legible on mobile.
- **Theme Support:** Match existing dashboard styling.

### Technical Constraints
<!-- This is where you list limitations the AI agent must work within -->
- Avoid new dependencies.
- Use existing WebSocket data flow.

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
- Terminal feed component for live updates.

### Page Updates
<!-- This is where you list pages that need modifications -->
- Replace `RealtimeChart` usage in `Dashboard`.

### State Management
<!-- This is where you plan how data flows through your frontend -->
- Keep local log buffer in dashboard state.

---

## 9. Implementation Plan

1. Add terminal feed component and styles.
2. Store and append ticker updates to a log buffer.
3. Swap chart panel with terminal feed.
4. Update checklist.

---

## 10. Task Completion Tracking

### Real-Time Progress Tracking
<!-- This is where you tell the AI agent to update progress as work is completed -->
Update the checklist when complete.

---

## 11. File Structure & Organization

- `frontend/components/Dashboard.tsx`
- `frontend/components/TerminalFeed.tsx`

---

## 12. AI Agent Instructions

### Implementation Workflow
<!-- This is where you give specific instructions to your AI agent -->
🎯 **MANDATORY PROCESS:**
- Use Context7 for React hook usage
- Add Context7 citation in code comments
- Keep changes minimal

### Communication Preferences
<!-- This is where you set expectations for how the AI should communicate -->
Concise updates with file paths.

### Code Quality Standards
<!-- This is where you define your coding standards for the AI to follow -->
Readable, minimal changes

---

## 13. Second-Order Impact Analysis

### Impact Assessment
<!-- This is where you think through broader consequences of your changes -->
Removes chart visualization in favor of textual updates; no backend impact.

---

**🎯 Ready to Plan Your Next Project?**

This template gives you the framework - now fill it out with your specific project details!

*Want the complete version with detailed examples, advanced strategies, and full AI agent workflows? [Watch the full tutorial video here]*

---

*This template is part of ShipKit - AI-powered development workflows and templates*  
*Get the complete toolkit at: https://shipkit.ai* 
