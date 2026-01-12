# AI Task Planning Template - Starter Framework

> **About This Template:** This is a systematic framework for planning and executing technical projects with AI assistance. Use this structure to break down complex features, improvements, or fixes into manageable, trackable tasks that AI agents can execute effectively.

---

## 1. Task Overview

### Task Title
<!-- Give your task a clear, specific name that describes what you're building or fixing -->
**Title:** Explain CI error and outline merge-to-main steps

### Goal Statement
<!-- Write one paragraph explaining what you want to achieve and why it matters for your project -->
**Goal:** Explain the CI failure/skip behavior, fix the failing test caused by runner randomness changes, and provide safe Git steps to merge into `main`.

---

## 2. Project Analysis & Current State

### Technology & Architecture
<!-- This is where you document your current tech stack so the AI understands your environment -->
- **Frameworks & Versions:** GitHub Actions (`.github/workflows/ci.yml`), uv, Ruff, Bandit, Docker Buildx
- **Language:** Python 3.12
- **Database & ORM:** N/A (CI workflow analysis only)
- **UI & Styling:** N/A
- **Authentication:** GitHub Actions `GITHUB_TOKEN` permissions (read)
- **Key Architectural Patterns:** CI pipeline with job dependencies via `needs`

### Current State
<!-- Describe what exists today - what's working, what's broken, what's missing -->
Lint job (`lint-and-audit`) failed due to Ruff violations, causing downstream jobs to be skipped. `docker-verify` runs independently and completed. `deploy-production` is also gated on push events and `needs`. CI now fails in `tests/test_runner.py` due to mocking `random` after switching to `secrets`-based helpers.

## 3. Context & Problem Definition

### Problem Statement
<!-- This is where you clearly define the specific problem you're solving -->
The Actions UI shows skipped jobs, and the user needs to know which dependency or condition caused the skip so they can focus on the root failure.

### Success Criteria
<!-- Define exactly how you'll know when this task is complete and successful -->
- [ ] Identify which jobs are gated by `needs` and explain the dependency chain.
- [ ] Explain why the failing lint job causes `test` (and `deploy`) to skip.
- [ ] Call out any additional conditional (`if`) that prevents deploy on PRs.
- [ ] Provide documented Git commands to update `main` and merge the current branch.
- [ ] Fix `tests/test_runner.py` to align with secure-random helpers in `SimulationRunner`.

---

## 4. Development Mode Context

### Development Mode Context
<!-- This is where you tell the AI agent about your project's constraints and priorities -->
- **🚨 Project Stage:** Active CI troubleshooting
- **Breaking Changes:** Not applicable (explanation-only)
- **Data Handling:** No data changes
- **User Base:** Contributors reviewing CI results
- **Priority:** Clarity and accuracy

---

## 5. Technical Requirements

### Functional Requirements
<!-- This is where the AI will understand exactly what the system should do - be specific about user actions and system behaviors -->

- System explains job skip behavior based on workflow `needs` and `if` conditions.
- When linting fails, downstream dependent jobs are skipped unless overridden.
- Provide merge steps using documented Git commands (`git fetch`, `git checkout`, `git pull`, `git merge`).

### Non-Functional Requirements
<!-- This is where you define performance, security, and usability standards -->
- **Performance:** N/A
- **Security:** N/A
- **Usability:** Clear, concise explanation
- **Responsive Design:** N/A
- **Theme Support:** N/A

### Technical Constraints
<!-- This is where you list limitations the AI agent must work within -->
- [Use existing workflow config; no changes required unless requested]

---

## 6. Data & Database Changes

### Database Schema Changes
<!-- This is where you specify any database modifications needed -->

N/A

### Data Model Updates
<!-- This is where you define TypeScript types, schema updates, or data structure changes -->

N/A

### Data Migration Plan
<!-- This is where you plan how to handle existing data during changes -->

N/A

---

## 7. API & Backend Changes

### Data Access Pattern Rules
<!-- This is where you tell the AI agent how to structure backend code in your project -->

N/A

### Server Actions
<!-- List the backend mutation operations you need -->

N/A

### Database Queries
<!-- Specify how you'll fetch data -->

N/A

---

## 8. Frontend Changes

### New Components
<!-- This is where you specify UI components to be created -->

N/A

### Page Updates
<!-- This is where you list pages that need modifications -->

N/A

### State Management
<!-- This is where you plan how data flows through your frontend -->

N/A

---

## 9. Implementation Plan

1. Explain CI skip behavior based on `.github/workflows/ci.yml`.
2. Provide merge-to-main steps and note detached HEAD/branch checks.

---

## 10. Task Completion Tracking

### Real-Time Progress Tracking
<!-- This is where you tell the AI agent to update progress as work is completed -->

- Track completion by checking off success criteria after explanation and command list are delivered.

---

## 11. File Structure & Organization

No files created or modified.

---

## 12. AI Agent Instructions

### Implementation Workflow
<!-- This is where you give specific instructions to your AI agent -->
🎯 **MANDATORY PROCESS:**
- Use Context7 docs for Git and GitHub Actions references.
- Do not run destructive Git commands.

### Communication Preferences
<!-- This is where you set expectations for how the AI should communicate -->
Concise, step-by-step guidance; ask before running any commands.

### Code Quality Standards
<!-- This is where you define your coding standards for the AI to follow -->
N/A

---

## 13. Second-Order Impact Analysis

### Impact Assessment
<!-- This is where you think through broader consequences of your changes -->

N/A (explanation and git guidance only).

---

**🎯 Ready to Plan Your Next Project?**

This template gives you the framework - now fill it out with your specific project details! 

*Want the complete version with detailed examples, advanced strategies, and full AI agent workflows? [Watch the full tutorial video here]*

---

*This template is part of ShipKit - AI-powered development workflows and templates*  
*Get the complete toolkit at: https://shipkit.ai* 
