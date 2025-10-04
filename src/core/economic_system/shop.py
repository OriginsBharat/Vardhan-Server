# src/core/economic_system/shop.py
# Defines system-run shops, their inventories, and manages purchase transactions.

import logging
from typing import List, Optional, Dict

from src.core.character_system.personas import Character
from src.core.economic_system.economy_manager import EconomyManager

class ShopItem:
    """Represents an item that can be bought in a shop."""
    def __init__(self, item_id: str, name: str, description: str, price: float):
        self.item_id = item_id  # A unique identifier, e.g., "healing_potion_minor"
        self.name = name
        self.description = description
        self.price = price

class Shop:
    """Represents a shop that holds a collection of items for sale."""
    def __init__(self, name: str, owner_id: int, inventory: List[ShopItem]):
        self.name = name
        self.owner_id = owner_id
        self.inventory: Dict[str, ShopItem] = {item.item_id: item for item in inventory}

    def get_item(self, item_id: str) -> Optional[ShopItem]:
        """Gets a specific item from the shop's inventory."""
        return self.inventory.get(item_id)

class ShopManager:
    """Manages all shops and handles the purchasing process."""
    def __init__(self, economy_manager: EconomyManager):
        self.economy_manager = economy_manager
        self.shops: List[Shop] = []
        logging.info("ShopManager initialized.")

    def create_shop(self, owner_id: int, shop_name: str, inventory: List[ShopItem]):
        """Creates a new shop and adds it to the manager."""
        shop = Shop(name=shop_name, owner_id=owner_id, inventory=inventory)
        self.shops.append(shop)
        logging.info(f"New shop '{shop_name}' created, owned by user {owner_id}.")

    def load_initial_shops(self, all_characters: List[Character]):
        """Loads the default, system-defined shops like Eka's."""
        eka_char = next((c for c in all_characters if c.name == "Eka"), None)
        if eka_char and eka_char.discord_id:
            general_store_items = [
                ShopItem("food_ration", "Food Ration", "A day's worth of basic, nutritious food.", 5.0),
                ShopItem("healing_potion", "Healing Potion", "A standard potion that restores health.", 20.0),
                ShopItem("book_of_tales", "Book of Tales", "A collection of short stories from faraway lands.", 15.0),
                ShopItem("luxurious_fabric", "Luxurious Fabric", "Fine cloth for creating beautiful garments.", 50.0),
            ]
            self.create_shop(eka_char.discord_id, "Eka's Emporium", general_store_items)
        else:
            logging.warning("Could not create Eka's shop because her character object or discord_id was not found.")

    def get_all_items_for_sale(self) -> Dict[str, List[Dict]]:
        """Returns a structured list of all items from all shops."""
        shop_inventories = {}
        for shop in self.shops:
            shop_inventories[shop.name] = [
                {"id": item.item_id, "name": item.name, "price": item.price, "desc": item.description}
                for item in shop.inventory.values()
            ]
        return shop_inventories

    def purchase_item(self, character: Character, item_id: str) -> bool:
        """Handles the logic for a character purchasing an item."""
        if not character.discord_id:
            logging.error(f"Cannot process purchase for {character.name} without discord_id.")
            return False

        item_to_buy: Optional[ShopItem] = None
        shop_owner_id: Optional[int] = None

        for shop in self.shops:
            item = shop.get_item(item_id)
            if item:
                item_to_buy = item
                shop_owner_id = shop.owner_id
                break

        if not item_to_buy or shop_owner_id is None:
            logging.warning(f"Character {character.name} tried to buy non-existent item '{item_id}'.")
            return False

        logging.info(f"Character {character.name} is attempting to purchase '{item_to_buy.name}' for {item_to_buy.price} Rs.")

        success = self.economy_manager.make_transaction(
            from_user_id=character.discord_id,
            to_user_id=shop_owner_id,
            amount=item_to_buy.price,
            description=f"Purchase of item: {item_to_buy.name}"
        )

        if success:
            logging.info(f"{character.name} successfully purchased {item_to_buy.name}.")
            # In a full implementation, the item would be added to the character's inventory here.
        else:
            logging.warning(f"Purchase failed for {character.name}. Insufficient funds for '{item_to_buy.name}'.")

        return success