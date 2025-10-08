import pinecone
from sentence_transformers import SentenceTransformer
import logging
from config import Config
import uuid

class Universe:
    """
    Manages the long-term, contextual memory of the AI world using Pinecone.
    """
    def __init__(self, config: Config):
        self.logger = logging.getLogger(__name__)
        self.config = config
        self.model = None
        self.index = None
        try:
            # Initialize Pinecone
            pinecone.init(api_key=self.config.pinecone_api_key)

            # Define the index name
            self.index_name = "my-ai-world"

            # Check if index exists, create if not
            if self.index_name not in pinecone.list_indexes():
                self.logger.info(f"Creating new Pinecone index: {self.index_name}")
                pinecone.create_index(
                    name=self.index_name,
                    dimension=768,  # Dimension for 'all-MiniLM-L6-v2'
                    metric='cosine'
                )

            self.index = pinecone.Index(host=self.config.pinecone_host)

            # Load the sentence transformer model
            self.model = SentenceTransformer('all-MiniLM-L6-v2')

            self.logger.info("Universe (Pinecone Memory) initialized successfully.")
        except Exception as e:
            self.logger.error(f"Failed to initialize Pinecone: {e}")
            self.index = None

    async def remember(self, character_name: str, text: str):
        """
        Stores a piece of text (a memory) for a character in the vector database.

        Args:
            character_name: The name of the character this memory belongs to.
            text: The conversational text or event to remember.
        """
        if not self.index:
            self.logger.warning("Pinecone index not available. Cannot remember.")
            return

        try:
            vector = self.model.encode(text).tolist()
            metadata = {'character': character_name, 'text': text}

            # Each memory gets a unique ID
            memory_id = str(uuid.uuid4())

            self.index.upsert(vectors=[(memory_id, vector, metadata)])
            self.logger.info(f"Remembered for {character_name}: '{text[:50]}...'")
        except Exception as e:
            self.logger.error(f"Failed to upsert memory to Pinecone: {e}")

    async def recall(self, character_name: str, query_text: str, top_k: int = 5) -> list[str]:
        """
        Recalls the most relevant memories for a character based on a query.

        Args:
            character_name: The character whose memories to search.
            query_text: The text to search for relevant memories.
            top_k: The number of memories to return.

        Returns:
            A list of the most relevant memory texts.
        """
        if not self.index:
            self.logger.warning("Pinecone index not available. Cannot recall.")
            return []

        try:
            query_vector = self.model.encode(query_text).tolist()

            # Filter by character name to only get relevant memories
            results = self.index.query(
                vector=query_vector,
                filter={'character': {'$eq': character_name}},
                top_k=top_k,
                include_metadata=True
            )

            recalled_memories = [match['metadata']['text'] for match in results['matches']]
            self.logger.info(f"Recalled {len(recalled_memories)} memories for {character_name}.")
            return recalled_memories
        except Exception as e:
            self.logger.error(f"Failed to query memories from Pinecone: {e}")
            return []