# src/config.py
# Handles loading and validation of all configuration variables from the .env file.

import os
from dotenv import load_dotenv
import logging

class Config:
    """
    A class to hold all configuration variables, loaded from a .env file.
    It provides a single, validated source of truth for all secrets and settings.
    """
    def __init__(self):
        # Explicitly define the path to the .env file in the project root.
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        dotenv_path = os.path.join(project_root, '.env')

        if not os.path.exists(dotenv_path):
             # This check is primarily for robustness; the setup script should create the file.
             raise ValueError(f"CRITICAL ERROR: .env file not found at path: {dotenv_path}")

        load_dotenv(dotenv_path=dotenv_path)

        # --- Discord Secrets ---
        self.DISCORD_BOT_TOKEN: str = self._get_env("DISCORD_BOT_TOKEN")
        self.DISCORD_GUILD_ID: int = int(self._get_env("DISCORD_GUILD_ID"))
        self.USER_ID: int = int(self._get_env("USER_ID"))

        # --- Local AI Service Paths & URLs ---
        self.COMFYUI_PATH: str = self._get_env("COMFYUI_PATH")
        self.OLLAMA_API_URL: str = self._get_env("OLLAMA_API_URL", "http://127.0.0.1:11434")
        self.COMFYUI_API_URL: str = self._get_env("COMFYUI_API_URL", "http://127.0.0.1:8188")

        # --- Cloud Memory (Pinecone) ---
        self.PINECONE_API_KEY: str = self._get_env("PINECONE_API_KEY")
        self.PINECONE_INDEX_HOST: str = self._get_env("PINECONE_INDEX_HOST")

        logging.info("Configuration loaded and validated.")

    def _get_env(self, key: str, default: str = None) -> str:
        """
        Retrieves an environment variable, raising an error if it's not found and no default is provided.
        """
        value = os.getenv(key, default)
        if value is None:
            raise ValueError(f"CRITICAL ERROR: Missing required environment variable '{key}'. Please check your .env file.")

        if "YOUR_" in value or "C:\\Path\\To\\" in value:
            raise ValueError(f"CRITICAL ERROR: Placeholder value for '{key}' found. Please fill in your actual credentials in the .env file.")

        return value