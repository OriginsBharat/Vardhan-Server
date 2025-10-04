# src/core/ai_services/ollama_client.py
# Client for interacting with a self-hosted Ollama instance.

import httpx
import json
import logging
from typing import Optional, Dict, Any

from src.config import Config

class OllamaClient:
    """
    Handles all communication with the local Ollama LLM service.
    """
    def __init__(self, config: Config):
        self.config = config
        self.api_url = f"{self.config.OLLAMA_API_URL}/api/generate"
        logging.info("OllamaClient initialized.")

    async def get_completion(self, prompt: str, model: Optional[str] = None) -> Optional[str]:
        """
        Gets a text completion from the Ollama API.

        Args:
            prompt: The full prompt to send to the language model.
            model: The specific model to use (e.g., 'llama3:latest'). If None, uses the default from config.

        Returns:
            The generated text response as a string, or None if an error occurred.
        """
        if not model:
            model = self.config.LLM_MODEL

        logging.info(f"Sending prompt to Ollama model '{model}'...")

        payload: Dict[str, Any] = {
            "model": model,
            "prompt": prompt,
            "stream": False, # We will handle the full response at once for simplicity
            "options": {
                "temperature": 0.8,
                "top_p": 0.9,
                "num_ctx": 4096 # Context window size
            }
        }

        try:
            async with httpx.AsyncClient(timeout=300.0) as client: # 5 minute timeout for long responses
                response = await client.post(self.api_url, json=payload)

                if response.status_code == 200:
                    response_data = response.json()
                    logging.info(f"Successfully received response from Ollama.")
                    return response_data.get("response", "").strip()
                else:
                    logging.error(f"Error from Ollama API: Status {response.status_code} - {response.text}")
                    return None

        except httpx.RequestError as e:
            logging.error(f"Could not connect to Ollama API at {self.api_url}. Is the server running? Error: {e}")
            return None
        except Exception as e:
            logging.error(f"An unexpected error occurred while communicating with Ollama: {e}")
            return None