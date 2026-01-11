# AI Task Planning Template - Future Roadmap & Improvements

## 1. Task Overview

### Task Title
**Title:** Roadmap for Advanced Simulation Capabilities

### Goal Statement
**Goal:** Define a strategic roadmap for evolving the Agent Market simulation from a functional prototype into an advanced research platform. This plan focuses on increasing realism, agent autonomy, and system robustness through four key feature pillars.

---

## 2. Project Analysis & Current State

### Technology & Architecture
- **Current:** Simple Order Matching, Isolated Agents, Basic RAG Memory, Internal News.
- **Target:** Limit Order Book, Social Network/Gossip, Reflection/Learning, Real-World Data feeds.

### Current State
The system successfully simulates basic trading and logs outcomes. However, market mechanics are simplified (no limit orders), agents act in isolation (no direct communication), and they do not "learn" higher-level strategies over long durations.

## 3. Context & Problem Definition

### Problem Statement
To study truly emergent economic behaviors (like bubbles driven by social hype, or liquidity crises), the simulation needs more complex interaction layers than just "Agent buys from Engine."

### Success Criteria
- [ ] Task defined for **Limit Order Book (LOB)** implementation.
- [ ] Task defined for **Agent "Gossip" Network** (P2P communication).
- [ ] Task defined for **Cognitive Reflection** (Long-term learning).
- [ ] Task defined for **Real-World Data Injection** (News/Price feeds).

---

## 4. Development Mode Context
- **Priority:** Future / Post-Submission.
- **Breaking Changes:** High (Fundamental changes to `MarketEngine` and `Trader.act`).

---

## 5. Technical Requirements

### Feature 1: Realistic Market Microstructure (LOB)
- Replace simple negotiation with a full **Limit Order Book**.
- Allow types: `LIMIT`, `MARKET`, `STOP_LOSS`.
- Enables "Market Maker" agents to provide liquidity spreads.

### Feature 2: Agent Communication (The "Gossip" Layer)
- Implement a broadcast channel (e.g., "Twitter" simulation).
- Agents can publish `Opinion` objects.
- Agents consume a `SocialFeed` in addition to `MarketState`.
- Hypothesis: Will we see viral panic or pump-and-dump schemes?

### Feature 3: Cognitive Reflection (Learning)
- Periodically (e.g., every 50 ticks), pause execution.
- Agents query their own history: "What worked? What failed?"
- Synthesize new `CoreBelief` memories (e.g., "I lose money on volatile stocks -> Avoid high volatility").
- Reference: *Generative Agents* (Park et al., 2023).

### Feature 4: Robustness & Self-Correction
- Implement "Retry-with-Feedback" for LLM calls.
- If JSON parsing fails, send the error back to the model to fix itself.
- Reduces "skipped turns" to near zero.

---

## 6. Implementation Plan (Draft)

### Phase 1: Robustness
- Add Pydantic retry loops to `Trader.act`.

### Phase 2: Microstructure
- Refactor `MarketEngine` to use a standard `OrderBook` matching algorithm.

### Phase 3: Social Layer
- Create `SocialGraph` in `src/market/social.py`.
- Update prompts to include "Recent Tweets".

### Phase 4: Reflection
- Add `reflect()` method to `Trader` class.
- Trigger reflection based on memory depth or P&L milestones.

---

## 11. File Structure & Organization
- `src/market/limit_order_book.py`
- `src/market/social.py`
- `src/agents/reflection.py`
