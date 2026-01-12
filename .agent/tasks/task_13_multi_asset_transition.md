# Task 13: Multi-Asset Bitcoin-Denominated Transition

## 1. Task Overview

### Task Title
**Title:** Implement Bitcoin-Denominated Stock Market

### Goal Statement
**Goal:** Refactor the core market engine and data schemas to support trading traditional stocks (AAPL, TSLA) priced in Bitcoin (BTC).

---

## 2. Project Analysis & Current State

### Current State
- **Branch:** `new-market`
- **Schema:** Hardcoded for a single item (`DEFAULT_ITEM = "apple"`) and USD-like pricing.
- **Engine:** Manages a single `OrderBook` instance.

## 3. Context & Problem Definition

### Problem Statement
The current system simulates a single USD asset. The goal is to simulate a crypto-native stock exchange where stock prices are quoted in Satoshis/BTC.

### Success Criteria
- [ ] `schema.py` defines `SUPPORTED_ASSETS = ["AAPL", "TSLA", "NVDA", "MSFT"]`.
- [ ] `schema.py` defines `QUOTE_CURRENCY = "BTC"`.
- [ ] `MarketEngine` initializes an order book for each stock.
- [ ] `main.py` is updated to run the multi-stock simulation.

---

## 9. Implementation Plan

### Phase 1: Core Schema & Engine Refactor
- [ ] Update `src/market/schema.py`: Clean up assets.
- [ ] Update `src/market/engine.py`: Support multiple books.
- [ ] Update `src/market/ledger.py`: Record stock tickers.

### Phase 2: Agent Adaptations
- [ ] Update `Portfolio` to hold BTC and Stocks.
- [ ] Update `Trader` prompt to understand the BTC valuation.

---

## 12. AI Agent Instructions
- **Strict Scope:** No ETH, No SOL. Only Stocks/BTC.