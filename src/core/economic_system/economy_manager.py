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

    def transaction(self, from_char: str, to_char: str, amount: int) -> bool:
        """
        Transfers a specific amount from one character to another.
        """
        if from_char.lower() != "master" and self.get_balance(from_char) < amount:
            self.logger.warning(f"Transaction failed: {from_char} has insufficient funds.")
            return False

        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                # Use a transaction to ensure atomicity
                cursor.execute("BEGIN TRANSACTION")
                # Debit from sender
                if from_char.lower() != "master":
                    cursor.execute("UPDATE wallets SET balance = balance - ? WHERE character_name = ?", (amount, from_char))
                # Credit to receiver
                cursor.execute("INSERT OR IGNORE INTO wallets (character_name) VALUES (?)", (to_char,))
                cursor.execute("UPDATE wallets SET balance = balance + ? WHERE character_name = ?", (amount, to_char))
                cursor.execute("COMMIT")

            self.logger.info(f"Transaction successful: {from_char} sent {amount} Rs to {to_char}.")
            return True
        except sqlite3.Error as e:
            self.logger.error(f"Transaction from {from_char} to {to_char} failed: {e}", exc_info=True)
            conn.execute("ROLLBACK")
            return False

    def update_balance(self, character_name: str, amount: int) -> bool:
        """
        Updates a character's balance by a certain amount (can be negative).
        This is for direct adjustments like earning from a job or paying a system fee.
        """
        if character_name.lower() != "master" and self.get_balance(character_name) + amount < 0:
            self.logger.warning(f"Balance update for {character_name} failed: insufficient funds.")
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