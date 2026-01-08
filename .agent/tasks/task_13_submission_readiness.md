# AI Task Planning Template - Starter Framework

> **About This Template:** This is a systematic framework for planning and executing technical projects with AI assistance. Use this structure to break down complex features, improvements, or fixes into manageable, trackable tasks that AI agents can execute effectively.

---

## 1. Task Overview

### Task Title
<!-- Give your task a clear, specific name that describes what you're building or fixing -->
**Title:** Submission Readiness: Functional Simulation + README Overhaul

### Goal Statement
<!-- Write one paragraph explaining what you want to achieve and why it matters for your project -->
**Goal:** Make the simulation reliably functional and deliver a concise, submission-ready README aligned to global guidelines.

---

## 2. Project Analysis & Current State

### Technology & Architecture
<!-- This is where you document your current tech stack so the AI understands your environment -->
- **Frameworks & Versions:** Python 3.12, litellm, sqlmodel, chromadb, rich
- **Language:** Python
- **Database & ORM:** SQLite + SQLModel
- **UI & Styling:** Rich terminal UI
- **Authentication:** N/A
- **Key Architectural Patterns:** Facade engine, multi-agent loop, RAG memory

### Current State
<!-- Describe what exists today - what's working, what's broken, what's missing -->
Simulation runs but can produce zero trades; README is verbose and missing a clear demo/evidence flow.

## 3. Context & Problem Definition

### Problem Statement
<!-- This is where you clearly define the specific problem you're solving -->
The project needs a reliable trading flow and a clear README for evaluation and hiring readiness.

### Success Criteria
<!-- Define exactly how you'll know when this task is complete and successful -->
- [ ] Simulation produces trades in a standard run.
- [ ] README includes overview, architecture diagram, how to run, demo guide, and evidence paths.
- [ ] Documentation aligns with global guidelines and requirements.

---

## 4. Development Mode Context

### Development Mode Context
<!-- This is where you tell the AI agent about your project's constraints and priorities -->
- **🚨 Project Stage:** TODO: Define if this is new development, production system, or legacy migration
- **Breaking Changes:** TODO: Specify if breaking changes are acceptable or must be avoided
- **Data Handling:** TODO: Define data preservation requirements
- **User Base:** TODO: Describe who will be affected by changes
- **Priority:** TODO: Set your speed vs stability priorities

---

## 5. Technical Requirements

### Functional Requirements
<!-- This is where the AI will understand exactly what the system should do - be specific about user actions and system behaviors -->

Ensure the simulation executes trades and produces artifacts. Provide a clear README for evaluators.
- Example format: "User can [specific action]"
- Example format: "System automatically [specific behavior]" 
- Example format: "When [condition] occurs, then [system response]"

### Non-Functional Requirements
<!-- This is where you define performance, security, and usability standards -->
- **Performance:** N/A
- **Security:** N/A
- **Usability:** Clear run + demo instructions
- **Responsive Design:** N/A
- **Theme Support:** N/A

### Technical Constraints
<!-- This is where you list limitations the AI agent must work within -->
- [Must use existing system X]
- [Cannot modify database table Y]
- [Must maintain compatibility with feature Z]

---

## 6. Data & Database Changes

### Database Schema Changes
<!-- This is where you specify any database modifications needed -->

TODO: Add your SQL schema changes here (new tables, columns, indexes, etc.)

### Data Model Updates
<!-- This is where you define TypeScript types, schema updates, or data structure changes -->

TODO: Define your TypeScript types, interfaces, and data structure changes

### Data Migration Plan
<!-- This is where you plan how to handle existing data during changes -->

TODO: Plan your data migration steps (backup, apply changes, transform data, validate)

---

## 7. API & Backend Changes

### Data Access Pattern Rules
<!-- This is where you tell the AI agent how to structure backend code in your project -->

TODO: Define where different types of code should go in your project (mutations, queries, API routes)

### Server Actions
<!-- List the backend mutation operations you need -->

TODO: List your create, update, delete operations and what they do

### Database Queries
<!-- Specify how you'll fetch data -->

TODO: Define your data fetching approach (direct queries vs separate functions)

---

## 8. Frontend Changes

### New Components
<!-- This is where you specify UI components to be created -->

TODO: List the new components you need to create and their purpose

### Page Updates
<!-- This is where you list pages that need modifications -->

TODO: List the pages that need changes and what modifications are required

### State Management
<!-- This is where you plan how data flows through your frontend -->

TODO: Define your state management approach and data flow strategy

---

## 9. Implementation Plan

1) Improve market initialization and action price validation.\n2) Rewrite README with architecture diagram and demo guide.\n3) Verify run outputs.

---

## 10. Task Completion Tracking

### Real-Time Progress Tracking
<!-- This is where you tell the AI agent to update progress as work is completed -->

Checklist of fixes and README sections.

---

## 11. File Structure & Organization

Modify `main.py`, `src/market/engine.py`, `src/agents/trader.py`, and `README.md` as needed.

---

## 12. AI Agent Instructions

### Implementation Workflow
<!-- This is where you give specific instructions to your AI agent -->
🎯 **MANDATORY PROCESS:**
Use Context7 for any API usage; keep docs concise.

### Communication Preferences
<!-- This is where you set expectations for how the AI should communicate -->
TODO: How do you want the agent to communicate with you

### Code Quality Standards
<!-- This is where you define your coding standards for the AI to follow -->
TODO: Any specific code standards

---

## 13. Second-Order Impact Analysis

### Impact Assessment
<!-- This is where you think through broader consequences of your changes -->

TODO: Tell the AI what sections of code you're worried about breaking, performance concerns, and user workflow impacts

---

**🎯 Ready to Plan Your Next Project?**

This template gives you the framework - now fill it out with your specific project details! 

*Want the complete version with detailed examples, advanced strategies, and full AI agent workflows? [Watch the full tutorial video here]*

---

*This template is part of ShipKit - AI-powered development workflows and templates*  
*Get the complete toolkit at: https://shipkit.ai* 
