# src/core/ai_services/xtts_client.py
# Client for interacting with a self-hosted XTTSv2 instance for voice generation.

import httpx
import logging
from typing import Optional

from src.config import Config

class XTTSClient:
    """
    Handles all communication with the local XTTSv2 TTS service.
    """
    def __init__(self, config: Config):
        self.config = config
        self.api_url = f"{self.config.XTTS_API_URL}/tts"
        logging.info("XTTSClient initialized.")

    async def generate_speech(self, text: str, speaker_wav_path: str) -> Optional[bytes]:
        """
        Generates speech audio from text using the XTTS API and a speaker WAV file.

        Args:
            text: The text to convert to speech.
            speaker_wav_path: The local file path to the .wav file for the speaker's voice.

        Returns:
            The raw audio data as bytes if successful, otherwise None.
        """
        logging.info(f"Requesting speech generation with speaker '{speaker_wav_path}'...")

        try:
            with open(speaker_wav_path, "rb") as wav_file:
                files = {'speaker_wav': ('speaker.wav', wav_file, 'audio/wav')}
                data = {'text': text, 'language': 'en'}

                async with httpx.AsyncClient(timeout=180.0) as client: # 3 minute timeout
                    response = await client.post(self.api_url, data=data, files=files)

                    if response.status_code == 200:
                        logging.info(f"Successfully generated speech for speaker '{speaker_wav_path}'.")
                        return await response.aread()
                    else:
                        logging.error(f"Error from XTTS API: Status {response.status_code} - {response.text}")
                        return None

        except FileNotFoundError:
            logging.error(f"Could not find speaker WAV file at path: {speaker_wav_path}")
            return None
        except httpx.RequestError as e:
            logging.error(f"Could not connect to XTTS API at {self.api_url}. Is the server running? Error: {e}")
            return None
        except Exception as e:
            logging.error(f"An unexpected error occurred during speech generation: {e}")
            return None