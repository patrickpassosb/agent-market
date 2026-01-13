# Task 7: Docker Containerization

## 1. Task Overview

### Task Title
**Title:** Docker Compose Dev UI Enablement

### Goal Statement
**Goal:** Extend the development Compose stack to run the web UI (Next.js) alongside the backend so reviewers can use the dashboard locally.

---

## 2. Project Analysis & Current State

### Technology & Architecture
- **Language:** Python 3.12+
- **Dependency Manager:** uv
- **Containerization:** Docker, Docker Compose

### Current State
- `Dockerfile` created (using python:3.12-slim and uv).
- `docker-compose.yml` created.
- `.dockerignore` configured.
- Project core logic (`main.py`) is functional.

## 3. Context & Problem Definition

### Problem Statement
The project needs a reproducible environment for evaluators. Manual dependency installation is error-prone. We need a standardized container setup.

### Success Criteria
- [x] `Dockerfile` builds successfully.
- [x] `docker-compose up` runs the `main.py` script.
- [x] `.env` variables are correctly loaded in the container.
- [x] Local changes are reflected in the container (via volumes).
- [ ] `docker-compose up` also starts the Next.js dev server and exposes the UI on port 3000.

---

## 9. Implementation Plan

- Step 1: Update `docker-compose.yml` to add backend + frontend dev services.
- Step 2: Ensure env vars for UI API/Ws URLs are wired.
- Step 3: Validate `docker-compose up` exposes the UI on port 3000 and backend on port 8000.

## 12. AI Agent Instructions

### Implementation Workflow
1.  **Dockerfile**: Use `python:3.12-slim`. Install `uv`. Copy `pyproject.toml` and `uv.lock`. usage `uv sync`.
2.  **Docker Compose**: Define service `agent-market`. Mount current directory to `/app`. Load `.env`.
3.  **Validation**: Ensure `docker-compose up` starts the generic Rich dashboard.
