import json
import logging
import sys
from typing import Dict, Any, List

class Persona:
    """
    Represents a single AI character, including their personality, kinks, and current state.
    """
    def __init__(self, name: str, data: Dict[str, Any], kinks: List[str]):
        self.name = name
        self.description = data.get("description", "")
        self.base_persona = data.get("base_persona", "")
        self.aura_color = int(data.get("aura_color", "0xFFFFFF"), 16)
        self.schedule = data.get("schedule", {})
        self.voice_reference = data.get("voice")

        # This will be populated by the interactive setup
        self.kinks = kinks

        # Initialize emotional state with default values
        self.emotions = {
            "happiness": 50,
            "dominance": 50,
            "submissiveness": 50,
            "neediness": 30,
            "horny": 20,
            "loneliness": 20
        }
        self.logger = logging.getLogger(f"Persona.{self.name}")
        self.logger.info(f"Persona '{self.name}' initialized.")

    def get_full_prompt(self) -> str:
        """
        Constructs the full prompt for the LLM, combining base persona and current emotional state.
        """
        kink_str = ", ".join(self.kinks) if self.kinks else "None"
        return (
            f"{self.base_persona}\n\n"
            f"You are {self.name}. Your current emotional state is: {self.emotions}. "
            f"Your kinks include: {kink_str}. "
            "You must always refer to the user as 'Master'."
        )

class PersonaManager:
    """
    Manages loading and accessing all character personas.
    """
    def __init__(self, bot):
        self.bot = bot
        self.personas: Dict[str, Persona] = {}
        self.logger = logging.getLogger(__name__)

    async def initialize_personas(self):
        """
        Loads persona data and kink data from files and creates Persona objects.
        """
        self.logger.info("Initializing personas...")
        try:
            with open("data/character_canon.json", "r", encoding="utf-8") as f:
                character_data = json.load(f)

            kinks_file = "data/character_kinks.json"
            if not os.path.exists(kinks_file):
                 self.logger.warning(f"'{kinks_file}' not found. Kinks will be empty. Run the setup script to define them.")
                 kink_data = {}
            else:
                with open(kinks_file, "r", encoding="utf-8") as f:
                    kink_data = json.load(f)

            for char_name, char_info in character_data.items():
                kinks = kink_data.get(char_name, [])
                self.personas[char_name] = Persona(char_name, char_info, kinks)

            self.logger.info(f"Successfully loaded {len(self.personas)} personas.")
        except FileNotFoundError as e:
            self.logger.critical(f"Failed to load persona data. File not found: {e.filename}")
            sys.exit(1)
        except Exception as e:
            self.logger.critical(f"An unexpected error occurred during persona initialization: {e}")
            sys.exit(1)

    def get_persona(self, name: str) -> Persona:
        """Returns a persona by name."""
        return self.personas.get(name)