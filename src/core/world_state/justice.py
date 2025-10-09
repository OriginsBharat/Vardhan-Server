import sqlite3
import logging
import uuid
from typing import Optional, Dict, Any

class JusticeManager:
    """Manages the justice system, including court cases and judgments."""
    def __init__(self, bot):
        self.bot = bot
        self.db_path = "data/world_data.db"
        self.logger = logging.getLogger(__name__)
        self._init_db()

    def _init_db(self):
        """Initializes the database table for cases."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                # Note: 'judge' defaults to 'Maya'
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS cases (
                        case_id TEXT PRIMARY KEY,
                        plaintiff TEXT NOT NULL,
                        defendant TEXT NOT NULL,
                        reason TEXT NOT NULL,
                        status TEXT NOT NULL DEFAULT 'open', -- 'open', 'closed'
                        judge TEXT NOT NULL DEFAULT 'Maya', -- 'Maya', 'Master'
                        verdict TEXT
                    )
                """)
                conn.commit()
            self.logger.info("Justice system database table initialized.")
        except sqlite3.Error as e:
            self.logger.error(f"Database error in JusticeManager init: {e}", exc_info=True)

    def create_case(self, plaintiff: str, defendant: str, reason: str) -> Optional[str]:
        """Creates a new case and returns the case ID."""
        case_id = str(uuid.uuid4())[:8]
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO cases (case_id, plaintiff, defendant, reason) VALUES (?, ?, ?, ?)",
                    (case_id, plaintiff, defendant, reason)
                )
                conn.commit()
            self.logger.info(f"New case created: {case_id} ({plaintiff} vs {defendant})")
            return case_id
        except sqlite3.Error as e:
            self.logger.error(f"Failed to create case: {e}")
            return None

    def get_case(self, case_id: str) -> Optional[Dict[str, Any]]:
        """Retrieves a case by its ID."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM cases WHERE case_id = ?", (case_id,))
                result = cursor.fetchone()
                return dict(result) if result else None
        except sqlite3.Error as e:
            self.logger.error(f"Failed to get case {case_id}: {e}")
            return None

    def set_judge(self, case_id: str, judge: str) -> bool:
        """Sets the judge for a specific case. Returns True on success."""
        if judge not in ['Maya', 'Master']:
            self.logger.warning(f"Invalid judge '{judge}' specified for case {case_id}.")
            return False
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("UPDATE cases SET judge = ? WHERE case_id = ?", (judge, case_id))
                conn.commit()
                # Check if the update was successful
                return conn.total_changes > 0
        except sqlite3.Error as e:
            self.logger.error(f"Failed to set judge for case {case_id}: {e}")
            return False

    def close_case_with_verdict(self, case_id: str, verdict: str) -> bool:
        """Closes a case and records the final verdict."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "UPDATE cases SET status = 'closed', verdict = ? WHERE case_id = ?",
                    (verdict, case_id)
                )
                conn.commit()
                if conn.total_changes > 0:
                    self.logger.info(f"Case {case_id} has been closed with a verdict.")
                    self.bot.narrative_manager.log_event(
                        f"Case {case_id} was closed with the verdict: '{verdict}'.",
                        level="major"
                    )
                    return True
                return False
        except sqlite3.Error as e:
            self.logger.error(f"Failed to close case {case_id} with verdict: {e}")
            return False