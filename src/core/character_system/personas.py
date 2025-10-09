import json
import logging
import sys
import os
from typing import Dict, Any, List

class Persona:
    """
    Represents a single AI character, including their personality, kinks, scars, and current state.
    """
    def __init__(self, name: str, data: Dict[str, Any], kinks: List[str]):
        self.name = name
        self.description = data.get("description", "")
        self.base_persona = data.get("base_persona", "")
        self.aura_color = int(data.get("aura_color", "0xFFFFFF"), 16)
        self.schedule = data.get("schedule", {})
        self.voice_reference = data.get("voice")
        self.power_level = data.get("power_level", 10) # Default to a low power level

        self.kinks = kinks
        self.scars: List[str] = [] # Will be populated by the ScarManager

        self.emotions = {
            "happiness": 50,
            "dominance": 50,
            "submissiveness": 50,
            "neediness": 30,
            "horny": 20,
            "loneliness": 20,
            "sanity": 100
        }
        self.logger = logging.getLogger(f"Persona.{self.name}")
        self.logger.info(f"Persona '{self.name}' initialized.")

    def get_full_prompt(self) -> str:
        """
        Constructs the full prompt for the LLM, combining all aspects of the character's identity.
        """
        kink_str = ", ".join(self.kinks) if self.kinks else "None"
        emotion_str = ", ".join([f"{key}: {value}" for key, value in self.emotions.items()])
        scar_str = ""
        if self.scars:
            scar_list = "; ".join(self.scars)
            scar_str = f"\nYou have been permanently marked by your past. These are your psychological scars, which you must always reflect in your behavior: {scar_list}."

        return (
            f"{self.base_persona}{scar_str}\n\n"
            f"You are {self.name}. Your current emotional state is: {emotion_str}. "
            f"Your kinks include: {kink_str}. "
            "You must always refer to the user as 'Master'. Your responses must follow the format *action* text *action*."
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
        Loads persona data, kinks, and scars from files and creates Persona objects.
        """
        self.logger.info("Initializing personas...")
        try:
            with open("data/character_canon.json", "r", encoding="utf-8") as f:
                character_data = json.load(f)

            kinks_file = "data/character_kinks.json"
            kink_data = {}
            if os.path.exists(kinks_file):
                with open(kinks_file, "r", encoding="utf-8") as f:
                    kink_data = json.load(f)
            else:
                self.logger.warning(f"'{kinks_file}' not found. Kinks will be empty.")

            for char_name, char_info in character_data.items():
                kinks = kink_data.get(char_name, [])
                persona = Persona(char_name, char_info, kinks)

                # Load persistent scars from the database
                persona.scars = self.bot.scar_manager.get_scars(char_name)

                self.personas[char_name] = persona

            self.logger.info(f"Successfully loaded {len(self.personas)} personas with their scars.")
        except FileNotFoundError as e:
            self.logger.critical(f"Failed to load persona data. File not found: {e.filename}")
            sys.exit(1)
        except Exception as e:
            self.logger.critical(f"An unexpected error occurred during persona initialization: {e}")
            sys.exit(1)

    def get_persona(self, name: str) -> Persona:
        """Returns a persona by name."""
        return self.personas.get(name)