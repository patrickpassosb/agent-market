"""
Market Ledger (Persistence Layer).

This module handles the permanent storage of market transactions using SQLModel.
It abstracts the database connection and session management.
"""

from typing import List, Optional
import logging
from sqlmodel import SQLModel, Session, create_engine, select
import os
import sqlite3
from .schema import Transaction, InteractionLog

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
        try:
            SQLModel.metadata.create_all(self.engine)
        except Exception:
            logging.exception("Failed to initialize ledger tables")
            raise
        self._ensure_run_id_column(db_path)

    def _ensure_run_id_column(self, db_path: str) -> None:
        """
        Ensure run_id columns exist for backward-compatible migrations.
        """
        def ensure_column(cursor, table: str):
            """Add run_id column to a table if it exists and lacks it."""
            cursor.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
                (table,),
            )
            if cursor.fetchone() is None:
                return
            cursor.execute(f'PRAGMA table_info("{table}")')
            columns = {row[1] for row in cursor.fetchall()}
            if "run_id" not in columns:
                cursor.execute(f'ALTER TABLE "{table}" ADD COLUMN run_id TEXT')

        try:
            with sqlite3.connect(db_path) as conn:  # https://github.com/python/cpython/blob/main/Doc/library/sqlite3.rst (Context7 /python/cpython)
                cursor = conn.cursor()
                ensure_column(cursor, "transaction")
                ensure_column(cursor, "interactionlog")
                conn.commit()
        except sqlite3.OperationalError:
            # Tables may not exist yet; create_all will handle them on next run.
            return

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

    def record_interaction(self, interaction: InteractionLog) -> InteractionLog:
        """
        Persists a non-transaction interaction (actions, negotiations) to the database.
        """
        with Session(self.engine) as session:
            session.add(interaction)
            session.commit()
            session.refresh(interaction)
            return interaction

    def get_interactions(self, limit: int = 100) -> List[InteractionLog]:
        """
        Retrieves the most recent interaction logs.
        """
        with Session(self.engine) as session:
            statement = select(InteractionLog).order_by(InteractionLog.timestamp.desc()).limit(limit)
            return list(session.exec(statement).all())
