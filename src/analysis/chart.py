import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

def plot_market_history(db_path: str = "market.db", output_dir: str = "plots"):
    """Reads the ledger and generates market analysis plots."""
    
    if not os.path.exists(db_path):
        print(f"Database {db_path} not found.")
        return

    os.makedirs(output_dir, exist_ok=True)
    
    conn = sqlite3.connect(db_path)
    
    # query transactions
    query = "SELECT * FROM 'transaction'"
    df = pd.read_sql_query(query, conn)
    conn.close()
    
    if df.empty:
        print("No transactions found in database.")
        return

    # Ensure timestamp is datetime (assuming it's stored as ISO string or timestamp)
    # The current schema stores valid datetimes approx tick time.
    # If using auto-increment ID as proxy for time is safer if timestamps are close.
    df['id'] = df['id'].astype(int)

    # --- Plot 1: Price History ---
    plt.figure(figsize=(12, 6))
    sns.lineplot(data=df, x='id', y='price', marker='o')
    plt.title('Market Price History (Real-Time)')
    plt.xlabel('Transaction Sequence')
    plt.ylabel('Price ($)')
    plt.grid(True)
    plt.savefig(f"{output_dir}/price_history.png")
    print(f"Saved {output_dir}/price_history.png")
    
    # --- Plot 2: Volume per Agent ---
    # Who is buying/selling the most?
    plt.figure(figsize=(12, 6))
    
    # Combine buyer and seller counts
    agent_counts = df['buyer_id'].value_counts().add(df['seller_id'].value_counts(), fill_value=0)
    
    sns.barplot(x=agent_counts.index, y=agent_counts.values, palette="viridis")
    plt.title('Trading Activity by Agent')
    plt.xlabel('Agent ID')
    plt.ylabel('Total Transactions (Buy + Sell)')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(f"{output_dir}/agent_activity.png")
    print(f"Saved {output_dir}/agent_activity.png")

if __name__ == "__main__":
    plot_market_history()
