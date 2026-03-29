import logging
import os
import uuid
from typing import Optional
import asyncio

# We assume the user has installed the chatterbox-ai library via the setup script.
try:
    from chatterbox import Chatterbox
    CHATTERBOX_INSTALLED = True
except ImportError:
    CHATTERBOX_INSTALLED = False
    class Chatterbox:
        def __init__(self, *args, **kwargs):
            logging.getLogger(__name__).critical("The 'chatterbox-ai' library is not installed. Voice features will be disabled. Please run SETUP_THE_WORLD.py again.")
        def generate(self, *args, **kwargs):
            raise NotImplementedError("Chatterbox is not installed.")

class ChatterboxClient:
    """
    Client for interacting with the Chatterbox (XTTS) voice generation library.
    """
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.engine = None
        if CHATTERBOX_INSTALLED:
            try:
                # Initialize the Chatterbox engine.
                self.engine = Chatterbox(use_gpu=True)
                self.logger.info("Chatterbox (XTTS) client initialized successfully.")
            except Exception as e:
                self.logger.critical(f"Failed to initialize Chatterbox library: {e}. Voice generation will be disabled.")
                self.engine = None
        else:
            self.engine = Chatterbox()

    async def generate_voice(self, text: str, voice_reference_wav: str, character_name: str) -> Optional[str]:
        """
        Generates a voice clip from text using a reference audio file.
        """
        if not self.engine or not CHATTERBOX_INSTALLED:
            self.logger.error("Chatterbox engine not available. Cannot generate voice.")
            return None

        voice_path = os.path.join("data/voices", voice_reference_wav)
        if not os.path.exists(voice_path):
            self.logger.error(f"Voice reference file not found for {character_name}: {voice_path}")
            return None

        self.logger.info(f"Generating voice for {character_name}...")

        try:
            output_dir = "voice_clips"
            os.makedirs(output_dir, exist_ok=True)
            output_filename = f"{character_name}_{uuid.uuid4()}.wav"
            output_path = os.path.join(output_dir, output_filename)

            loop = asyncio.get_running_loop()
            await loop.run_in_executor(
                None,
                self.engine.generate,
                text,
                voice_path,
                output_path
            )

            self.logger.info(f"Voice clip for {character_name} saved to {output_path}")
            return output_path

        except NotImplementedError:
             self.logger.error("Cannot generate voice: Chatterbox library is not installed.")
             return None
        except Exception as e:
            self.logger.error(f"An unexpected error occurred during voice generation for {character_name}: {e}", exc_info=True)
            return None