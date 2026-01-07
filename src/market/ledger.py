from typing import List, Optional
from sqlmodel import SQLModel, Session, create_engine, select
import os
from .schema import Transaction

class Ledger:
    def __init__(self, db_path: str = "market.db"):
        self.engine = create_engine(f"sqlite:///{db_path}")
        SQLModel.metadata.create_all(self.engine)

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
