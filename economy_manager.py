import json
import os
import random

class EconomyManager:
    def __init__(self, db_path='economy_db.json'):
        self.db_path = db_path
        self.data = self._load_db()

    def _load_db(self):
        """Loads the economy database from the JSON file."""
        try:
            with open(self.db_path, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            # This should not happen if the file is created correctly, but it's good practice
            print("ERROR: economy_db.json not found or is corrupted. A new one will be created.")
            return {
                "user_profiles": {"MASTER": {"wallet": 999999999, "inventory": []}},
                "bot_wallets": {},
                "shop_items": {}
            }

    def _save_db(self):
        """Saves the current state of the economy database to the JSON file."""
        with open(self.db_path, 'w') as f:
            json.dump(self.data, f, indent=4)

    def get_balance(self, bot_name):
        """Gets the wallet balance for a given bot."""
        return self.data['bot_wallets'].get(bot_name, 0)

    def get_shop_items(self):
        """Returns a dictionary of all items available in the shop."""
        return self.data.get('shop_items', {})

    def add_currency(self, bot_name, amount):
        """Adds a specified amount of currency to a bot's wallet."""
        if bot_name in self.data['bot_wallets']:
            self.data['bot_wallets'][bot_name] += amount
            self._save_db()
            return True
        return False

    def remove_currency(self, bot_name, amount):
        """Removes a specified amount of currency from a bot's wallet."""
        if bot_name in self.data['bot_wallets'] and self.data['bot_wallets'][bot_name] >= amount:
            self.data['bot_wallets'][bot_name] -= amount
            self._save_db()
            return True
        return False

    def buy_item(self, bot_name, item_name):
        """Allows a bot to buy an item from the shop."""
        shop_items = self.get_shop_items()
        if item_name not in shop_items:
            return f"I couldn't find '{item_name}' in the shop."

        item = shop_items[item_name]
        price = item['price']

        current_balance = self.get_balance(bot_name)
        if current_balance < price:
            return f"I can't afford '{item_name}'. I only have {current_balance} currency, but it costs {price}."

        if self.remove_currency(bot_name, price):
            # For now, buying an item just removes currency. Inventory tracking would be next.
            return f"I just bought '{item_name}' from the shop for {price} currency! My new balance is {self.get_balance(bot_name)}."
        else:
            return "Something went wrong with the transaction."

    def grant_salary(self, bot_name, base_salary=10):
        """Grants a small salary to a bot, maybe with a random bonus."""
        salary = base_salary + random.randint(0, 5)
        if self.add_currency(bot_name, salary):
            print(f"💰 Granted a salary of {salary} to {bot_name}.")
            return salary
        return 0