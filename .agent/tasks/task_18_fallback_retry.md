# AI Task Planning Template - Starter Framework

> **About This Template:** This is a systematic framework for planning and executing technical projects with AI assistance. Use this structure to break down complex features, improvements, or fixes into manageable, trackable tasks that AI agents can execute effectively.

---

## 1. Task Overview

### Task Title
<!-- Give your task a clear, specific name that describes what you're building or fixing -->
**Title:** Add LLM Provider Fallback Retries

### Goal Statement
<!-- Write one paragraph explaining what you want to achieve and why it matters for your project -->
**Goal:** When an LLM call fails, retry with the next available model/provider from the routing list to reduce runtime failures.

---

## 2. Project Analysis & Current State

### Technology & Architecture
<!-- This is where you document your current tech stack so the AI understands your environment -->
- **Frameworks & Versions:** LiteLLM
- **Language:** Python
- **Database & ORM:** N/A
- **UI & Styling:** N/A
- **Authentication:** Provider API keys
- **Key Architectural Patterns:** Provider routing in `src/utils/personas.py`

### Current State
<!-- Describe what exists today - what's working, what's broken, what's missing -->
LLM calls are made once with a selected model. Failures (rate limit, bad request) do not retry or fallback.

## 3. Context & Problem Definition

### Problem Statement
<!-- This is where you clearly define the specific problem you're solving -->
Provider failures break the simulation loop. We need to retry with alternative providers/models.

### Success Criteria
<!-- Define exactly how you'll know when this task is complete and successful -->
- [x] Trader LLM calls retry with next model on failure.
- [x] Journalist LLM calls retry with next model on failure.
- [x] Fallback logic uses the same provider ordering rules.
- [x] Comments cite Context7 LiteLLM docs.

---

## 4. Development Mode Context

### Development Mode Context
<!-- This is where you tell the AI agent about your project's constraints and priorities -->
- **🚨 Project Stage:** New development
- **Breaking Changes:** Avoid
- **Data Handling:** No data changes
- **User Base:** Internal demo/dev
- **Priority:** Resilience to API failures

---

## 5. Technical Requirements

### Functional Requirements
<!-- This is where the AI will understand exactly what the system should do - be specific about user actions and system behaviors -->
- Try each candidate model until one succeeds.
- Preserve existing response parsing logic.

### Non-Functional Requirements
<!-- This is where you define performance, security, and usability standards -->
- **Performance:** Minimal overhead for retries
- **Security:** No changes
- **Usability:** Improved stability
- **Responsive Design:** N/A
- **Theme Support:** N/A

### Technical Constraints
<!-- This is where you list limitations the AI agent must work within -->
- Use existing `src/utils/personas.py` provider order
- No new dependencies

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

1. Expose candidate model list by tier from `src/utils/personas.py`.
2. Add retry loop in Trader and Journalist LLM calls.
3. Update success criteria.

---

## 10. Task Completion Tracking

### Real-Time Progress Tracking
<!-- This is where you tell the AI agent to update progress as work is completed -->
Update checklist when done.

---

## 11. File Structure & Organization

- `src/utils/personas.py`
- `src/agents/trader.py`
- `src/agents/journalist.py`

---

## 12. AI Agent Instructions

### Implementation Workflow
<!-- This is where you give specific instructions to your AI agent -->
🎯 **MANDATORY PROCESS:**
- Use Context7 for LiteLLM usage
- Keep changes minimal
- Update checklist

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
Slight increase in latency on failures; otherwise low risk.

---

**🎯 Ready to Plan Your Next Project?**

This template gives you the framework - now fill it out with your specific project details!

*Want the complete version with detailed examples, advanced strategies, and full AI agent workflows? [Watch the full tutorial video here]*

---

*This template is part of ShipKit - AI-powered development workflows and templates*  
*Get the complete toolkit at: https://shipkit.ai* 
