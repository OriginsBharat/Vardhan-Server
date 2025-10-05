# src/core/character_system/memory_universe.py
# Implements Codename "Universe": the long-term memory system using Pinecone.

import pinecone
import logging
from typing import List, Dict
from datetime import datetime

from src.config import Config

# This is the name of the index we will create in the Pinecone account.
INDEX_NAME = "my-ai-world"

class MemoryUniverse:
    """
    Manages the long-term, contextual memory for all characters using Pinecone.
    """
    def __init__(self, config: Config):
        self.config = config
        try:
            self.pinecone_client = pinecone.Pinecone(api_key=self.config.PINECONE_API_KEY)
            self.index = self.pinecone_client.Index(host=self.config.PINECONE_INDEX_HOST)
            logging.info(f"MemoryUniverse initialized. Connected to Pinecone index via host.")
        except Exception as e:
            logging.error(f"CRITICAL: Failed to initialize Pinecone. Long-term memory will not function. Error: {e}")
            self.pinecone_client = None
            self.index = None

    def add_memory(self, character_name: str, memory_text: str, metadata: Dict = None):
        """
        Adds a new memory to the character's namespace in the Pinecone index.
        The conversion of text to a vector is handled by Pinecone's inference pipeline.

        Args:
            character_name: The namespace for the character's memories.
            memory_text: The text content of the memory.
            metadata: Optional dictionary for storing extra info.
        """
        if not self.index:
            logging.error(f"Cannot add memory for {character_name}; Pinecone index is not available.")
            return

        memory_id = datetime.utcnow().isoformat()
        if metadata is None:
            metadata = {}
        metadata["timestamp"] = memory_id
        metadata["character"] = character_name

        # We need to create a vector for the memory. We'll use a placeholder for now.
        # A real implementation would use a sentence-transformer model here.
        # For the purpose of this structure, we'll use a dummy vector.
        dummy_vector = [0.1] * 768 # The dimension we will use

        try:
            self.index.upsert(
                vectors=[{"id": memory_id, "values": dummy_vector, "metadata": metadata}],
                namespace=character_name.lower()
            )
            logging.info(f"Added new memory to {character_name}'s universe.")
        except Exception as e:
            logging.error(f"Failed to upsert memory to Pinecone for {character_name}: {e}")

    def recall_memories(self, character_name: str, query_text: str, num_memories: int = 5) -> List[str]:
        """
        Recalls the most relevant memories for a character by querying Pinecone.

        Returns:
            A list of the most relevant memory texts (or their metadata).
        """
        if not self.index:
            logging.error(f"Cannot recall memories for {character_name}; Pinecone index is not available.")
            return []

        # Convert query text to a vector (dummy vector for now)
        query_vector = [0.1] * 768

        try:
            results = self.index.query(
                vector=query_vector,
                top_k=num_memories,
                include_metadata=True,
                namespace=character_name.lower()
            )
            recalled_docs = [match['metadata'].get('text', '') for match in results.get('matches', [])]
            logging.info(f"Recalled {len(recalled_docs)} memories for {character_name}.")
            return recalled_docs
        except Exception as e:
            logging.error(f"Failed to query memories from Pinecone for {character_name}: {e}")
            return []