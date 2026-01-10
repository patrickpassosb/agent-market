# AI Task Planning Template - Security Audit

## 1. Task Overview

### Task Title
**Title:** Comprehensive Security Audit & Hardening

### Goal Statement
**Goal:** Identify and rectify potential security vulnerabilities within the Agent Market simulation project, including SQL injection, XSS, exposed secrets, and logic-level security flaws, ensuring a robust and secure trading environment.

---

## 2. Project Analysis & Current State

### Technology & Architecture
- **Frameworks & Versions:** Python 3.12, FastAPI, SQLModel (SQLAlchemy), LiteLLM, React (Next.js), Tailwind CSS.
- **Language:** Python, TypeScript.
- **Database & ORM:** SQLite, SQLModel.
- **UI & Styling:** React, Tailwind CSS.
- **Authentication:** None (Currently a single-user local simulation).
- **Key Architectural Patterns:** REST API, WebSockets, Multi-Agent System.

### Current State
The project is a locally running simulation. While not yet exposed to the open internet, it lacks basic security hardening. The database layer uses SQLModel, which generally protects against SQL injection, but raw queries or unsafe usage must be audited. Secrets are primarily managed via `.env`, but hardcoded keys might exist. Frontend components might render user/agent-generated content (like headlines) without escaping.

## 3. Context & Problem Definition

### Problem Statement
As the project evolves from a prototype to a more complex system, security becomes a primary concern. Potential risks include:
- Compromise of LLM API keys.
- Database corruption or data theft via SQL injection.
- Session hijacking or UI defacement via XSS in the dashboard.
- Simulation manipulation via unvalidated API inputs.

### Success Criteria
- [ ] No hardcoded API keys or secrets in the repository.
- [ ] Database interactions audited and verified to use parameter binding (SQLModel/SQLAlchemy best practices).
- [ ] Frontend rendering verified to escape/sanitize dynamic content (agent headlines, reasoning, etc.).
- [ ] API endpoints have strict Pydantic model validation for all inputs.
- [ ] Basic security headers added to the FastAPI application.

---

## 4. Development Mode Context
- **🚨 Project Stage:** Prototype/Growth
- **Breaking Changes:** Acceptable if necessary for security.
- **Data Handling:** Preserve simulation history.
- **User Base:** Internal/Developer focused.
- **Priority:** Stability & Security.

---

## 5. Technical Requirements

### Functional Requirements
- System must protect LLM API keys.
- System must prevent unauthorized database modifications.
- System must safely render agent-generated narrative strings.

### Non-Functional Requirements
- **Security:** Strict input validation, secret management, content sanitization.
- **Code Quality:** Adherence to OWASP Top 10 principles where applicable.

---

## 6. Implementation Plan

### Phase 1: Secrets & Configuration Audit
- [ ] Search entire codebase for high-entropy strings or hardcoded API keys.
- [ ] Verify `.env` is correctly gitignored.
- [ ] Ensure `litellm` and other providers exclusively use environment variables.

### Phase 2: Database Layer Audit (SQL Injection)
- [ ] Review `src/market/ledger.py` and other files using `Session` or raw `sqlite3`.
- [ ] Verify all queries use parameter binding or SQLModel expression language.

### Phase 3: Input Validation & API Hardening
- [ ] Review all FastAPI routes in `src/api/server.py`.
- [ ] Ensure all body inputs and query parameters are typed and validated via Pydantic models.
- [ ] Add basic security middleware (e.g., trusted hosts, CORS restrictions).

### Phase 4: Frontend Audit (XSS)
- [ ] Review how `AgentRoster`, `SentimentFeed`, and `MarketPulse` render dynamic text.
- [ ] Verify common React escaping is sufficient or if manual sanitization is needed for rich/agent-generated text.

### Phase 5: Verification & Reporting
- [ ] Run security linters (e.g., `bandit` for Python).
- [ ] Document found issues and their resolutions.

---

## 10. Task Completion Tracking
- [ ] Phase 1: Secrets Audit
- [ ] Phase 2: DB Audit
- [ ] Phase 3: API Hardening
- [ ] Phase 4: Frontend Audit
- [ ] Phase 5: Verification

---

## 12. AI Agent Instructions

### Implementation Workflow
- Conduct a search-first audit before making changes.
- Use `bandit` or similar tools if available.
- Prioritize fixes that have zero impact on simulation logic.

### Code Quality Standards
- No raw string formatting for SQL queries.
- Consistent use of Pydantic for validation.
- Clear separation of sensitive configuration.
