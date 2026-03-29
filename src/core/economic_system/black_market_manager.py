import sqlite3
import logging
import uuid
from typing import Optional, List, Dict, Any

class BlackMarketManager:
    """Manages the black market listings and transactions."""
    def __init__(self, bot):
        self.bot = bot
        self.db_path = "data/world_data.db"
        self.logger = logging.getLogger(__name__)
        self._init_db()

    def _init_db(self):
        """Initializes the database table for black market listings."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS black_market_listings (
                        listing_id TEXT PRIMARY KEY,
                        seller_name TEXT NOT NULL,
                        item_name TEXT NOT NULL,
                        item_description TEXT,
                        price INTEGER NOT NULL,
                        status TEXT NOT NULL DEFAULT 'available' -- 'available', 'sold'
                    )
                """)
                conn.commit()
            self.logger.info("Black market database table initialized.")
        except sqlite3.Error as e:
            self.logger.error(f"Database error in BlackMarketManager init: {e}", exc_info=True)

    def create_listing(self, seller: str, item_name: str, description: str, price: int) -> Optional[str]:
        """Creates a new black market listing."""
        listing_id = str(uuid.uuid4())[:8]
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO black_market_listings (listing_id, seller_name, item_name, item_description, price) VALUES (?, ?, ?, ?, ?)",
                    (listing_id, seller, item_name, description, price)
                )
                conn.commit()
            self.logger.info(f"New black market listing created: {listing_id} by {seller}")
            return listing_id
        except sqlite3.Error as e:
            self.logger.error(f"Failed to create black market listing: {e}")
            return None

    def get_listing(self, listing_id: str) -> Optional[Dict[str, Any]]:
        """Retrieves a listing by its ID."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM black_market_listings WHERE listing_id = ? AND status = 'available'", (listing_id,))
                result = cursor.fetchone()
                return dict(result) if result else None
        except sqlite3.Error as e:
            self.logger.error(f"Failed to get black market listing {listing_id}: {e}")
            return None

    def get_all_listings(self) -> List[Dict[str, Any]]:
        """Retrieves all available listings."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM black_market_listings WHERE status = 'available'")
                results = cursor.fetchall()
                return [dict(row) for row in results]
        except sqlite3.Error as e:
            self.logger.error(f"Failed to get all black market listings: {e}")
            return []

    def purchase(self, listing_id: str, buyer_name: str) -> bool:
        """Handles the purchase of a black market item."""
        listing = self.get_listing(listing_id)
        if not listing:
            return False

        seller_name = listing['seller_name']
        price = listing['price']

        # Use the economy manager to handle the transaction
        transaction_success = self.bot.economy_manager.transaction(buyer_name, seller_name, price)
        if not transaction_success:
            return False

        # Mark the item as sold
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("UPDATE black_market_listings SET status = 'sold' WHERE listing_id = ?", (listing_id,))
                conn.commit()
            self.logger.info(f"Listing {listing_id} purchased by {buyer_name}.")
            return True
        except sqlite3.Error as e:
            self.logger.error(f"Failed to update listing {listing_id} to 'sold': {e}")
            # Attempt to revert the transaction
            self.bot.economy_manager.transaction(seller_name, buyer_name, price)
            return False