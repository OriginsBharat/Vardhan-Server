import unittest
import os
import json
from src.core.personas import PersonaManager, Persona
from src.core.economic_system.economy_manager import EconomyManager

class TestCoreSystems(unittest.TestCase):

    def setUp(self):
        """Set up a temporary testing environment."""
        # Create dummy data files
        self.canon_data = {
            "Maya": {
                "description": "Test AI",
                "base_persona": "You are a test AI.",
                "aura_color": "0xFFFFFF"
            }
        }
        self.kinks_data = {
            "Maya": ["testing", "debugging"]
        }
        os.makedirs("data", exist_ok=True)
        with open("data/character_canon.json", "w") as f:
            json.dump(self.canon_data, f)
        with open("data/character_kinks.json", "w") as f:
            json.dump(self.kinks_data, f)

        # Setup a dummy bot object for the manager
        class DummyBot:
            pass
        self.bot = DummyBot()

        self.persona_manager = PersonaManager(self.bot)

        # Setup economy manager with a test database
        self.test_db = "data/test_world.db"
        self.economy_manager = EconomyManager(db_path=self.test_db)

    def tearDown(self):
        """Clean up the testing environment."""
        os.remove("data/character_canon.json")
        os.remove("data/character_kinks.json")
        if os.path.exists(self.test_db):
            os.remove(self.test_db)

    def test_persona_loading(self):
        """Test if personas are loaded correctly."""
        # This needs to be async in a real test runner, but for a simple check:
        import asyncio
        asyncio.run(self.persona_manager.initialize_personas())

        self.assertIn("Maya", self.persona_manager.personas)
        maya_persona = self.persona_manager.get_persona("Maya")
        self.assertIsInstance(maya_persona, Persona)
        self.assertEqual(maya_persona.name, "Maya")
        self.assertEqual(maya_persona.kinks, ["testing", "debugging"])

    def test_economy_balance(self):
        """Test wallet creation and balance updates."""
        character = "Maya"
        # Initial balance should be 0
        self.assertEqual(self.economy_manager.get_balance(character), 0)

        # Test adding funds
        self.economy_manager.update_balance(character, 100)
        self.assertEqual(self.economy_manager.get_balance(character), 100)

        # Test subtracting funds
        self.economy_manager.update_balance(character, -50)
        self.assertEqual(self.economy_manager.get_balance(character), 50)

        # Test a new character
        new_char = "Eka"
        self.assertEqual(self.economy_manager.get_balance(new_char), 0)
        self.economy_manager.update_balance(new_char, 500)
        self.assertEqual(self.economy_manager.get_balance(new_char), 500)

if __name__ == '__main__':
    unittest.main()