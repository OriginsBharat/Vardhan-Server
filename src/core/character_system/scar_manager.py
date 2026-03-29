import sqlite3
import logging
from typing import List

class ScarManager:
    """Manages the psychological scars of the characters."""
    def __init__(self, bot):
        self.bot = bot
        self.db_path = "data/world_data.db"
        self.logger = logging.getLogger(__name__)
        self._init_db()

    def _init_db(self):
        """Initializes the database table for scars."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS scars (
                        character_name TEXT NOT NULL,
                        scar_description TEXT NOT NULL,
                        PRIMARY KEY (character_name, scar_description)
                    )
                """)
                conn.commit()
            self.logger.info("Psychological scar system database table initialized.")
        except sqlite3.Error as e:
            self.logger.error(f"Database error in ScarManager init: {e}", exc_info=True)

    def add_scar(self, character_name: str, scar_description: str):
        """Adds a new psychological scar to a character."""
        try:
            # First, update the persona object in memory
            persona = self.bot.persona_manager.get_persona(character_name)
            if persona and scar_description not in persona.scars:
                persona.scars.append(scar_description)

                # Then, persist it to the database
                with sqlite3.connect(self.db_path) as conn:
                    cursor = conn.cursor()
                    cursor.execute(
                        "INSERT OR IGNORE INTO scars (character_name, scar_description) VALUES (?, ?)",
                        (character_name, scar_description)
                    )
                    conn.commit()
                self.logger.info(f"Added new scar to {character_name}: '{scar_description}'")
                self.bot.narrative_manager.log_event(
                    f"{character_name} has been inflicted with a new psychological scar: '{scar_description}'. Their soul is forever changed.",
                    level="major"
                )
        except sqlite3.Error as e:
            self.logger.error(f"Failed to add scar for {character_name}: {e}")

    def get_scars(self, character_name: str) -> List[str]:
        """Retrieves all scars for a character from the database."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT scar_description FROM scars WHERE character_name = ?", (character_name,))
                results = cursor.fetchall()
                return [row[0] for row in results]
        except sqlite3.Error as e:
            self.logger.error(f"Failed to retrieve scars for {character_name}: {e}")
            return []