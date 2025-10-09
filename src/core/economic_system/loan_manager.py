import sqlite3
import logging
import uuid
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any

class LoanManager:
    """Manages the loan and debt system of the world."""
    def __init__(self, bot):
        self.bot = bot
        self.db_path = "data/world_data.db"
        self.logger = logging.getLogger(__name__)
        self._init_db()

    def _init_db(self):
        """Initializes the database tables for loans and servitude."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS loans (
                        loan_id TEXT PRIMARY KEY,
                        lender_name TEXT NOT NULL,
                        borrower_name TEXT NOT NULL,
                        amount INTEGER NOT NULL,
                        interest_rate REAL NOT NULL,
                        due_date TEXT NOT NULL,
                        status TEXT NOT NULL DEFAULT 'active' -- 'active', 'paid', 'defaulted'
                    )
                """)
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS servitude (
                        servant_name TEXT PRIMARY KEY,
                        master_name TEXT NOT NULL,
                        originating_loan_id TEXT NOT NULL,
                        FOREIGN KEY (originating_loan_id) REFERENCES loans(loan_id)
                    )
                """)
                conn.commit()
            self.logger.info("Loan and servitude database tables initialized.")
        except sqlite3.Error as e:
            self.logger.error(f"Database error in LoanManager init: {e}", exc_info=True)

    def create_loan(self, lender: str, borrower: str, amount: int, interest: float, duration_days: int) -> Optional[str]:
        """Creates a new loan and returns the loan ID."""
        loan_id = str(uuid.uuid4())[:8]
        due_date = (datetime.now() + timedelta(days=duration_days)).isoformat()

        transaction_success = self.bot.economy_manager.transaction(lender, borrower, amount)
        if not transaction_success:
            self.logger.error(f"Loan creation failed: Could not transfer principal from {lender} to {borrower}.")
            return None

        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO loans (loan_id, lender_name, borrower_name, amount, interest_rate, due_date) VALUES (?, ?, ?, ?, ?, ?)",
                    (loan_id, lender, borrower, amount, interest, due_date)
                )
                conn.commit()
            self.logger.info(f"New loan created: {loan_id} ({lender} -> {borrower} for {amount} Rs).")
            return loan_id
        except sqlite3.Error as e:
            self.logger.error(f"Failed to create loan record: {e}")
            self.bot.economy_manager.transaction(borrower, lender, amount)
            return None

    def get_loan(self, loan_id: str) -> Optional[Dict[str, Any]]:
        """Retrieves a loan by its ID."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM loans WHERE loan_id = ?", (loan_id,))
                result = cursor.fetchone()
                return dict(result) if result else None
        except sqlite3.Error as e:
            self.logger.error(f"Failed to get loan {loan_id}: {e}")
            return None

    def repay_loan(self, loan_id: str) -> bool:
        """Marks a loan as paid. Assumes payment has been handled separately."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("UPDATE loans SET status = 'paid' WHERE loan_id = ?", (loan_id,))
                conn.commit()
                if conn.total_changes > 0:
                    self.logger.info(f"Loan {loan_id} has been marked as paid.")
                    return True
                return False
        except sqlite3.Error as e:
            self.logger.error(f"Failed to repay loan {loan_id}: {e}")
            return False

    def check_for_defaults(self) -> List[Dict[str, Any]]:
        """Checks for active loans past their due date, marks them as defaulted, and enslaves the borrower."""
        defaulted_loans = []
        now = datetime.now().isoformat()
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                # Use a transaction to ensure atomicity
                cursor.execute("BEGIN TRANSACTION")
                cursor.execute("SELECT * FROM loans WHERE status = 'active' AND due_date < ?", (now,))
                loans_to_default = cursor.fetchall()

                for loan_data in loans_to_default:
                    loan = dict(loan_data)
                    loan_id = loan['loan_id']

                    # 1. Update loan status to 'defaulted'
                    cursor.execute("UPDATE loans SET status = 'defaulted' WHERE loan_id = ?", (loan_id,))

                    # 2. Enslave the borrower
                    cursor.execute(
                        "INSERT OR REPLACE INTO servitude (servant_name, master_name, originating_loan_id) VALUES (?, ?, ?)",
                        (loan['borrower_name'], loan['lender_name'], loan['loan_id'])
                    )

                    defaulted_loans.append(loan)
                    self.logger.warning(f"Loan {loan_id} for {loan['borrower_name']} has defaulted and they are now enslaved to {loan['lender_name']}.")

                    # Inflict the psychological scar of servitude
                    self.bot.scar_manager.add_scar(
                        character_name=loan['borrower_name'],
                        scar_description=f"Forced into indentured servitude under {loan['lender_name']} after defaulting on a loan."
                    )

                cursor.execute("COMMIT")
            return defaulted_loans
        except sqlite3.Error as e:
            self.logger.error(f"Failed to check for loan defaults: {e}")
            conn.execute("ROLLBACK")
            return []

    def is_enslaved(self, character_name: str) -> Optional[str]:
        """Checks if a character is enslaved and returns their master's name if they are."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT master_name FROM servitude WHERE servant_name = ?", (character_name,))
                result = cursor.fetchone()
                return result[0] if result else None
        except sqlite3.Error as e:
            self.logger.error(f"Failed to check servitude status for {character_name}: {e}")
            return None