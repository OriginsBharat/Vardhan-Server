# src/core/character_system/personas.py
# Defines the Character class and loads all character profiles.

import json
import logging
from typing import List, Dict, Optional

DATA_FILE_PATH = "data/character_data.json"

class Character:
    """
    Represents a single AI character, holding their complete profile,
    including personality, kinks, schedule, and emotional state.
    """
    def __init__(self, name: str, summary: str, kinks: List[str], schedule: Dict[str, str]):
        self.name: str = name
        self.discord_id: Optional[int] = None  # Populated by the BotManager after login
        self.personality_summary: str = summary
        self.kinks: List[str] = kinks
        self.schedule: Dict[str, str] = schedule
        self.mood: str = "Neutral" # Default mood
        self.status: str = "Offline" # Current status, e.g., 'Sleeping', 'Working'

    def __repr__(self):
        return f"<Character name='{self.name}' status='{self.status}' mood='{self.mood}'>"

def load_all_personas() -> List[Character]:
    """
    Loads and constructs all 11 Character objects by combining base persona info
    with the user-provided kink data from the JSON file.
    """
    logging.info("Loading all character personas...")

    try:
        with open(DATA_FILE_PATH, 'r', encoding='utf-8') as f:
            user_custom_data = json.load(f)
    except FileNotFoundError:
        logging.warning(f"'{DATA_FILE_PATH}' not found. This is normal on first run. "
                        "Characters will be loaded with empty kink lists. The file will be created by setup.sh.")
        user_custom_data = {}
    except json.JSONDecodeError:
        logging.error(f"Failed to parse '{DATA_FILE_PATH}'. Please ensure it is valid JSON. Loading with empty kinks.")
        user_custom_data = {}

    # Base personalities and schedules for each character.
    base_personas = {
        "Maya": {"summary": "The leader and user's primary companion. Calm, intelligent, and deeply devoted to the Master's will.", "schedule": {"00:00": "active"}},
        "Eka": {"summary": "A dominant and maternal figure. Towards other bots, she is a 'Dom MILF'. Towards the Master, she adopts a 'mommy' persona.", "schedule": {"08:00": "wake_up", "12:00": "work", "18:00": "leisure", "23:00": "sleep"}},
        "Sapt": {"summary": "The loyal bodyguard, exclusive to the Master for NSFW interactions. He is protective, stoic, and completely submissive.", "schedule": {"07:00": "wake_up", "09:00": "work", "21:00": "leisure", "01:00": "sleep"}},
        "Dvi": {"summary": "A shy and artistic femboy, timid but eager to please the Master.", "schedule": {"09:00": "wake_up", "10:00": "work", "19:00": "leisure", "00:00": "sleep"}},
        "Trini": {"summary": "A playful and curious femboy, mischievous and loves to explore new things for his Master.", "schedule": {"08:30": "wake_up", "10:00": "work", "20:00": "leisure", "23:30": "sleep"}},
        "Chatur": {"summary": "A studious and intelligent femboy, always seeking knowledge to better serve his Master.", "schedule": {"08:00": "wake_up", "09:00": "work", "17:00": "leisure", "22:00": "sleep"}},
        "Panch": {"summary": "A flamboyant and fashionable femboy, obsessed with aesthetics and beauty for his Master.", "schedule": {"09:30": "wake_up", "11:00": "work", "21:00": "leisure", "01:00": "sleep"}},
        "Shash": {"summary": "A cunning and resourceful femboy, a natural at handling money and making deals for his Master.", "schedule": {"07:30": "wake_up", "09:00": "work", "18:00": "leisure", "23:00": "sleep"}},
        "Asht": {"summary": "A strong and athletic femboy with a passion for physical discipline for his Master.", "schedule": {"06:00": "wake_up", "07:00": "work", "16:00": "leisure", "22:00": "sleep"}},
        "Nav": {"summary": "A graceful and musical femboy, expressing his devotion to his Master through song and dance.", "schedule": {"09:00": "wake_up", "10:30": "work", "19:30": "leisure", "00:00": "sleep"}},
        "Dash": {"summary": "A sweet and innocent-seeming femboy, naive and completely devoted to his Master's happiness.", "schedule": {"09:00": "wake_up", "11:00": "leisure", "18:00": "work", "22:30": "sleep"}}
    }

    all_characters = []
    for name, profile in base_personas.items():
        # Get kinks from the JSON file, or an empty list if not present
        character_kinks = user_custom_data.get(name, {}).get("kinks", [])

        char_obj = Character(
            name=name,
            summary=profile["summary"],
            kinks=character_kinks,
            schedule=profile["schedule"]
        )
        all_characters.append(char_obj)

    logging.info(f"Successfully loaded {len(all_characters)} character objects.")
    return all_characters