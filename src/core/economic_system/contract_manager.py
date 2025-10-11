import sqlite3
import logging
import uuid
from typing import Optional, List, Dict, Any

class ContractManager:
    """Manages the bot-to-bot contract system for the Living Marketplace."""
    def __init__(self, bot):
        self.bot = bot
        self.db_path = "data/world_data.db"
        self.logger = logging.getLogger(__name__)
        self._init_db()

    def _init_db(self):
        """Initializes the database table for contracts."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS contracts (
                        contract_id TEXT PRIMARY KEY,
                        client_name TEXT NOT NULL,
                        contractor_name TEXT, -- Can be NULL for open contracts
                        task_description TEXT NOT NULL,
                        reward INTEGER NOT NULL,
                        status TEXT NOT NULL DEFAULT 'open' -- 'open', 'accepted', 'completed', 'failed'
                    )
                """)
                conn.commit()
            self.logger.info("Living Marketplace (contracts) database table initialized.")
        except sqlite3.Error as e:
            self.logger.error(f"Database error in ContractManager init: {e}", exc_info=True)

    def create_contract(self, client_name: str, task_description: str, reward: int) -> Optional[str]:
        """Creates a new open contract."""
        contract_id = str(uuid.uuid4())[:8]

        # The client must have the funds to post the contract.
        # The funds are held in escrow by the system (conceptually).
        if not self.bot.economy_manager.transaction(client_name, "system_escrow", reward):
            self.logger.warning(f"Contract creation failed: {client_name} has insufficient funds for reward.")
            return None

        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO contracts (contract_id, client_name, task_description, reward) VALUES (?, ?, ?, ?)",
                    (contract_id, client_name, task_description, reward)
                )
                conn.commit()
            self.logger.info(f"New contract created: {contract_id} by {client_name} for {reward} Rs.")
            return contract_id
        except sqlite3.Error as e:
            self.logger.error(f"Failed to create contract: {e}")
            # Attempt to refund the client if DB write fails
            self.bot.economy_manager.transaction("system_escrow", client_name, reward)
            return None

    def get_open_contracts(self) -> List[Dict[str, Any]]:
        """Retrieves all open contracts."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM contracts WHERE status = 'open'")
                return [dict(row) for row in cursor.fetchall()]
        except sqlite3.Error as e:
            self.logger.error(f"Failed to get open contracts: {e}")
            return []

    def accept_contract(self, contract_id: str, contractor_name: str) -> bool:
        """Allows a bot to accept an open contract."""
        contract = self.get_open_contracts()
        # Ensure the contract is actually open
        if not any(c['contract_id'] == contract_id for c in contract):
            return False

        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "UPDATE contracts SET contractor_name = ?, status = 'accepted' WHERE contract_id = ? AND status = 'open'",
                    (contractor_name, contract_id)
                )
                conn.commit()
                if conn.total_changes > 0:
                    self.logger.info(f"{contractor_name} has accepted contract {contract_id}.")
                    return True
                return False
        except sqlite3.Error as e:
            self.logger.error(f"Failed to accept contract {contract_id}: {e}")
            return False

    def complete_contract(self, contract_id: str, contractor_name: str) -> bool:
        """Marks a contract as complete and pays the contractor."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT reward FROM contracts WHERE contract_id = ? AND contractor_name = ? AND status = 'accepted'",
                    (contract_id, contractor_name)
                )
                result = cursor.fetchone()
                if not result:
                    return False

                reward = result['reward']

                # Pay the contractor from escrow
                if not self.bot.economy_manager.transaction("system_escrow", contractor_name, reward):
                    self.logger.error(f"Failed to pay contractor {contractor_name} for contract {contract_id}.")
                    return False

                cursor.execute("UPDATE contracts SET status = 'completed' WHERE contract_id = ?", (contract_id,))
                conn.commit()
                self.logger.info(f"Contract {contract_id} completed by {contractor_name}. Reward of {reward} Rs paid.")
                return True
        except sqlite3.Error as e:
            self.logger.error(f"Failed to complete contract {contract_id}: {e}")
            return False