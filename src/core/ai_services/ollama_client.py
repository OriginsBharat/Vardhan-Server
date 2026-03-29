import httpx
import logging

class OllamaClient:
    """
    Client for interacting with the Ollama API for text generation.
    """
    def __init__(self, api_url: str):
        self.api_url = api_url
        self.logger = logging.getLogger(__name__)

    async def generate_text(self, prompt: str, model: str) -> str:
        """
        Generates text using the specified model and prompt.

        Args:
            prompt: The text prompt to send to the model.
            model: The name of the Ollama model to use.

        Returns:
            The generated text as a string, or an error message.
        """
        self.logger.info(f"Generating text with model {model}...")
        try:
            async with httpx.AsyncClient(timeout=300.0) as client:
                response = await client.post(
                    f"{self.api_url}/api/generate",
                    json={
                        "model": model,
                        "prompt": prompt,
                        "stream": False
                    },
                )
                response.raise_for_status()
                data = response.json()
                self.logger.info("Successfully generated text.")
                # Ensure the response is clean and properly formatted
                return data.get("response", "").strip().replace('\\"', '"')
        except httpx.RequestError as e:
            self.logger.error(f"Error connecting to Ollama API: {e}")
            return f"Error: Could not connect to the Ollama server at {self.api_url}. Is it running?"
        except Exception as e:
            self.logger.error(f"An unexpected error occurred during text generation: {e}")
            return "Error: An unexpected error occurred while generating text."