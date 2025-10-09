import sqlite3
import logging
import uuid
from typing import Optional, Dict, Any

class ArenaManager:
    """Manages duels and outcomes in the Arena of Souls."""
    def __init__(self, bot):
        self.bot = bot
        self.db_path = "data/world_data.db"
        self.logger = logging.getLogger(__name__)
        self._init_db()

    def _init_db(self):
        """Initializes the database table for duels."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS duels (
                        duel_id TEXT PRIMARY KEY,
                        challenger_name TEXT NOT NULL,
                        opponent_name TEXT NOT NULL,
                        status TEXT NOT NULL DEFAULT 'pending', -- 'pending', 'active', 'finished'
                        winner_name TEXT,
                        loser_name TEXT
                    )
                """)
                conn.commit()
            self.logger.info("Arena of Souls database table initialized.")
        except sqlite3.Error as e:
            self.logger.error(f"Database error in ArenaManager init: {e}", exc_info=True)

    def create_duel(self, challenger: str, opponent: str) -> Optional[str]:
        """Creates a new duel challenge."""
        duel_id = str(uuid.uuid4())[:8]
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO duels (duel_id, challenger_name, opponent_name) VALUES (?, ?, ?)",
                    (duel_id, challenger, opponent)
                )
                conn.commit()
            self.logger.info(f"New duel challenge created: {duel_id} ({challenger} vs {opponent})")
            return duel_id
        except sqlite3.Error as e:
            self.logger.error(f"Failed to create duel: {e}")
            return None

    def get_duel(self, duel_id: str) -> Optional[Dict[str, Any]]:
        """Retrieves a duel by its ID."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM duels WHERE duel_id = ?", (duel_id,))
                result = cursor.fetchone()
                return dict(result) if result else None
        except sqlite3.Error as e:
            self.logger.error(f"Failed to get duel {duel_id}: {e}")
            return None

    def resolve_duel(self, duel_id: str, winner: str, loser: str):
        """Resolves a duel, sets the winner/loser, and inflicts a scar."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "UPDATE duels SET status = 'finished', winner_name = ?, loser_name = ? WHERE duel_id = ?",
                    (winner, loser, duel_id)
                )
                conn.commit()

            self.logger.info(f"Duel {duel_id} resolved. Winner: {winner}, Loser: {loser}.")

            # Inflict the scar of humiliation
            self.bot.scar_manager.add_scar(
                character_name=loser,
                scar_description=f"Publicly defeated and humiliated in a duel by {winner}."
            )

            # Log the event for the Master's Journal
            self.bot.narrative_manager.log_event(
                f"{winner} defeated {loser} in a brutal duel in the Arena of Souls. The humiliation has left a permanent scar on {loser}.",
                level="critical"
            )
        except sqlite3.Error as e:
            self.logger.error(f"Failed to resolve duel {duel_id}: {e}")