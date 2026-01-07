import chromadb
from typing import List, Dict, Any
import uuid
import os

class AgentMemory:
    def __init__(self, agent_id: str, db_path: str = "./chroma_db"):
        self.agent_id = agent_id
        # Ensure directory exists for local persistence
        os.makedirs(db_path, exist_ok=True)
        
        self.client = chromadb.PersistentClient(path=db_path)
        self.collection = self.client.get_or_create_collection(
            name=f"agent_memory_{agent_id}"
        )

    def add_memory(self, text: str, metadata: Dict[str, Any] = None):
        if metadata is None:
            metadata = {}
        
        # Always store timestamp if not present
        from datetime import datetime
        metadata.setdefault("timestamp", datetime.utcnow().timestamp())

        self.collection.add(
            documents=[text],
            metadatas=[metadata],
            ids=[str(uuid.uuid4())]
        )

    def retrieve_memory(self, query: str, n_results: int = 5) -> List[str]:
        results = self.collection.query(
            query_texts=[query],
            n_results=n_results
        )
        if results and results["documents"]:
            return results["documents"][0]
        return []
