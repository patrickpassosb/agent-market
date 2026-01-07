"""
Market Ledger (Persistence Layer).

This module handles the permanent storage of market transactions using SQLModel.
It abstracts the database connection and session management.
"""

from typing import List, Optional
from sqlmodel import SQLModel, Session, create_engine, select
import os
from .schema import Transaction

class Ledger:
    """
    Manages database interactions for market transactions.
    
    Attributes:
        engine (Engine): SQLAlchemy Engine instance connected to the SQLite database.
    """

    def __init__(self, db_path: str = "market.db"):
        """
        Initialize the Ledger and the database connection.
        
        Args:
            db_path (str): File path for the SQLite database.
        """
        # connect_args={"check_same_thread": False} is required for SQLite when accessed 
        # from multiple threads (though our sim is currently single-threaded loop).
        self.engine = create_engine(f"sqlite:///{db_path}", connect_args={"check_same_thread": False})
        
        # Initialize tables
        # Use a try-except block to handle cases where tables might already exist 
        # or concurrent access issues during init.
        try:
            SQLModel.metadata.create_all(self.engine)
        except Exception as e:
            # In production, we should log this. For now, we assume it's a non-fatal 
            # issue like pre-existing tables.
            pass

    def record_transaction(self, transaction: Transaction) -> Transaction:
        """
        Persists a completed transaction to the database.
        
        Args:
            transaction (Transaction): The transaction object to save.
            
        Returns:
            Transaction: The refreshed transaction object (with assigned ID).
        """
        with Session(self.engine) as session:
            session.add(transaction)
            session.commit()
            session.refresh(transaction) # Refresh to get the auto-generated ID
            return transaction

    def get_transactions(self, limit: int = 100) -> List[Transaction]:
        """
        Retrieves the most recent transactions from the ledger.
        
        Args:
            limit (int): Maximum number of records to return.
            
        Returns:
            List[Transaction]: List of transaction objects, sorted by newest first.
        """
        with Session(self.engine) as session:
            statement = select(Transaction).order_by(Transaction.timestamp.desc()).limit(limit)
            return list(session.exec(statement).all())