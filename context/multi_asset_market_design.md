# Design Doc: Multi-Asset Crypto Exchange Simulation

## 1. Vision
Transform the current single-asset market into a **Crypto-Denominated Stock Exchange**. 
Agents will trade traditional stocks (AAPL, TSLA) and crypto assets (ETH, SOL) using **Bitcoin (BTC)** as the money. This creates unique volatility dynamics where asset values fluctuate based on both their intrinsic news and Bitcoin's performance.

## 2. Core Concept Changes

### A. The "Numeraire" (Base Currency)
*   **Current:** USD ($) is the implicit base.
*   **New:** **Bitcoin (BTC)** is the base currency.
    *   Agents hold a "Wallet" containing primarily BTC.
    *   All asset prices are quoted in BTC (e.g., `AAPL/BTC = 0.005`).
    *   Profit/Loss (PnL) is calculated in BTC (Satoshis).

### B. Multi-Asset Support
Instead of a generic `DEFAULT_ITEM`, the system will support a registry of assets.
*   **Tickers:** `AAPL`, `TSLA`, `ETH`, `SOL`.
*   **Market State:** Instead of one price, the state becomes a list of tickers.
    ```python
    # Conceptual Data Structure
    market_state = {
        "AAPL": {"price": 0.0051, "trend": "up", "volatility": "low"},
        "TSLA": {"price": 0.0032, "trend": "down", "volatility": "high"},
        # ...
    }
    ```

## 3. Architecture & Tech Stack Decisions

### A. Database: SQLite vs. Redis?
*   **Decision:** Start with **Python Dictionaries** (Hybrid).
    *   **Core:** Python Dictionaries (In-Memory) for the Order Book are fastest for single-machine simulation.
    *   **Future Upgrade (Redis):** If we move to a distributed system (agents on different servers), we will swap the Order Book backend to Redis Sorted Sets. This is a modular change contained within `order_book.py`.

### B. Agent Cognition (The "Attention" Problem)
An AI agent cannot analyze 50 charts at once. We will implement an **Attention Mechanism**:
1.  **Scanner:** A cheap rule-based script scans all assets.
2.  **Filter:** It identifies "Top Movers" or assets matching the Agent's persona.
3.  **Focus:** The Agent's main "Brain" only analyzes the chosen few to conserve tokens and improve reasoning.

## 4. Implementation Steps

### Phase 1: Configuration & Schema
1.  Modify `schema.py` to support `QuoteCurrency` (BTC) and `AssetPair` (ETH/BTC).
2.  Update `engine.py` to initialize multiple `OrderBook` instances.

### Phase 2: Portfolio Upgrade
1.  Update `Portfolio` class to hold a dictionary of balances: `{'BTC': 1.5, 'AAPL': 100}`.
2.  Update `valuation` logic for BTC totals.

### Phase 3: The "Scanner" Layer
1.  Modify `MarketState` to provide a summary.
2.  Update `Trader` agent to select an asset.

## 5. Critical Risks & Mitigations

### A. The Liquidity Problem ("Empty Rooms")
*   **Issue:** 12 Agents cannot effectively trade 10 different stocks; the markets will be empty/illiquid.
*   **Solution:** We must implement **Automated Market Makers (AMMs)**—dumb bots that randomly place buy/sell orders around the price—to provide baseline liquidity for the AI agents to trade against.

### B. The "Cold Start" Price
*   **Issue:** What is the starting price of AAPL in BTC?
*   **Solution:** A `seed_market()` function will populate the order books with initial realistic orders so the first trade occurs at a logical price.

### C. User Experience (UI)
*   **Issue:** The terminal cannot show 10 live order books at once.
*   **Solution:** Refactor the UI to show a "Ticker Tape" summary and allow the user to cycle through detailed views of specific assets.