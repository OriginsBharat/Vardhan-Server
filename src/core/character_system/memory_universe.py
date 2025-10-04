# src/core/character_system/memory_universe.py
# Implements Codename "Universe": the long-term memory system using a vector database.

import chromadb
import logging
from typing import List, Dict
from datetime import datetime

# The directory where the persistent vector database will be stored.
DB_PATH = "data/memory_universe"

class MemoryUniverse:
    """
    Manages the long-term, contextual memory for all characters using a vector database.
    Each character gets their own "collection" within the database.
    """
    def __init__(self):
        try:
            # Initialize a persistent client. Data will be saved to disk.
            self.client = chromadb.PersistentClient(path=DB_PATH)
            logging.info(f"MemoryUniverse initialized. Vector database is stored at: {DB_PATH}")
        except Exception as e:
            logging.error(f"CRITICAL: Failed to initialize ChromaDB. Long-term memory will not function. Error: {e}")
            self.client = None

    def _get_collection(self, character_name: str):
        """
        Gets or creates a dedicated memory collection for a character.
        """
        if not self.client:
            return None
        # Collection names must be lowercase and meet certain criteria.
        collection_name = f"memories_for_{character_name.lower().replace(' ', '_')}"
        return self.client.get_or_create_collection(name=collection_name)

    def add_memory(self, character_name: str, memory_text: str, metadata: Dict = None):
        """
        Adds a new memory to a character's collection. The memory text itself
        is converted into a vector embedding by ChromaDB automatically.

        Args:
            character_name: The name of the character whose memory this is.
            memory_text: The text content of the memory (e.g., a summary of a conversation).
            metadata: Optional dictionary for storing extra info, like timestamps.
        """
        collection = self._get_collection(character_name)
        if not collection:
            logging.error(f"Cannot add memory for {character_name}; vector database is not available.")
            return

        # Use a timestamp as a unique ID for the memory.
        memory_id = datetime.utcnow().isoformat()

        # Add a timestamp to the metadata if not already present.
        if metadata is None:
            metadata = {}
        metadata["timestamp"] = memory_id

        try:
            collection.add(
                documents=[memory_text],
                metadatas=[metadata],
                ids=[memory_id]
            )
            logging.info(f"Added new memory to {character_name}'s universe: '{memory_text[:50]}...'")
        except Exception as e:
            logging.error(f"Failed to add memory to ChromaDB for {character_name}: {e}")

    def recall_memories(self, character_name: str, query_text: str, num_memories: int = 5) -> List[str]:
        """
        Recalls the most relevant memories for a character based on a query.

        Args:
            character_name: The name of the character recalling memories.
            query_text: The text to search for (e.g., the current conversation topic).
            num_memories: The maximum number of relevant memories to return.

        Returns:
            A list of the most relevant memory texts.
        """
        collection = self._get_collection(character_name)
        if not collection:
            logging.error(f"Cannot recall memories for {character_name}; vector database is not available.")
            return []

        if collection.count() == 0:
            return [] # No memories to recall

        try:
            results = collection.query(
                query_texts=[query_text],
                n_results=min(num_memories, collection.count()) # Cannot request more results than exist
            )
            # The results are nested; we want the 'documents' from the first query.
            recalled_docs = results.get('documents', [[]])[0]
            logging.info(f"Recalled {len(recalled_docs)} memories for {character_name} based on query: '{query_text[:50]}...'")
            return recalled_docs
        except Exception as e:
            logging.error(f"Failed to query memories from ChromaDB for {character_name}: {e}")
            return []