import logging
import os
import uuid
import asyncio

class ChatterboxClient:
    """
    Client for interacting with the Chatterbox voice generation library.
    """
    def __init__(self, url: str):
        self.logger = logging.getLogger(__name__)
        # The URL is kept for consistency with other clients but is not used
        # as Chatterbox is a library, not a separate server.
        try:
            from chatterbox import Chatter, Voice
            self.Chatter = Chatter
            self.Voice = Voice
            self.engine_ready = True
            self.logger.info("Chatterbox voice engine initialized successfully.")
        except ImportError:
            self.logger.warning("Chatterbox library not found. Voice generation will be disabled. Please run 'pip install chatterbox-ai'.")
            self.engine_ready = False

    async def generate_voice(self, text: str, character_name: str) -> str:
        """
        Generates spoken audio from text using a reference voice.

        Args:
            text: The text to be converted to speech.
            character_name: The name of the character, used to find the reference voice file.

        Returns:
            The file path of the generated audio file, or an error message.
        """
        if not self.engine_ready:
            return "Error: Chatterbox voice engine is not installed."

        self.logger.info(f"Generating voice for {character_name}...")

        reference_voice_path = os.path.join("data", "voices", f"{character_name}.wav")
        if not os.path.exists(reference_voice_path):
            self.logger.error(f"Reference voice for {character_name} not found at {reference_voice_path}")
            return f"Error: Reference voice file '{character_name}.wav' not found in data/voices/."

        try:
            # Chatterbox operations can be blocking, run them in a separate thread
            # to avoid blocking the bot's asynchronous event loop.
            loop = asyncio.get_running_loop()

            # Define the synchronous part of the work
            def _generate():
                chatter = self.Chatter()
                voice = self.Voice(path=reference_voice_path)

                output_dir = os.path.join("data", "voices", "generated")
                os.makedirs(output_dir, exist_ok=True)

                audio_file_path = os.path.join(output_dir, f"{character_name}_speech_{uuid.uuid4()}.wav")
                chatter.say(text, voice=voice, path=audio_file_path)
                return audio_file_path

            # Run the synchronous function in a default executor (thread pool)
            audio_file_path = await loop.run_in_executor(None, _generate)

            self.logger.info(f"Successfully generated voice file at {audio_file_path}")
            return audio_file_path

        except Exception as e:
            self.logger.error(f"An unexpected error occurred during voice generation for {character_name}: {e}")
            return "Error: An unexpected error occurred while generating the voice."