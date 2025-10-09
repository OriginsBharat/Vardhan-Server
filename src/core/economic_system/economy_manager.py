import sqlite3
import logging
from typing import Optional

class EconomyManager:
    """
    Manages the entire economy of the AI world, including wallets and transactions.
    """
    def __init__(self, db_path="data/world_data.db"):
        self.db_path = db_path
        self.logger = logging.getLogger(__name__)
        self._init_db()

    def _init_db(self):
        """Initializes the database and creates the wallets table if it doesn't exist."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS wallets (
                        character_name TEXT PRIMARY KEY,
                        balance INTEGER NOT NULL DEFAULT 1000
                    )
                """)
                conn.commit()
            self.logger.info("Economy database initialized successfully.")
        except sqlite3.Error as e:
            self.logger.error(f"Database error during initialization: {e}", exc_info=True)

    def get_balance(self, character_name: str) -> int:
        """
        Gets the balance for a specific character. Creates a wallet if one doesn't exist.

        Args:
            character_name: The name of the character.

        Returns:
            The character's balance as an integer.
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                # Ensure the character exists in the wallet, if not, they start with a default balance
                cursor.execute("INSERT OR IGNORE INTO wallets (character_name) VALUES (?)", (character_name,))
                cursor.execute("SELECT balance FROM wallets WHERE character_name = ?", (character_name,))
                result = cursor.fetchone()
                return result[0] if result else 0
        except sqlite3.Error as e:
            self.logger.error(f"Failed to get balance for {character_name}: {e}", exc_info=True)
            return 0

    def update_balance(self, character_name: str, amount: int) -> bool:
        """
        Updates a character's balance by a certain amount (can be negative).
        Ensures a character cannot have a negative balance unless they are the Master.

        Args:
            character_name: The name of the character.
            amount: The amount to add (positive) or subtract (negative).

        Returns:
            True if the update was successful, False otherwise.
        """
        # The Master can have infinite money and go into debt if needed
        if character_name.lower() == "master":
             pass # No balance check for the master
        else:
            current_balance = self.get_balance(character_name)
            if current_balance + amount < 0:
                self.logger.warning(f"Transaction for {character_name} failed: insufficient funds.")
                return False

        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("INSERT OR IGNORE INTO wallets (character_name) VALUES (?)", (character_name,))
                cursor.execute("UPDATE wallets SET balance = balance + ? WHERE character_name = ?", (amount, character_name))
                conn.commit()

                new_balance = self.get_balance(character_name)
                self.logger.info(f"Updated {character_name}'s balance by {amount}. New balance: {new_balance} Rs.")
                return True
        except sqlite3.Error as e:
            self.logger.error(f"Failed to update balance for {character_name}: {e}", exc_info=True)
            return False