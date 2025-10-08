import httpx
import logging
import os
import uuid

class ChatterboxClient:
    """
    Client for interacting with a Chatterbox-like voice generation service.
    For this project, we will simulate this by calling the chatterbox library directly
    as a local function, since it's a Python library, not a server.
    """
    def __init__(self, url: str): # URL is kept for consistency but not used
        self.logger = logging.getLogger(__name__)
        # In a real-world scenario with a separate server, you'd use the URL.
        # Here, we'll import the library directly.
        try:
            from chatterbox import Chatter, Voice
            self.Chatter = Chatter
            self.Voice = Voice
            self.engine_ready = True
        except ImportError:
            self.logger.warning("Chatterbox library not found. Voice generation will be disabled.")
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
            return f"Error: Reference voice file '{character_name}.wav' not found."

        try:
            # Create a new Chatter instance
            chatter = self.Chatter()

            # Create a voice object from the reference file
            voice = self.Voice(path=reference_voice_path)

            # Generate the audio
            audio_file_path = os.path.join("data", "voices", "generated", f"{character_name}_speech_{uuid.uuid4()}.wav")

            # Ensure the output directory exists
            os.makedirs(os.path.dirname(audio_file_path), exist_ok=True)

            chatter.say(text, voice=voice, path=audio_file_path)

            self.logger.info(f"Successfully generated voice file at {audio_file_path}")
            return audio_file_path

        except Exception as e:
            self.logger.error(f"An unexpected error occurred during voice generation: {e}")
            return "Error: An unexpected error occurred while generating the voice."