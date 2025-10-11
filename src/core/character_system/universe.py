import pinecone
from sentence_transformers import SentenceTransformer
import logging
from config import Config
import uuid
import asyncio

class Universe:
    """
    Manages the long-term, contextual memory of the AI world using Pinecone.
    """
    def __init__(self, config: Config):
        self.logger = logging.getLogger(__name__)
        self.config = config
        self.model = None
        self.index = None

        if not self.config.pinecone_api_key or not self.config.pinecone_host:
            self.logger.warning("Pinecone API Key or Host is not configured. Universe memory will be disabled.")
            return

        try:
            # Initialize Pinecone
            pinecone.init(api_key=self.config.pinecone_api_key)

            self.index_name = "my-ai-world"

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
            self.logger.critical(f"Failed to initialize Pinecone: {e}. Universe memory will be disabled.")
            self.index = None

    async def remember(self, character_name: str, text: str):
        """
        Stores a piece of text (a memory) for a character in the vector database.
        """
        if not self.index or not self.model:
            return

        try:
            loop = asyncio.get_running_loop()
            def _encode_and_upsert():
                vector = self.model.encode(text).tolist()
                metadata = {'character': character_name, 'text': text}
                memory_id = str(uuid.uuid4())
                self.index.upsert(vectors=[(memory_id, vector, metadata)])

            await loop.run_in_executor(None, _encode_and_upsert)
            self.logger.info(f"Remembered for {character_name}: '{text[:50]}...'")
        except Exception as e:
            self.logger.error(f"Failed to upsert memory to Pinecone for {character_name}: {e}")

    async def recall(self, character_name: str, query_text: str, top_k: int = 5) -> list[str]:
        """
        Recalls the most relevant memories for a character based on a query.
        """
        if not self.index or not self.model:
            return []

        try:
            loop = asyncio.get_running_loop()
            def _query():
                query_vector = self.model.encode(query_text).tolist()
                results = self.index.query(
                    vector=query_vector,
                    filter={'character': {'$eq': character_name}},
                    top_k=top_k,
                    include_metadata=True
                )
                return [match['metadata']['text'] for match in results['matches']]

            recalled_memories = await loop.run_in_executor(None, _query)
            self.logger.info(f"Recalled {len(recalled_memories)} memories for {character_name}.")
            return recalled_memories
        except Exception as e:
            self.logger.error(f"Failed to query memories from Pinecone for {character_name}: {e}")
            return []