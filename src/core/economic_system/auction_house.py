import sqlite3
from pathlib import Path
from datetime import datetime, timedelta

class AuctionHouse:
    """Manages the auction system for high-value items and services."""
    def __init__(self, db_path='data/world_data.db'):
        self.db_path = Path(db_path)
        self._init_db()

    def _get_conn(self):
        return sqlite3.connect(self.db_path)

    def _init_db(self):
        """Initializes the auctions and bids tables."""
        with self._get_conn() as conn:
            cursor = conn.cursor()
            # Auctions table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS auctions (
                    auction_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    seller_name TEXT NOT NULL,
                    item_name TEXT NOT NULL,
                    item_description TEXT,
                    start_time DATETIME DEFAULT CURRENT_TIMESTAMP,
                    end_time DATETIME NOT NULL,
                    starting_bid REAL NOT NULL,
                    current_bid REAL,
                    winning_bidder TEXT,
                    is_active BOOLEAN DEFAULT 1
                )
            """)
            # Bids table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS bids (
                    bid_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    auction_id INTEGER NOT NULL,
                    bidder_name TEXT NOT NULL,
                    bid_amount REAL NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (auction_id) REFERENCES auctions (auction_id)
                )
            """)
            conn.commit()

    def create_auction(self, seller_name, item_name, description, starting_bid, duration_hours):
        """Creates a new auction."""
        end_time = datetime.now() + timedelta(hours=duration_hours)
        with self._get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO auctions (seller_name, item_name, item_description, end_time, starting_bid, current_bid)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (seller_name, item_name, description, end_time, starting_bid, starting_bid))
            auction_id = cursor.lastrowid
            conn.commit()
        print(f"[Economy] New auction #{auction_id} created by {seller_name} for '{item_name}'.")
        return auction_id

    def place_bid(self, auction_id, bidder_name, bid_amount, economy_manager):
        """Places a bid on an active auction."""
        with self._get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT current_bid, end_time, is_active FROM auctions WHERE auction_id = ?", (auction_id,))
            auction = cursor.fetchone()

            if not auction or not auction[2] or datetime.now() > datetime.fromisoformat(auction[1]):
                return False, "Auction is not active or has ended."

            if bid_amount <= auction[0]:
                return False, f"Your bid must be higher than the current bid of {auction[0]} Rs."

            if economy_manager.get_balance(bidder_name) < bid_amount and bidder_name.lower() != "master":
                return False, "You do not have enough Rs to place this bid."

            cursor.execute(
                "UPDATE auctions SET current_bid = ?, winning_bidder = ? WHERE auction_id = ?",
                (bid_amount, bidder_name, auction_id)
            )
            cursor.execute(
                "INSERT INTO bids (auction_id, bidder_name, bid_amount) VALUES (?, ?, ?)",
                (auction_id, bidder_name, bid_amount)
            )
            conn.commit()
        return True, f"Successfully bid {bid_amount} Rs on auction #{auction_id}."

    def get_active_auctions(self):
        """Returns a list of all active auctions."""
        with self._get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT auction_id, seller_name, item_name, item_description, current_bid, end_time
                FROM auctions WHERE is_active = 1 AND end_time > ?
            """, (datetime.now(),))
            return cursor.fetchall()

    def check_and_close_auctions(self, economy_manager):
        """Finds finished auctions, processes them, and returns results."""
        closed_auctions = []
        with self._get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT auction_id, seller_name, winning_bidder, current_bid, item_name FROM auctions WHERE is_active = 1 AND end_time <= ?", (datetime.now(),))
            finished_auctions = cursor.fetchall()

            for auction in finished_auctions:
                auction_id, seller, winner, bid, item = auction
                if winner:
                    description = f"Won auction #{auction_id} for '{item}'"
                    if economy_manager.transfer_money(winner, seller, bid, description):
                        closed_auctions.append(f"Auction #{auction_id} for '{item}' has ended. **{winner}** won with a bid of **{bid} Rs**!")
                    else:
                        closed_auctions.append(f"Auction #{auction_id} for '{item}' has ended, but winner **{winner}** could not afford the **{bid} Rs** bid. The sale has failed.")
                else:
                    closed_auctions.append(f"Auction #{auction_id} for '{item}' has ended with no bids.")

                cursor.execute("UPDATE auctions SET is_active = 0 WHERE auction_id = ?", (auction_id,))
            conn.commit()
        return closed_auctions