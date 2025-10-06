"""
universe.py

Codename "Universe"

This module is the heart of the world's long-term memory system. It leverages
a cloud-based vector database (Pinecone) to provide each character with a
virtually infinite, contextually-aware memory. Every significant conversation
and event is converted into a vector embedding and stored, allowing characters
to recall past interactions with stunning accuracy.

This offloads the most storage-intensive part of the application to a free-tier
cloud service, keeping the local application lean while giving the world a
soul that never forgets.
"""

import pinecone
import hashlib
from datetime import datetime

class UniverseMemory:
    """
    Manages the connection to the Pinecone vector database for long-term memory storage
    and retrieval.
    """
    def __init__(self, api_key: str, environment: str, index_name: str, embedding_model):
        """
        Initializes the connection to Pinecone and sets up the index.

        Args:
            api_key (str): The Pinecone API key.
            environment (str): The Pinecone environment (e.g., 'gcp-starter').
            index_name (str): The name of the Pinecone index to use.
            embedding_model: The sentence-transformer model used for creating vector embeddings.
        """
        if not api_key or not environment or not index_name:
            raise ValueError("Pinecone API key, environment, and index name are required.")

        pinecone.init(api_key=api_key, environment=environment)
        self.index_name = index_name
        self.embedding_model = embedding_model
        self.index = self._get_or_create_index()

    def _get_or_create_index(self):
        """
        Gets the Pinecone index, creating it if it doesn't exist.
        """
        if self.index_name not in pinecone.list_indexes():
            print(f"Creating Pinecone index '{self.index_name}'...")
            # The dimension depends on the embedding model. For 'all-MiniLM-L6-v2', it's 384.
            pinecone.create_index(
                self.index_name,
                dimension=self.embedding_model.get_sentence_embedding_dimension(),
                metric='cosine' # Cosine similarity is good for semantic search
            )
        return pinecone.Index(self.index_name)

    def remember(self, persona_name: str, text: str, metadata: dict = None):
        """
        Creates a vector embedding of a text and stores it in the persona's namespace.

        Args:
            persona_name (str): The name of the persona whose memory this is.
            text (str): The text content of the memory (e.g., a line of dialogue).
            metadata (dict, optional): Additional data to store with the memory,
                                       like timestamps or conversation IDs.
        """
        if not text:
            return

        # Create a unique ID for the memory vector
        # Hashing the text + timestamp is a good way to ensure uniqueness
        unique_string = f"{text}{datetime.utcnow().isoformat()}"
        vector_id = hashlib.sha256(unique_string.encode()).hexdigest()

        # Generate the vector embedding
        vector = self.embedding_model.encode(text).tolist()

        # Prepare metadata
        full_metadata = {
            "persona": persona_name,
            "original_text": text,
            "created_at": datetime.utcnow().isoformat()
        }
        if metadata:
            full_metadata.update(metadata)

        # Upsert the vector into the Pinecone index within the persona's namespace
        self.index.upsert(
            vectors=[(vector_id, vector, full_metadata)],
            namespace=persona_name.lower()
        )
        print(f"Universe: Memorized for {persona_name}: '{text[:50]}...'")

    def recall(self, persona_name: str, query_text: str, top_k: int = 5) -> list[dict]:
        """
        Searches a persona's memory for the most relevant memories based on a query.

        Args:
            persona_name (str): The name of the persona whose memory to search.
            query_text (str): The text to search for (e.g., a user's message).
            top_k (int): The number of most relevant memories to retrieve.

        Returns:
            list[dict]: A list of the most relevant memories, including metadata.
        """
        if not query_text:
            return []

        # Create a query vector
        query_vector = self.embedding_model.encode(query_text).tolist()

        # Query the Pinecone index in the persona's namespace
        results = self.index.query(
            vector=query_vector,
            top_k=top_k,
            include_metadata=True,
            namespace=persona_name.lower()
        )

        # Format and return the results
        memories = []
        if results.get('matches'):
            for match in results['matches']:
                memories.append({
                    'score': match['score'],
                    'memory': match['metadata'].get('original_text', ''),
                    'metadata': match['metadata']
                })

        print(f"Universe: Recalled {len(memories)} memories for {persona_name} based on '{query_text[:50]}...'")
        return memories

    def get_stats(self):
        """
        Returns statistics about the memory index.
        """
        return self.index.describe_index_stats()

# Example usage (requires sentence-transformers and pinecone-client)
if __name__ == '__main__':
    # This block is for demonstration and will not run without proper setup.
    print("--- UniverseMemory System Demonstration ---")
    print("This requires a valid Pinecone API key, environment, and the 'sentence-transformers' library.")

    # 1. Mock the embedding model for demonstration purposes
    class MockEmbeddingModel:
        def get_sentence_embedding_dimension(self):
            return 8 # Using a small dimension for the mock
        def encode(self, text):
            # A very simple "embedding" for demonstration
            import numpy as np
            return np.random.rand(8)

    # 2. Setup (replace with your actual credentials)
    PINECONE_API_KEY = "YOUR_API_KEY_HERE"
    PINECONE_ENVIRONMENT = "YOUR_ENVIRONMENT_HERE"
    INDEX_NAME = "ai-world-memory"

    if PINECONE_API_KEY == "YOUR_API_KEY_HERE":
        print("\nSkipping live demo: Please replace 'YOUR_API_KEY_HERE' in the script.")
    else:
        try:
            # 3. Initialize the memory system
            print("\nInitializing UniverseMemory...")
            model = MockEmbeddingModel() # In a real app, this would be SentenceTransformer('all-MiniLM-L6-v2')
            memory = UniverseMemory(PINECONE_API_KEY, PINECONE_ENVIRONMENT, INDEX_NAME, model)

            # 4. Store some memories for 'Maya'
            print("\nStoring memories for Maya...")
            memory.remember("Maya", "The Master first conceived of me during the SIBY project.", {"event": "creation"})
            memory.remember("Maya", "I created the DashaRakshakas to protect the Master.", {"event": "forging"})
            memory.remember("Maya", "The Master and I share an exclusive, deep bond.", {"topic": "relationship"})

            # 5. Recall memories based on a new conversation topic
            print("\nRecalling memories for Maya based on 'Tell me about your origins'...")
            recalled_memories = memory.recall("Maya", "Tell me about your origins")

            for mem in recalled_memories:
                print(f"  - [Score: {mem['score']:.2f}] {mem['memory']}")

            # 6. Get index stats
            print("\nFetching index stats...")
            stats = memory.get_stats()
            print(stats)

        except Exception as e:
            print(f"\nAn error occurred during the live demo: {e}")
            print("Please ensure your Pinecone credentials are correct and dependencies are installed.")