# Global Guidelines for AI Challenges

These guidelines offer reusable tips, recommended project structure, and consistent evaluation criteria for all challenges — from chatbots to autonomous agents, generative systems, and robotics tasks. They are intentionally broad and technology‑agnostic to preserve candidate creativity, while giving evaluators a unified framework to assess solutions fairly.

---

## General Tips for Candidates

* You do **not** need paid APIs to complete any challenge. You may use free tiers or aggregators like OpenRouter.
* Prefer **small, clean, well‑structured systems** over large but unclear ones.
* Demonstrate **traceability**: logs, agent messages, intermediate results, or a debug mode.
* Clear documentation matters as much as code quality.

---

## README Checklist (Strongly Recommended)

Each project should include a `README.md` with:

1. **Overview** — What the project does and which challenge it solves.
2. **Architecture** — Short explanation or diagram of how components interact.
3. **How to Run** — Setup steps, environment variables, and commands.
4. **Demo Guide** — How to trigger the evaluation flow or main scenario.

---

## How We Evaluate

Evaluation is consistent across challenges and considers:

### 1. Correctness & Functionality

* Does the system perform the intended challenge end‑to‑end?
* Is there a clear demonstration path?

### 2. Architecture & Code Quality

* Clear module separation (agents, tools, orchestration, data).
* Readable, maintainable, reasonably documented code.

### 3. Autonomy & Agent Behavior

* For multi‑agent challenges: meaningful roles, communication, reasoning.
* System adapts to different inputs or scenarios with minimal changes.

### 4. Observability & Documentation

* Logs, traces, or debug outputs show how the system works internally.
* README allows evaluators to run and understand the system easily.

A light rubric:

* ⭐⭐⭐⭐⭐ — Full autonomous flow, clear architecture, robust demo, strong reasoning.
* ⭐⭐⭐⭐ — Mostly complete, minor rough edges, well‑structured.
* ⭐⭐⭐ — Works in limited scenario, partially autonomous.
* ⭐⭐ — Significant pieces missing.
* ⭐ — Prototype only.

---

## LLM & Tools Usage Guidelines

* Any LLM is allowed; free tiers or local models are acceptable.
* Vector DBs, queues, or frameworks are optional—use only if they add value.
* Interfaces matter more than vendors; keep boundaries clean (e.g., an LLM client interface, a tool abstraction).

---

## Minimum Expected Submission

* Git repository with:

  * Source code
  * `README.md` following the checklist
  * Optional Dockerfile / docker-compose for reproducibility
* At least one **script or command** that demonstrates the end‑to‑end flow.
* Logs or traces showing how the system behaved.