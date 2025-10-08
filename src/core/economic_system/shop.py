import sqlite3
from pathlib import Path

class ShopManager:
    """Manages bot-owned shops and their inventory."""
    def __init__(self, db_path='data/world_data.db'):
        self.db_path = Path(db_path)
        self._init_db()

    def _get_conn(self):
        return sqlite3.connect(self.db_path)

    def _init_db(self):
        """Initializes the shop and inventory tables."""
        with self._get_conn() as conn:
            cursor = conn.cursor()
            # Shops table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS shops (
                    shop_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    owner_name TEXT NOT NULL UNIQUE,
                    shop_name TEXT NOT NULL,
                    description TEXT
                )
            """)
            # Inventory table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS inventory (
                    item_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    shop_id INTEGER NOT NULL,
                    item_name TEXT NOT NULL,
                    description TEXT,
                    price REAL NOT NULL,
                    quantity INTEGER NOT NULL,
                    FOREIGN KEY (shop_id) REFERENCES shops (shop_id)
                )
            """)
            conn.commit()

    def open_shop(self, owner_name, shop_name, description):
        """Allows a character to open their own shop."""
        with self._get_conn() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute("INSERT INTO shops (owner_name, shop_name, description) VALUES (?, ?, ?)",
                               (owner_name, shop_name, description))
                conn.commit()
                print(f"[Economy] {owner_name} has opened a new shop: {shop_name}!")
                return True
            except sqlite3.IntegrityError:
                print(f"[Economy] Error: {owner_name} already owns a shop.")
                return False

    def add_item_to_shop(self, owner_name, item_name, description, price, quantity):
        """Adds an item to a character's shop inventory."""
        with self._get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT shop_id FROM shops WHERE owner_name = ?", (owner_name,))
            shop = cursor.fetchone()
            if not shop:
                print(f"[Economy] Error: {owner_name} does not own a shop.")
                return False

            shop_id = shop[0]
            cursor.execute("INSERT INTO inventory (shop_id, item_name, description, price, quantity) VALUES (?, ?, ?, ?, ?)",
                           (shop_id, item_name, description, price, quantity))
            conn.commit()
        print(f"[Economy] {owner_name} added {quantity} of {item_name} to their shop for {price} Rs each.")
        return True

    def list_shops(self):
        """Lists all available shops."""
        with self._get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT shop_name, owner_name, description FROM shops")
            return cursor.fetchall()

    def list_inventory(self, owner_name):
        """Lists the inventory of a specific shop by owner name."""
        with self._get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT i.item_name, i.description, i.price, i.quantity
                FROM inventory i
                JOIN shops s ON i.shop_id = s.shop_id
                WHERE s.owner_name = ?
            """, (owner_name,))
            return cursor.fetchall()

    def purchase_item(self, buyer_name, seller_name, item_name, quantity, economy_manager):
        """Handles the purchase of an item from a shop."""
        with self._get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT i.item_id, i.price, i.quantity FROM inventory i JOIN shops s ON i.shop_id = s.shop_id WHERE s.owner_name = ? AND i.item_name = ?",
                (seller_name, item_name)
            )
            item = cursor.fetchone()

            if not item:
                return False, "Item not found in this shop."

            item_id, price, stock = item
            if stock < quantity:
                return False, "Not enough items in stock."

            total_cost = price * quantity
            if not economy_manager.transfer_money(buyer_name, seller_name, total_cost, f"Purchase of {quantity}x {item_name}"):
                return False, "Insufficient funds."

            # Update stock
            new_stock = stock - quantity
            if new_stock > 0:
                cursor.execute("UPDATE inventory SET quantity = ? WHERE item_id = ?", (new_stock, item_id))
            else:
                cursor.execute("DELETE FROM inventory WHERE item_id = ?", (item_id,))

            conn.commit()
        return True, f"Successfully purchased {quantity}x {item_name} from {seller_name}."