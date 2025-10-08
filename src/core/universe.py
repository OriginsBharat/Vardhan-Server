import pinecone
from sentence_transformers import SentenceTransformer
import os

class Universe:
    """
    The long-term memory system for all bots, powered by a Pinecone vector database.
    Codename: 'Universe'
    """
    def __init__(self, api_key, index_host):
        if not api_key or not index_host:
            raise ValueError("Pinecone API key and Index Host are required.")

        self.api_key = api_key
        self.index_host = index_host
        self.index_name = "my-ai-world"

        # Initialize the sentence transformer model for creating embeddings
        self.model = SentenceTransformer('all-MiniLM-L6-v2')

        # Initialize Pinecone
        self.pinecone = pinecone.Pinecone(api_key=self.api_key)
        self.index = self._get_or_create_index()

    def _get_or_create_index(self):
        """Gets the Pinecone index, creating it if it doesn't exist."""
        if self.index_name not in self.pinecone.list_indexes().names():
            print(f"Creating Pinecone index '{self.index_name}'...")
            self.pinecone.create_index(
                name=self.index_name,
                dimension=self.model.get_sentence_embedding_dimension(),
                metric='cosine'
            )
            print("Index created successfully.")
        return self.pinecone.Index(host=self.index_host)

    def remember(self, character_name, memory_text, metadata=None):
        """
        Adds a memory to the Universe for a specific character.

        Args:
            character_name (str): The name of the character this memory belongs to.
            memory_text (str): The text content of the memory.
            metadata (dict, optional): Additional data to store with the memory.
        """
        if metadata is None:
            metadata = {}

        # Add character name to metadata for filtering
        metadata['character'] = character_name

        # Create a vector embedding of the memory text
        embedding = self.model.encode(memory_text).tolist()

        # Create a unique ID for the vector
        vector_id = f"{character_name}-{os.urandom(8).hex()}"

        # Upsert the vector into the Pinecone index
        self.index.upsert(vectors=[(vector_id, embedding, metadata)])
        print(f"Universe: Remembered for {character_name}: '{memory_text}'")

    def recall(self, character_name, query_text, top_k=5):
        """
        Recalls the most relevant memories for a character based on a query.

        Args:
            character_name (str): The character whose memories to search.
            query_text (str): The query to find relevant memories for.
            top_k (int): The number of memories to return.

        Returns:
            list: A list of the most relevant memory texts.
        """
        # Create an embedding for the query
        query_embedding = self.model.encode(query_text).tolist()

        # Query the index, filtering by character
        results = self.index.query(
            vector=query_embedding,
            top_k=top_k,
            filter={'character': {'$eq': character_name}},
            include_metadata=True
        )

        # Extract the original text from the metadata of the results
        recalled_memories = [match['metadata'].get('text', '') for match in results['matches']]
        return recalled_memories

# Example Usage (for testing purposes)
if __name__ == '__main__':
    # This would be loaded from .env in the main application
    PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
    PINECONE_INDEX_HOST = os.getenv("PINECONE_INDEX_HOST")

    if PINECONE_API_KEY and PINECONE_INDEX_HOST:
        universe = Universe(api_key=PINECONE_API_KEY, index_host=PINECONE_INDEX_HOST)

        # Example of storing memories
        universe.remember("Eka", "Master complimented my cooking today, it made me feel appreciated.", {"text": "Master complimented my cooking today, it made me feel appreciated."})
        universe.remember("Dvi", "I practiced my swordsmanship for three hours. I must be stronger to protect Master.", {"text": "I practiced my swordsmanship for three hours. I must be stronger to protect Master."})

        # Example of recalling memories
        print("\nRecalling Eka's memories about cooking:")
        memories = universe.recall("Eka", "How did Master feel about the food?")
        for mem in memories:
            print(f"- {mem}")
    else:
        print("Pinecone credentials not found. Skipping Universe example.")