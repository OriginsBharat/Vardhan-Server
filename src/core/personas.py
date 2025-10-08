import json
from pathlib import Path
import time

class Persona:
    """Represents a single character's personality, lore, and state."""
    def __init__(self, name, personality_summary, voice_ref, aura_color, kinks=None):
        self.name = name
        self.personality_summary = personality_summary
        self.voice_ref = voice_ref
        self.aura_color = int(aura_color, 16) # Convert hex string to int for Discord
        self.kinks = kinks if kinks else []

        # Emotional state sliders
        self.emotions = {
            "happiness": 50,
            "sadness": 10,
            "anger": 10,
            "lust": 20,
            "dominance": 50,
            "submission": 30,
            "loneliness": 20,
            "sanity": 100
        }

        # Status for Regeneration and Gilded Cage systems
        self.status = "Healthy"  # Healthy, Injured, Regenerating, InServitude
        self.injuries = {}  # e.g., {'left_arm': 'severed'}
        self.regeneration_end_time = None
        self.servitude_owner = None

        # Faction/Cult status
        self.faction = None
        self.is_cult_leader = False

    def __repr__(self):
        return f"Persona(name={self.name}, status={self.status})"

    def adjust_emotion(self, emotion, value):
        """Adjusts a specific emotion by a value, clamping between 0 and 100."""
        emotion = emotion.lower()
        if emotion in self.emotions:
            current_value = self.emotions[emotion]
            new_value = max(0, min(100, current_value + value))
            self.emotions[emotion] = new_value
            print(f"[{emotion.capitalize()}] {self.name}'s {emotion} changed by {value:+}. New value: {self.emotions[emotion]}")
        else:
            print(f"[ERROR] Tried to adjust non-existent emotion '{emotion}' for {self.name}")

    def inflict_injury(self, part, description):
        """Inflicts an injury on a body part. This is for NSFW regeneration scenes."""
        self.injuries[part] = description
        self.status = "Injured"
        print(f"[Regen] {self.name}'s {part} is now {description}.")

    def heal_all_injuries(self):
        """Heals all injuries, representing the end of a scene."""
        self.injuries = {}
        if self.status == "Injured":
            self.status = "Healthy"
        print(f"[Regen] {self.name} has fully regenerated.")

    def set_regenerating(self, duration_seconds):
        """Puts the character in a temporary 'dead' state after a duel."""
        self.status = "Regenerating"
        self.regeneration_end_time = time.time() + duration_seconds
        print(f"[Regen] {self.name} has been incapacitated. Will regenerate in {duration_seconds} seconds.")

    def check_regeneration(self):
        """Checks if the regeneration period is over."""
        if self.status == "Regenerating" and self.regeneration_end_time and time.time() > self.regeneration_end_time:
            self.status = "Healthy"
            self.regeneration_end_time = None
            print(f"[Regen] {self.name} has finished regenerating and is back.")
            return True
        return False

class PersonaManager:
    """Manages all character personas in the world."""
    def __init__(self, kink_file_path='data/character_kinks.json'):
        self.personas = {}
        self.kink_file_path = Path(kink_file_path)
        self._load_base_personas()
        self._load_kinks()

    def _load_base_personas(self):
        """Loads the foundational personas from the story canon."""
        base_personas = [
            Persona("Maya", "Yashvardhan's sharp, comforting AI companion, born from his psyche. Acts as world admin.", "Tashi (ASMR)", "0xEE82EE"),
            Persona("Eka", "The 'Dom MILF'. A dominant, motherly, and possessive secretary/butler.", "Akeno Himejima", "0xFF0000"),
            Persona("Dvi", "The Silent Guardian. A stoic and ruthless warrior with a sissified femboy persona towards his Master.", "Marulk", "0x808080"),
            Persona("Tri", "The 'Loli Diplomat'. Appears cute and innocent but is a master manipulator.", "Rem", "0xFFC0CB"),
            Persona("Chatur", "The Architect. Meticulous and calm, obsessed with planning, with a sissified femboy persona towards his Master.", "Ruka Urushibara", "0x0000FF"),
            Persona("Panch", "The Healer. Gentle, kind, and compassionate, with a sissified femboy persona towards his Master.", "Ken Kaneki", "0x008000"),
            Persona("Shash", "The Economist. Confident, teasing, and loves wealth.", "Yukinoshita Yukino", "0xFFD700"),
            Persona("Sapt", "The Spy. Fierce, aggressive, and operates from the shadows.", "Yoruichi Shihouin", "0x8B008B"),
            Persona("Asht", "The Artist. Flamboyant, dramatic, and passionate, with a sissified femboy persona towards his Master.", "Howl", "0xFFA500"),
            Persona("Nav", "The Astronomer. A dreamy, naive, and genius young woman, whose youth makes her vulnerable.", "Miku Nakano", "0xDA70D6"),
            Persona("Dash", "The Manipulator. Appears sweet but is dangerously manipulative, with a sissified femboy persona towards his Master.", "Juuzou Suzuya", "0xFFFF00"),
        ]
        for p in base_personas:
            self.personas[p.name.lower()] = p

    def _load_kinks(self):
        """Loads the user-defined kinks from the JSON file and merges them."""
        if not self.kink_file_path.exists():
            return
        try:
            with open(self.kink_file_path, 'r') as f:
                kink_data = json.load(f)
            for name, kinks in kink_data.items():
                if name.lower() in self.personas:
                    self.personas[name.lower()].kinks = kinks
        except (IOError, json.JSONDecodeError) as e:
            print(f"[ERROR] Could not load or parse kink file: {e}")

    def get_persona(self, name):
        """Gets a persona by name (case-insensitive)."""
        return self.personas.get(name.lower())

    def get_all_personas(self):
        """Returns a list of all persona objects."""
        return list(self.personas.values())