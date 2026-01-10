# AI Task Planning Template - Starter Framework

> **About This Template:** This is a systematic framework for planning and executing technical projects with AI assistance. Use this structure to break down complex features, improvements, or fixes into manageable, trackable tasks that AI agents can execute effectively.

---

## 1. Task Overview

### Task Title
**Title:** Overhaul Frontend to Premium Trading Dashboard

### Goal Statement
**Goal:** Transform the existing "Terminal Live" frontend into a high-fidelity, Bloomberg-style trading terminal with real-time data visualization, agent performance tracking, and AI-driven market insights. This will improve trust in the simulation and provide clearer insights into agent behavior.

---

## 2. Project Analysis & Current State

### Technology & Architecture
- **Frameworks & Versions:** Next.js 14 (App Router), Tailwind CSS v4
- **Language:** TypeScript
- **State Management:** React Hooks + WebSockets
- **Visualization:** lightweight-charts
- **UI & Styling:** Glassmorphism, Neon/Futuristic theme

### Current State
- Minimal terminal log and text-based ticker watch.
- WebSocket streaming market prices.
- Agents act in background, but visuals are basic.

## 3. Context & Problem Definition

### Problem Statement
The current UI is "unclear" and "ugly," making it difficult to visualize the value of the simulation. It lacks high-fidelity charts, agent profiles, and synthesized insights, which are crucial for a multi-agent system demonstration.

### Success Criteria
- [ ] UI redesigned with a premium glassmorphic aesthetic (matching the generated mockup).
- [ ] **MainChart**: Real-time TradingView-style chart with area/candlestick series and volume.
- [ ] **MarketPulse**: Sidebar with glowing trendlines for all supported assets.
- [ ] **AgentRoster**: Card-based profiles showing agent strategy, P&L, and live activity.
- [ ] **SentimentFeed**: Dedicated panel for "Journalist Agent" news and market sentiment.
- [ ] Responsive grid layout with header stats (Ticker, Volatility, Active Agents).

---

## 4. Development Mode Context
- **🚨 Project Stage:** Critical UI Overhaul
- **Breaking Changes:** Acceptable (frontend only)
- **Data Handling:** Volatile (real-time stream)
- **User Base:** Evaluators, Developers
- **Priority:** Very High

---

## 5. Technical Requirements

### Functional Requirements
- Live price updates via WebSocket.
- Initial state fetch via REST.
- Interactive chart displaying price action.
- Agent feed showing structured logs (BUY/SELL/HOLD + reasoning).

### Non-Functional Requirements
- **Visuals:** Must WOW the user. Glassmorphism, glowing borders, smooth transitions.
- **Performance:** Low latency updates for chart and tickers.
- **Usability:** High information density without clutter.

### Technical Constraints
- Must use `lightweight-charts`.
- Must be compatible with existing FastAPI backend endpoints (`/ws`, `/state`, `/agents`).

---

## 6. Data & Database Changes
None.

---

## 7. API & Backend Changes
None (reusing existing endpoints).

---

## 8. Frontend Changes

### New Components
- `MarketPulse`: Sparklines-based ticker list.
- `AgentRoster`: Card-based agent grid.
- `SentimentFeed`: AI-driven news card list.
- `DashboardLayout`: Main grid container.

### Updated Components
- `RealtimeChart`: Switched to Area/Candlestick with better aesthetics.
- `Dashboard`: Orchestrator for the new layout.

---

## 9. Implementation Plan
1. **Design System**: Define HSL color tokens and glassmorphism utility classes in `globals.css`.
2. **Layout Shell**: Create the main grid structure in `Dashboard.tsx`.
3. **MarketPulse**: Build the sidebar with ticker updates.
4. **AgentRoster**: Implement the agent profile cards.
5. **RealtimeChart**: Enhance the chart with better styling and data handling.
6. **SentimentFeed**: Connect to the journalist news data.
7. **Final Polish**: Transitions and micro-animations.

---

## 10. Task Completion Tracking
- [x] Setup Design System
- [x] Implement Layout Shell
- [x] Build MarketPulse
- [x] Build AgentRoster
- [x] Build RealtimeChart
- [x] Build SentimentFeed
- [x] Polish & Verify

---

## 11. File Structure & Organization
- `frontend/app/globals.css`
- `frontend/components/MarketPulse.tsx`
- `frontend/components/AgentRoster.tsx`
- `frontend/components/SentimentFeed.tsx`
- `frontend/components/RealtimeChart.tsx`

---

## 12. AI Agent Instructions

### Implementation Workflow
🎯 **MANDATORY PROCESS:**
- Use Context7 for any advanced `lightweight-charts` features (area series styling).
- Ensure all components are type-safe.

---

## 13. Second-Order Impact Analysis
Improved visibility will likely lead to more focused requests for agent strategy improvements.
