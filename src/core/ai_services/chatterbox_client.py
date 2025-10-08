import chatterbox
from pathlib import Path
import tempfile

class ChatterboxClient:
    """
    A client for generating voice using the Chatterbox library.
    This client uses local voice samples for cloning.
    """
    def __init__(self, voice_dir="data/voices"):
        self.voice_dir = Path(voice_dir)
        self.voice_dir.mkdir(exist_ok=True)

    def generate_voice(self, character_name, text_to_speak):
        """
        Generates voice audio for a character.

        Args:
            character_name (str): The name of the character whose voice to use.
            text_to_speak (str): The text to be spoken.

        Returns:
            str: The file path to the generated audio file, or None on failure.
        """
        reference_wav = self.voice_dir / f"{character_name}.wav"

        if not reference_wav.exists():
            print(f"[ERROR] Voice reference file not found for {character_name} at {reference_wav}")
            return None

        try:
            # Create a temporary file to save the output audio
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_file:
                output_path = tmp_file.name

            # Generate the audio using chatterbox
            chatterbox.generate(
                text=text_to_speak,
                source_wav=str(reference_wav),
                target_wav=output_path
            )

            print(f"[VOICE] Generated voice for {character_name} at {output_path}")
            return output_path

        except Exception as e:
            print(f"[ERROR] Chatterbox voice generation failed for {character_name}: {e}")
            return None