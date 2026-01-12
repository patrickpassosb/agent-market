# AI Task Planning Template - Enhanced Observability

## 1. Task Overview

### Task Title
**Title:** Enhanced Observability & Experiment Evidence

### Goal Statement
**Goal:** Implement visual reporting tools and advanced logging to provide "experiment evidence" (plots, transaction history) required for the challenge submission.

---

## 2. Project Analysis & Current State

### Technology & Architecture
- **Visualization:** Matplotlib / Seaborn (already in dependencies).
- **Storage:** SQLite (Ledger).
- **Reporting:** Markdown-based report generation.

### Current State
Market data is logged to console and visible in the dashboard, but there is no automated way to generate post-simulation reports or price trend graphs.

## 3. Context & Problem Definition

### Problem Statement
The challenge requires "experiment evidence (videos, plots, logs)". While logs exist, plots and structured reports are missing.

### Success Criteria
- [x] `src/analysis/report.py` generates a Markdown summary per run in `reports/<run_id>/report.md`.
- [x] `src/analysis/chart.py` creates PNG price history plots for each asset and an agent ROI chart.
- [x] `main.py` prints an end-of-simulation summary to the terminal using `Rich`.
- [x] `main.py` supports a `--report` flag to trigger report generation on exit.

---

## 4. Implementation Plan

### Phase 1: Data Extraction
1. Write queries in `Ledger` to extract price-over-time data and agent P/L history.

### Phase 2: Visualization
1. Implement `generate_market_summary_plot()` using Seaborn.
2. Implement `generate_agent_performance_chart()` to show ROI rankings.

### Phase 3: Reporting
1. Create a template for `reports/latest_run_summary.md`.
2. Add a CLI flag `--report` to `main.py` that triggers report generation on exit.

---

## 5. Verification Methods
1. Run a 100-tick simulation.
2. Verify that `reports/` folder contains a new plot and summary file.
