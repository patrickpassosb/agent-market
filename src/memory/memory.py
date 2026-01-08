"""
Agent Memory System (RAG).

This module implements a persistent vector memory for agents using ChromaDB.
It allows agents to store experiences (text) and retrieve them later based on semantic similarity.
This forms the basis of Retrieval Augmented Generation (RAG) for the agents.
"""

import chromadb
from typing import List, Dict, Any
import uuid
import os
from datetime import datetime, timezone

class AgentMemory:
    """
    Manages long-term memory for a specific agent.
    
    Each agent gets its own ChromaDB collection.
    
    Attributes:
        agent_id (str): The ID of the owner agent.
        client (chromadb.PersistentClient): The database client.
        collection (chromadb.Collection): The vector collection for this agent.
    """

    def __init__(self, agent_id: str, db_path: str = "./chroma_db"):
        """
        Initialize the memory system.
        
        Args:
            agent_id (str): Unique ID of the agent.
            db_path (str): Local filesystem path to store the vector DB.
        """
        self.agent_id = agent_id
        # Ensure directory exists for local persistence to avoid Chroma errors
        os.makedirs(db_path, exist_ok=True)
        
        self.client = chromadb.PersistentClient(path=db_path)
        
        # Create or get a collection specific to this agent
        # Collections are isolated namespaces within Chroma
        self.collection = self.client.get_or_create_collection(
            name=f"agent_memory_{agent_id}"
        )

    def add_memory(self, text: str, metadata: Dict[str, Any] = None):
        """
        Stores a textual memory.
        
        The text is embedded (vectorized) by Chroma's default embedding function
        and stored with metadata.
        
        Args:
            text (str): The content to remember.
            metadata (Dict[str, Any], optional): Additional context (e.g., timestamp, mood).
        """
        if metadata is None:
            metadata = {}
        
        # Automatically add timestamp for temporal context
        metadata.setdefault("timestamp", datetime.now(timezone.utc).timestamp())  # https://github.com/python/cpython/blob/main/Doc/library/datetime.rst (Context7 /python/cpython)

        self.collection.add(
            documents=[text],
            metadatas=[metadata],
            ids=[str(uuid.uuid4())] # Generate unique ID for the memory fragment
        )

    def retrieve_memory(self, query: str, n_results: int = 5) -> List[str]:
        """
        Retrieves the most relevant memories for a given query.
        
        Args:
            query (str): The search text (e.g., "market strategy").
            n_results (int): How many matches to return.
            
        Returns:
            List[str]: A list of matched memory texts.
        """
        results = self.collection.query(
            query_texts=[query],
            n_results=n_results
        )
        
        # Chroma returns a list of lists (one per query)
        # We only queried one string, so we return the first list of documents.
        if results and results["documents"]:
            return results["documents"][0]
        return []
