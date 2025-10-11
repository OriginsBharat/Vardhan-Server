import sqlite3
import logging
import os

class EconomyManager:
    """
    Manages the economy, including wallets and transactions.
    """
    def __init__(self, bot):
        self.bot = bot
        script_dir = os.path.dirname(__file__)
        project_root = os.path.abspath(os.path.join(script_dir, '..', '..', '..'))
        self.db_path = os.path.join(project_root, 'data', 'world_data.db')
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self.logger = logging.getLogger(__name__)
        self._init_db()

    def _init_db(self):
        """Initializes the database and creates the wallets table."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS wallets (
                        character_name TEXT PRIMARY KEY,
                        balance INTEGER NOT NULL DEFAULT 100
                    )
                """)
                conn.commit()
            self.logger.info("Economy database (wallets table) initialized successfully.")
        except sqlite3.Error as e:
            self.logger.error(f"Database error during economy initialization: {e}", exc_info=True)

    def get_balance(self, character_name: str) -> int:
        """Gets the balance for a character. The Master has infinite wealth."""
        if character_name.lower() == self.bot.config.user_id: # Check against the Master's ID
            return float('inf')

        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("INSERT OR IGNORE INTO wallets (character_name) VALUES (?)", (character_name,))
                cursor.execute("SELECT balance FROM wallets WHERE character_name = ?", (character_name,))
                result = cursor.fetchone()
                return result[0] if result else 0
        except sqlite3.Error as e:
            self.logger.error(f"Failed to get balance for {character_name}: {e}", exc_info=True)
            return 0

    def transaction(self, character_name: str, amount: int) -> bool:
        """
        Updates a character's balance. Returns True on success, False on failure.
        """
        if str(character_name) == str(self.bot.config.user_id):
            return True # Master's transactions always succeed

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
                self.logger.info(f"Transaction complete. {character_name}'s new balance: {new_balance} Rs.")
                return True
        except sqlite3.Error as e:
            self.logger.error(f"Failed to process transaction for {character_name}: {e}", exc_info=True)
            return False