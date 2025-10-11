import json
import logging
from typing import Dict, Any, List
import os

class Persona:
    """
    Represents a single AI character, including their personality and current state.
    """
    def __init__(self, name: str, canon_data: Dict[str, Any]):
        self.name = name
        self.gender = canon_data.get("gender")
        self.base_persona = canon_data.get("base_persona")
        self.nsfw_persona_user = canon_data.get("nsfw_persona_user")
        self.nsfw_persona_general = canon_data.get("nsfw_persona_general")
        self.aura_color = int(canon_data.get("aura_color", "0xFFFFFF").replace("#", "0x"), 16)

        self.emotions = {
            "neediness": 0.2, "arousal": 0.1, "flirting": 0.5, "anger": 0.1, "caring": 0.7
        }
        self.logger = logging.getLogger(f"Persona.{self.name}")
        self.logger.info(f"Persona '{self.name}' initialized in memory.")

    def get_full_prompt(self, persona_type: str = "base", for_user: bool = False) -> str:
        """
        Constructs the full system prompt for the LLM based on persona and emotional state.
        """
        if persona_type == "nsfw":
            persona_text = self.nsfw_persona_user if for_user else self.nsfw_persona_general
        else:
            persona_text = self.base_persona

        emotion_str = " ".join([f"Your current {emotion} level is {value:.2f}." for emotion, value in self.emotions.items()])
        # Kinks will be added later when the kink file is integrated
        return f"{persona_text}\n\nYour current emotional state is: {emotion_str}"

class PersonaManager:
    """
    Manages loading and accessing all character personas.
    """
    def __init__(self):
        self.personas: Dict[str, Persona] = {}
        self.logger = logging.getLogger(__name__)
        self._initialize_personas()

    def _initialize_personas(self):
        """Loads all persona data from the canon file."""
        self.logger.info("Initializing PersonaManager for the full Pantheon...")
        try:
            # Construct an absolute path to the data file
            script_dir = os.path.dirname(__file__)
            project_root = os.path.abspath(os.path.join(script_dir, '..', '..', '..'))
            canon_path = os.path.join(project_root, 'data', 'character_canon.json')

            with open(canon_path, "r", encoding="utf-8") as f:
                character_data = json.load(f)

            for name, data in character_data.items():
                self.personas[name] = Persona(name, data)

            self.logger.info(f"Successfully loaded {len(self.personas)} personas.")
        except (FileNotFoundError, ValueError) as e:
            self.logger.critical(f"Failed to load persona data: {e}", exc_info=True)
            raise e

    def get_persona(self, name: str) -> Persona:
        """Returns a persona by name."""
        return self.personas.get(name)

    def get_all_personas(self) -> List[Persona]:
        """Returns a list of all persona objects."""
        return list(self.personas.values())