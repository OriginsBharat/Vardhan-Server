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
                        balance INTEGER NOT NULL DEFAULT 0
                    )
                """)
                conn.commit()
            self.logger.info("Economy database initialized successfully.")
        except sqlite3.Error as e:
            self.logger.error(f"Database error during initialization: {e}")

    def get_balance(self, character_name: str) -> Optional[int]:
        """
        Gets the balance for a specific character.

        Args:
            character_name: The name of the character.

        Returns:
            The character's balance as an integer, or None if the character is not found.
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT balance FROM wallets WHERE character_name = ?", (character_name,))
                result = cursor.fetchone()
                return result[0] if result else 0
        except sqlite3.Error as e:
            self.logger.error(f"Failed to get balance for {character_name}: {e}")
            return None

    def update_balance(self, character_name: str, amount: int) -> bool:
        """
        Updates a character's balance by a certain amount (can be negative).

        Args:
            character_name: The name of the character.
            amount: The amount to add (positive) or subtract (negative).

        Returns:
            True if the update was successful, False otherwise.
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                # Ensure the character exists in the wallet
                cursor.execute("INSERT OR IGNORE INTO wallets (character_name) VALUES (?)", (character_name,))

                # Perform the update
                cursor.execute("UPDATE wallets SET balance = balance + ? WHERE character_name = ?", (amount, character_name))
                conn.commit()
                self.logger.info(f"Updated {character_name}'s balance by {amount}. New balance: {self.get_balance(character_name)}")
                return True
        except sqlite3.Error as e:
            self.logger.error(f"Failed to update balance for {character_name}: {e}")
            return False

    async def perform_work(self, persona):
        """
        Simulates a character performing their job and earning money.
        The actual job logic and income will be defined in the JobManager.
        """
        # This is a placeholder for more complex job logic
        # For now, let's assume a simple fixed income.
        income = 100 # Example income
        self.update_balance(persona.name, income)
        self.logger.info(f"{persona.name} worked and earned {income} Rs.")
        # In a real implementation, this would call a JobManager to get job-specific details.