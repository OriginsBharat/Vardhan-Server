import httpx
import logging
from config import config

class OllamaClient:
    """
    Client for interacting with the Ollama API for text generation.
    """
    def __init__(self):
        self.api_url = config.ollama_api_url
        self.model = config.llm_model
        self.logger = logging.getLogger(__name__)
        self.logger.info(f"OllamaClient initialized for model '{self.model}' at {self.api_url}")

    async def generate_text(self, system_prompt: str, user_prompt: str) -> str:
        """
        Generates text using the specified model and prompts.
        """
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]

        self.logger.info(f"Generating text for prompt: {user_prompt[:80]}...")
        try:
            async with httpx.AsyncClient(timeout=180.0) as client:
                response = await client.post(
                    f"{self.api_url}/api/chat",
                    json={
                        "model": self.model,
                        "messages": messages,
                        "stream": False
                    }
                )
                response.raise_for_status()
                data = response.json()
                self.logger.info("Successfully generated text response.")
                return data["message"]["content"].strip()
        except httpx.RequestError as e:
            self.logger.error(f"Error connecting to Ollama API: {e}")
            return f"*Jules's Note: Could not connect to the Ollama server at {self.api_url}. Is it running?*"
        except Exception as e:
            self.logger.error(f"An unexpected error occurred during text generation: {e}", exc_info=True)
            return "*Jules's Note: An unexpected error occurred while I was trying to think.*"