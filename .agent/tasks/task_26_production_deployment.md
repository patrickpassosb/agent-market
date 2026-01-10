# AI Task Planning Template - Production Deployment

## 1. Task Overview

### Task Title
**Title:** Production Deployment on AWS EC2

### Goal Statement
**Goal:** Deploy the full-stack application (FastAPI + Next.js) to an AWS EC2 instance using Docker Compose to ensure a 24/7 autonomous simulation that is reproducible in the cloud.

---

## 2. Project Analysis & Current State

### Technology & Architecture
- **Infrastructure:** AWS EC2 (Free Tier t2.micro).
- **Orchestration:** Docker Compose.
- **Frontend:** Next.js (Static Export or Containerized).
- **Backend:** FastAPI + SQLite.

### Current State
Project runs locally via `docker-compose` and shell scripts. Environment variables are managed via `.env`.

## 3. Context & Problem Definition

### Problem Statement
1. Local execution is not persistent.
2. Evaluators need a live demo link or a simple one-command deployment path to verify "reproducibility" as per challenge requirements.

### Success Criteria
- [ ] `docker-compose.prod.yml` created with restart policies.
- [ ] Nginx configuration added to route `/api` and `/` traffic on Port 80.
- [ ] Automated deployment script `scripts/deploy.sh` created.
- [ ] README updated with "Live Demo" and AWS setup instructions.

---

## 4. Implementation Plan

### Phase 1: Docker Optimization
1. Create `docker-compose.prod.yml` with `restart: always`.
2. Ensure `market.db` and `chroma_db` use named volumes for persistence on EC2.

### Phase 2: Web Server (Nginx)
1. Create `nginx.conf` to serve as a reverse proxy for the Next.js frontend and FastAPI backend.

### Phase 3: CI/CD & Scripts
1. Create `scripts/setup_ec2.sh` to install Docker/Git on a fresh Ubuntu instance.
2. Create `scripts/deploy.sh` for one-click updates.

---

## 5. Verification Methods
1. Verify app accessibility via EC2 Public IP.
2. Verify that stopping/starting containers preserves market trade history.
