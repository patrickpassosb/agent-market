# AI Task Planning Template - Vertex AI Integration

## 1. Task Overview

### Task Title
**Title:** Integration of Google Vertex AI Provider

### Goal Statement
**Goal:** Integrate Google Vertex AI as a supported LLM provider to leverage the user's free credits ($300) and access robust, high-RPM models (Gemini 1.5 Pro/Flash) for the simulation.

---

## 2. Project Analysis & Current State

### Technology & Architecture
- **Orchestration:** Python `asyncio` loop.
- **LLM Routing:** `LiteLLM` handles API calls.
- **Configuration:** `.env` file and `src/utils/personas.py`.

### Current State
- Supports Groq, Cerebras, SambaNova, Gemini (AI Studio), and OpenRouter.
- Vertex AI is missing from dependencies and routing logic.

## 3. Context & Problem Definition

### Problem Statement
The user has Vertex AI credits but the system cannot currently use them. Relying only on free-tier APIs (Groq/Gemini Studio) risks rate limits. Vertex AI offers enterprise-grade quotas.

### Success Criteria
- [x] `google-cloud-aiplatform` installed in `pyproject.toml`.
- [x] `.env.example` updated with Vertex credentials (`VERTEXAI_PROJECT`, `VERTEXAI_LOCATION`, `GOOGLE_APPLICATION_CREDENTIALS`).
- [x] `src/utils/personas.py` updated to route to `vertex_ai/gemini-1.5-pro` and `vertex_ai/gemini-1.5-flash`.
- [x] System successfully initializes with `MODEL_PROVIDER_ORDER=vertex_ai`.

---

## 4. Development Mode Context
- **Priority:** High (Requested by user).
- **Breaking Changes:** None (additive).

---

## 5. Technical Requirements

### Functional Requirements
- System must authenticate using Application Default Credentials (ADC) or a Service Account JSON file.
- Vertex AI models must be selectable in the `PROVIDER_ORDER`.

---

## 6. Implementation Plan

### Phase 1: Dependencies
1. Add `google-cloud-aiplatform` to `pyproject.toml` and install. (Completed)

### Phase 2: Configuration
1. Update `.env.example` with Vertex specific variables. (Completed)

### Phase 3: Routing Logic
1. Update `src/utils/personas.py`:
   - Add `VERTEX_MODELS` mapping.
   - Update `_available_models` to check for `VERTEXAI_PROJECT`. (Completed)

---

## 7. Task Completion Tracking
- [x] Phase 1: Dependencies
- [x] Phase 2: Configuration
- [x] Phase 3: Routing Logic
