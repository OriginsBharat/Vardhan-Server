import sqlite3
from pathlib import Path

class EconomyManager:
    """Manages the entire economy of the AI world, including wallets, transactions, and debt servitude."""
    def __init__(self, db_path='data/world_data.db'):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _get_conn(self):
        """Returns a database connection."""
        return sqlite3.connect(self.db_path)

    def _init_db(self):
        """Initializes the database tables if they don't exist."""
        with self._get_conn() as conn:
            cursor = conn.cursor()
            # Wallets table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS wallets (
                    character_name TEXT PRIMARY KEY,
                    balance REAL NOT NULL DEFAULT 0
                )
            """)
            # Transactions table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS transactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    from_character TEXT,
                    to_character TEXT,
                    amount REAL NOT NULL,
                    description TEXT
                )
            """)
            # Servitude table for the Gilded Cage
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS servitude (
                    character_name TEXT PRIMARY KEY,
                    owner_name TEXT NOT NULL,
                    debt_amount REAL NOT NULL,
                    start_date DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.commit()

    def create_wallet(self, character_name, initial_balance=1000):
        """Creates a new wallet for a character."""
        with self._get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT OR IGNORE INTO wallets (character_name, balance) VALUES (?, ?)", (character_name, initial_balance))
            conn.commit()

    def get_balance(self, character_name):
        """Gets the balance of a character's wallet."""
        with self._get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT balance FROM wallets WHERE character_name = ?", (character_name,))
            result = cursor.fetchone()
            return result[0] if result else 0

    def adjust_balance(self, character_name, amount, description=""):
        """Adjusts a character's balance. Logs the transaction."""
        if character_name.lower() == "master":
            return True # Master has infinite money

        # Check if character is in servitude
        if self.is_in_servitude(character_name):
            print(f"[Economy] Transaction failed for {character_name}: Character is in servitude and cannot earn/lose money.")
            return False

        current_balance = self.get_balance(character_name)
        new_balance = current_balance + amount

        if new_balance < 0:
            return False # Insufficient funds

        with self._get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE wallets SET balance = ? WHERE character_name = ?", (new_balance, character_name))
            from_char = "System" if amount > 0 else character_name
            to_char = character_name if amount > 0 else "System"
            cursor.execute(
                "INSERT INTO transactions (from_character, to_character, amount, description) VALUES (?, ?, ?, ?)",
                (from_char, to_char, abs(amount), description)
            )
            conn.commit()
        return True

    def transfer_money(self, from_character, to_character, amount, description=""):
        """Transfers money between two characters."""
        if self.get_balance(from_character) < amount and from_character.lower() != "master":
            return False

        with self._get_conn() as conn:
            cursor = conn.cursor()
            if from_character.lower() != "master":
                cursor.execute("UPDATE wallets SET balance = balance - ? WHERE character_name = ?", (amount, from_character))
            cursor.execute("UPDATE wallets SET balance = balance + ? WHERE character_name = ?", (amount, to_character))
            cursor.execute(
                "INSERT INTO transactions (from_character, to_character, amount, description) VALUES (?, ?, ?, ?)",
                (from_character, to_character, amount, description)
            )
            conn.commit()
        return True

    def enter_servitude(self, character_name, owner_name, debt_amount):
        """Forces a character into servitude under an owner."""
        with self._get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO servitude (character_name, owner_name, debt_amount) VALUES (?, ?, ?)",
                           (character_name, owner_name, debt_amount))
            conn.commit()

    def is_in_servitude(self, character_name):
        """Checks if a character is currently in servitude and returns their owner."""
        with self._get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT owner_name FROM servitude WHERE character_name = ?", (character_name,))
            result = cursor.fetchone()
            return result[0] if result else None

    def free_from_servitude(self, character_name):
        """Releases a character from servitude."""
        with self._get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM servitude WHERE character_name = ?", (character_name,))
            conn.commit()