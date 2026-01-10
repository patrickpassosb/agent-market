# AI Task Planning Template - Scaling & Intelligence

## 1. Task Overview

### Task Title
**Title:** High-Scale Agent Intelligence & Rate Limiting

### Goal Statement
**Goal:** Scale the simulation to 20 robust agents by integrating high-throughput free APIs (Cerebras/Gemini) and implementing a centralized Rate Limiter to prevent API failures (429 errors).

---

## 2. Project Analysis & Current State

### Technology & Architecture
- **Frameworks:** LiteLLM (for provider routing), Asyncio (for concurrency).
- **Providers:** Currently using Groq/Gemini/Ollama.
- **Agent Count:** Targeted 20 agents.

### Current State
Simulation supports async execution, but adding more agents increases the risk of hitting rate limits on free API tiers. No centralized mechanism exists to throttle LLM requests across all agents.

## 3. Context & Problem Definition

### Problem Statement
1. **API Fragility:** With 20 agents acting every few seconds, free-tier rate limits (RPM/TPM) will be exceeded frequently.
2. **Provider Concentration:** Relying on one or two providers limits the "free compute" pool.
3. **Hardware Constraints:** Local execution of LLMs is not feasible for 20 agents on limited hardware.

### Success Criteria
- [ ] Centralized `AsyncRateLimiter` implemented in `src/utils/concurrency.py`.
- [ ] Integration of **Cerebras** and **Gemini 1.5 Flash** (high-throughput providers) in `src/utils/personas.py`.
- [ ] Simulation successfully runs 20 agents without a single `429 Too Many Requests` error.
- [ ] Latency is managed via a priority queue (Journalist > Trader).

---

## 4. Development Mode Context
- **Priority:** Critical for Scaling.
- **Breaking Changes:** Minor (Updating agent router logic).

---

## 5. Technical Requirements

### Functional Requirements
- Throttle LLM calls to a configurable `MAX_RPM` (Requests Per Minute).
- Rotate between 3+ high-throughput providers to maximize free-tier capacity.

---

## 6. Implementation Plan

### Phase 1: Concurrency Utilities
1. Create `src/utils/concurrency.py` with an `AsyncRateLimiter` class using `asyncio.Semaphore` and time-window tracking.

### Phase 2: Intelligence Expansion
1. Update `src/utils/personas.py` to add **Cerebras** as a primary high-speed provider.
2. Refine the tier system to use Gemini 1.5 Flash for "Analytical" tasks (Journalist) and Cerebras/Groq for "Fast" tasks (Traders).

### Phase 3: Integration
1. Update `Trader.act` and `JournalistAgent.analyze` to wrap LLM calls with the `RateLimiter`.
2. Update `src/api/server.py` to spawn 20 agents by default.

---

## 7. Verification Methods
1. Run simulation with `num_agents=20`.
2. Monitor logs for `Rate Limit Exceeded` warnings or errors.
3. Verify that all 20 agents are successfully logging actions in the dashboard.

---

## 8. AI Agent Instructions
- Use Context7 to check Cerebras and Gemini 1.5 Flash integration details in `litellm`.
- Ensure the Rate Limiter is asynchronous and non-blocking.
