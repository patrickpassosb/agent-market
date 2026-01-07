# Task 6: Docker Containerization

## 1. Task Overview

### Task Title
**Title:** Docker Containerization for Reproducibility

### Goal Statement
**Goal:** Implement a `Dockerfile` and `docker-compose.yml` to ensure the simulation can be reliably reproduced and executed in a consistent environment, satisfying the "Minimum Expected Submission" criteria.

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

---

## 9. Implementation Plan

- Step 1: Create `Dockerfile` optimized for Python/uv.
- Step 2: Create `docker-compose.yml` for simplified orchestration.
- Step 3: Validate the containerized run.

## 12. AI Agent Instructions

### Implementation Workflow
1.  **Dockerfile**: Use `python:3.12-slim`. Install `uv`. Copy `pyproject.toml` and `uv.lock`. usage `uv sync`.
2.  **Docker Compose**: Define service `agent-market`. Mount current directory to `/app`. Load `.env`.
3.  **Validation**: Ensure `docker-compose up` starts the generic Rich dashboard.
