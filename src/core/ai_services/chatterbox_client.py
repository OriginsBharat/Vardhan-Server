# src/core/ai_services/chatterbox_client.py
# Client for interacting with the Chatterbox voice cloning engine.

import logging
import os
from typing import Optional
from chatterbox import Chatterbox

# Create a single, reusable instance of Chatterbox
# This will download the model on its first run.
try:
    chatterbox_model = Chatterbox()
except Exception as e:
    logging.error(f"Failed to initialize Chatterbox model. Voice generation will be disabled. Error: {e}")
    chatterbox_model = None

class ChatterboxClient:
    """
    Handles all communication with the Chatterbox TTS service.
    """
    def __init__(self):
        self.output_dir = "data/tts_cache"
        os.makedirs(self.output_dir, exist_ok=True)
        logging.info("ChatterboxClient initialized.")

    def generate_speech(self, text: str, speaker_wav_path: str) -> Optional[str]:
        """
        Generates speech audio from text using the Chatterbox engine and a speaker WAV file.

        Args:
            text: The text to convert to speech.
            speaker_wav_path: The local file path to the .wav file for the speaker's voice.

        Returns:
            The file path to the generated .wav audio file if successful, otherwise None.
        """
        if not chatterbox_model:
            logging.error("Chatterbox model is not available. Cannot generate speech.")
            return None

        if not os.path.exists(speaker_wav_path):
            logging.error(f"Speaker WAV file not found at: {speaker_wav_path}")
            return None

        logging.info(f"Generating speech for speaker '{speaker_wav_path}'...")

        try:
            # Define a unique output path for the generated audio
            output_filename = f"{os.path.basename(speaker_wav_path).split('.')[0]}_{hash(text)}.wav"
            output_path = os.path.join(self.output_dir, output_filename)

            # Generate the speech and save it to the file
            chatterbox_model.generate(
                text=text,
                speaker=speaker_wav_path,
                output_path=output_path
            )

            logging.info(f"Successfully generated speech and saved to {output_path}")
            return output_path

        except Exception as e:
            logging.error(f"An unexpected error occurred during Chatterbox speech generation: {e}")
            return None