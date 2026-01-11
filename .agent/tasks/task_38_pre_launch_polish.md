# AI Task Planning Template - Pre-Launch Polish & Scale

## 1. Task Overview

### Task Title
**Title:** Pre-Launch Polish & Intelligent Scaling

### Goal Statement
**Goal:** Finalize the application for production by implementing "Smart Asset Selection" for agents (replacing random behavior), adding a rigorous "Pre-Deployment Flight Check" script, and polishing the deployment documentation.

---

## 2. Project Analysis & Current State

### Current State
- **Frontend:** Premium dashboard is code-complete with connection indicators.
- **Backend:** Rate limiting and multiple models are implemented.
- **Agent Logic:** Currently uses `random.choice(SUPPORTED_ASSETS)` to pick what to trade, which reduces simulation realism.
- **Deployment:** User reported deployment failures. No automated check exists to verify environment configuration before build.

## 3. Context & Problem Definition

### Problem Statement
1. **Dumb Agents:** Agents randomly pick assets, ignoring market trends or news.
2. **Fragile Deployment:** Missing API keys or config errors cause Docker builds to fail or runtime crashes.

### Success Criteria
- [x] **Smart Agents:** `Trader.act` selects assets based on volatility or recent news headlines.
- [x] **Flight Check:** `scripts/pre_deploy_check.sh` validates `.env`, keys, and Docker status.
- [x] **Docs:** `README.md` updated with a "Production Deployment" guide.

---

## 4. Implementation Plan

### Phase 1: Smart Agent Logic
1. Modify `Trader.act` in `src/agents/trader.py`. (Completed in `main.py` loop)
2. Inject `market_metrics` (volatility) into the decision process.
3. Logic: 70% chance to pick high-volatility asset, 30% random (for exploration).

### Phase 2: Deployment Safety
1. Create `scripts/pre_deploy_check.sh`.
2. Check for: `API_KEY`, `GEMINI_API_KEY` (or others), `ENV=production`.
3. Verify Docker daemon is running.

### Phase 3: Final Polish
1. Run the flight check. (Passed)
2. Verify the simulation locally with the new smart logic.