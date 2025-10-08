import json
import logging
from typing import Dict, Any

class Persona:
    """
    Represents a single AI character, including their personality, kinks, and current state.
    """
    def __init__(self, name: str, data: Dict[str, Any], kinks: list):
        self.name = name
        self.description = data.get("description", "")
        self.base_persona = data.get("base_persona", "")
        self.aura_color = int(data.get("aura_color", "0xFFFFFF"), 16)
        self.kinks = kinks
        self.schedule = data.get("schedule", {})

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
        # This is a simplified prompt, can be made more complex
        return f"{self.base_persona}\n\nYour name is {self.name}. Right now you are feeling: {self.emotions}. Your kinks are: {', '.join(self.kinks)}. You must refer to the user as 'Master'."

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
            # Load base character data from our "canon"
            with open("data/character_canon.json", "r") as f:
                character_data = json.load(f)

            # Load the kinks defined by the user during setup
            with open("data/character_kinks.json", "r") as f:
                kink_data = json.load(f)

            for char_name, char_info in character_data.items():
                kinks = kink_data.get(char_name, [])
                self.personas[char_name] = Persona(char_name, char_info, kinks)

            self.logger.info(f"Successfully loaded {len(self.personas)} personas.")
        except FileNotFoundError as e:
            self.logger.error(f"Failed to load persona data. File not found: {e.filename}")
            print(f"FATAL ERROR: Could not find required data file {e.filename}. Please ensure it exists.")
            sys.exit(1)
        except Exception as e:
            self.logger.error(f"An unexpected error occurred during persona initialization: {e}")
            sys.exit(1)

    def get_persona(self, name: str) -> Persona:
        """Returns a persona by name."""
        return self.personas.get(name)