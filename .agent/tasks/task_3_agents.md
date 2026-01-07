# Task 3: Agent Implementation

## 1. Task Overview

### Task Title
**Title:** Agent Logic and LLM Integration

### Goal Statement
**Goal:** Implement the autonomous agents (`BaseAgent`, `Trader`) that interact with the market. These agents will use `litellm` to query Gemini/GPT models and return structured `AgentAction`s using Pydantic validation.

---

## 2. Project Analysis & Current State

### Technology & Architecture
- **LLM Client:** `litellm` (supports Gemini, OpenAI, etc).
- **Validation:** `pydantic` (for `response_format`).
- **Memory:** `chromadb` (Stub/Basic wrapper needed).
- **Core Integration:** Agents need to interface with `MarketEngine`.

## 3. Context & Problem Definition

### Problem Statement
Currently, we have a market but no active participants. We need to build the agents that can "see" the market state and make rational (or irrational, based on personality) trading decisions.

### Success Criteria
- [ ] `BaseAgent` abstract class implemented.
- [ ] `Trader` agent implemented with `perceive()` and `act()` methods.
- [ ] `litellm` integration working with `response_format` to enforce `AgentAction` schema.
- [ ] Agents can successfully generate valid BUY/SELL orders via LLM.
- [ ] Basic "Memory" interface defined (even if simple list for now, to be expanded).

---

## 9. Implementation Plan

- Step 1: Implement `src/memory/memory.py` (Basic interface).
- Step 2: Implement `src/agents/base.py`.
- Step 3: Implement `src/agents/trader.py` (with LLM call).
- Step 4: Verify with `tests/demo_agent.py` (Mock LLM or real call).
