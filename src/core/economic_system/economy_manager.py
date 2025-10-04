# src/core/economic_system/economy_manager.py
# Manages the entire economy, including wallets, transactions, and data persistence.

import sqlite3
import logging
from datetime import datetime
from threading import Lock
from typing import Optional

DB_PATH = "data/world_data.db"

class EconomyManager:
    """
    Handles all economic activities in the world.
    This includes managing player wallets and logging all transactions.
    This class is designed to be thread-safe.
    """
    def __init__(self, master_user_id: int):
        # `check_same_thread=False` is necessary for multi-threaded/async access.
        # We will manage concurrency with our own lock.
        self.conn = sqlite3.connect(DB_PATH, check_same_thread=False)
        self.cursor = self.conn.cursor()
        self.master_id = master_user_id
        self.lock = Lock()
        self._setup_database()
        logging.info("EconomyManager initialized and database connected.")

    def _setup_database(self):
        """Creates the necessary database tables if they don't already exist."""
        with self.lock:
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS wallets (
                    user_id INTEGER PRIMARY KEY,
                    balance REAL NOT NULL DEFAULT 0
                )
            """)
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS transactions (
                    transaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    from_user_id INTEGER,
                    to_user_id INTEGER,
                    amount REAL NOT NULL,
                    description TEXT
                )
            """)
            self.conn.commit()
            logging.info("Database tables for economy are set up.")

    def _wallet_exists(self, user_id: int) -> bool:
        """Checks if a wallet exists for the user."""
        self.cursor.execute("SELECT 1 FROM wallets WHERE user_id = ?", (user_id,))
        return self.cursor.fetchone() is not None

    def _create_wallet(self, user_id: int, starting_balance: float = 100.0):
        """Creates a new wallet for a user if it doesn't exist."""
        if not self._wallet_exists(user_id):
            balance = 999999999 if user_id == self.master_id else starting_balance
            self.cursor.execute("INSERT INTO wallets (user_id, balance) VALUES (?, ?)", (user_id, balance))
            self.conn.commit()
            logging.info(f"Created new wallet for user {user_id} with balance {balance} Rs.")

    def get_balance(self, user_id: int) -> float:
        """Retrieves the balance for a given user. Creates a wallet if it doesn't exist."""
        with self.lock:
            self._create_wallet(user_id)
            self.cursor.execute("SELECT balance FROM wallets WHERE user_id = ?", (user_id,))
            result = self.cursor.fetchone()
            return result[0] if result else 0.0

    def deposit(self, user_id: int, amount: float, description: str) -> bool:
        """Deposits an amount into a user's wallet."""
        if amount <= 0: return False
        with self.lock:
            try:
                self._create_wallet(user_id)
                self.cursor.execute("UPDATE wallets SET balance = balance + ? WHERE user_id = ?", (amount, user_id))
                self._log_transaction(None, user_id, amount, description)
                self.conn.commit()
                return True
            except sqlite3.Error as e:
                logging.error(f"Failed to deposit {amount} to user {user_id}: {e}")
                self.conn.rollback()
                return False

    def make_transaction(self, from_user_id: int, to_user_id: int, amount: float, description: str) -> bool:
        """Transfers currency from one user to another."""
        if amount <= 0: return False
        with self.lock:
            # The master has "infinite" money, so we skip their balance check.
            if from_user_id != self.master_id:
                from_balance = self.get_balance(from_user_id)
                if from_balance < amount:
                    logging.warning(f"Transaction failed: User {from_user_id} has insufficient funds.")
                    return False

            self._create_wallet(to_user_id)
            try:
                if from_user_id != self.master_id:
                    self.cursor.execute("UPDATE wallets SET balance = balance - ? WHERE user_id = ?", (amount, from_user_id))
                self.cursor.execute("UPDATE wallets SET balance = balance + ? WHERE user_id = ?", (amount, to_user_id))
                self._log_transaction(from_user_id, to_user_id, amount, description)
                self.conn.commit()
                logging.info(f"Transaction successful: {amount} Rs from {from_user_id} to {to_user_id} for '{description}'.")
                return True
            except sqlite3.Error as e:
                logging.error(f"An error occurred during transaction from {from_user_id} to {to_user_id}: {e}")
                self.conn.rollback()
                return False

    def _log_transaction(self, from_user_id: Optional[int], to_user_id: int, amount: float, description: str):
        """A private helper to log a transaction to the database."""
        timestamp = datetime.utcnow().isoformat()
        self.cursor.execute("""
            INSERT INTO transactions (timestamp, from_user_id, to_user_id, amount, description)
            VALUES (?, ?, ?, ?, ?)
        """, (timestamp, from_user_id, to_user_id, amount, description))

    def close(self):
        """Closes the database connection."""
        with self.lock:
            if self.conn:
                self.conn.close()
                logging.info("Database connection closed.")