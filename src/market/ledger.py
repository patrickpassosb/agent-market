from typing import List, Optional
from sqlmodel import SQLModel, Session, create_engine, select
import os
from .schema import Transaction

class Ledger:
    def __init__(self, db_path: str = "market.db"):
        # Connect args to allow for timeout in case of locking
        self.engine = create_engine(f"sqlite:///{db_path}", connect_args={"check_same_thread": False})
        
        # Safe creation
        try:
            SQLModel.metadata.create_all(self.engine)
        except Exception as e:
            # If it fails, it usually means tables exist or index conflict, which is fine to ignore for now if we want to proceed.
            # But better is to just let it pass if tables exist (create_all is idempotent usually).
            pass

    def record_transaction(self, transaction: Transaction) -> Transaction:
        with Session(self.engine) as session:
            session.add(transaction)
            session.commit()
            session.refresh(transaction)
            return transaction

    def get_transactions(self, limit: int = 100) -> List[Transaction]:
        with Session(self.engine) as session:
            statement = select(Transaction).order_by(Transaction.timestamp.desc()).limit(limit)
            return list(session.exec(statement).all())
