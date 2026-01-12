# AI Task Planning Template - Starter Framework

> **About This Template:** This is a systematic framework for planning and executing technical projects with AI assistance. Use this structure to break down complex features, improvements, or fixes into manageable, trackable tasks that AI agents can execute effectively.

---

## 1. Task Overview

### Task Title
<!-- Give your task a clear, specific name that describes what you're building or fixing -->
**Title:** Update Gemini Model Names for LiteLLM

### Goal Statement
<!-- Write one paragraph explaining what you want to achieve and why it matters for your project -->
**Goal:** Replace invalid Gemini model identifiers with valid ones from the account’s model list so LiteLLM calls succeed.

---

## 2. Project Analysis & Current State

### Technology & Architecture
<!-- This is where you document your current tech stack so the AI understands your environment -->
- **Frameworks & Versions:** LiteLLM, Gemini API
- **Language:** Python
- **Database & ORM:** N/A
- **UI & Styling:** N/A
- **Authentication:** GEMINI_API_KEY
- **Key Architectural Patterns:** Provider routing in `src/utils/personas.py`

### Current State
<!-- Describe what exists today - what's working, what's broken, what's missing -->
Gemini models are set to `gemini/gemini-1.5-flash`, which is not present in the account model list. This causes 404 errors at runtime.

## 3. Context & Problem Definition

### Problem Statement
<!-- This is where you clearly define the specific problem you're solving -->
Gemini API requests fail because the configured model name is not supported for the account, breaking agent and journalist generation.

### Success Criteria
<!-- Define exactly how you'll know when this task is complete and successful -->
- [x] Gemini model identifiers updated to valid values.
- [x] Journalist default model updated to match new Gemini model.
- [x] Code comments cite Context7 docs for LiteLLM Gemini model naming.

---

## 4. Development Mode Context

### Development Mode Context
<!-- This is where you tell the AI agent about your project's constraints and priorities -->
- **🚨 Project Stage:** New development
- **Breaking Changes:** Avoid
- **Data Handling:** No data changes
- **User Base:** Internal demo/dev
- **Priority:** Fix runtime errors quickly

---

## 5. Technical Requirements

### Functional Requirements
<!-- This is where the AI will understand exactly what the system should do - be specific about user actions and system behaviors -->
- Gemini model names use `gemini/` prefix per LiteLLM.
- Selected model names appear in the account model list.

### Non-Functional Requirements
<!-- This is where you define performance, security, and usability standards -->
- **Performance:** No change
- **Security:** No change
- **Usability:** No change
- **Responsive Design:** N/A
- **Theme Support:** N/A

### Technical Constraints
<!-- This is where you list limitations the AI agent must work within -->
- Modify only existing Gemini model strings.
- Keep provider routing logic intact.

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
No changes.

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

1. Update Gemini model mappings in `src/utils/personas.py`.
2. Update journalist default model in `src/agents/journalist.py`.
3. Mark success criteria complete.

---

## 10. Task Completion Tracking

### Real-Time Progress Tracking
<!-- This is where you tell the AI agent to update progress as work is completed -->
Update the checklist when the model names are fixed.

---

## 11. File Structure & Organization

- `src/utils/personas.py`
- `src/agents/journalist.py`

---

## 12. AI Agent Instructions

### Implementation Workflow
<!-- This is where you give specific instructions to your AI agent -->
🎯 **MANDATORY PROCESS:**
- Use Context7 for LiteLLM Gemini naming
- Add Context7 citation in code comments
- Keep changes minimal

### Communication Preferences
<!-- This is where you set expectations for how the AI should communicate -->
Concise updates with file paths.

### Code Quality Standards
<!-- This is where you define your coding standards for the AI to follow -->
Keep code readable and consistent with existing style.

---

## 13. Second-Order Impact Analysis

### Impact Assessment
<!-- This is where you think through broader consequences of your changes -->
Low risk; provider routing unchanged.

---

**🎯 Ready to Plan Your Next Project?**

This template gives you the framework - now fill it out with your specific project details!

*Want the complete version with detailed examples, advanced strategies, and full AI agent workflows? [Watch the full tutorial video here]*

---

*This template is part of ShipKit - AI-powered development workflows and templates*  
*Get the complete toolkit at: https://shipkit.ai* 
