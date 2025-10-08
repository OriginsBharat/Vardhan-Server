import unittest
import os
import json
from src.core.personas import PersonaManager

class TestPersonaManager(unittest.TestCase):

    def setUp(self):
        """Set up a temporary kink file for testing."""
        self.kink_file_path = "tests/temp_kinks.json"
        kink_data = {
            "Maya": ["test_kink_1", "test_kink_2"],
            "Eka": ["domination"]
        }
        with open(self.kink_file_path, "w") as f:
            json.dump(kink_data, f)

        self.persona_manager = PersonaManager(kink_file_path=self.kink_file_path)

    def tearDown(self):
        """Clean up the temporary kink file."""
        if os.path.exists(self.kink_file_path):
            os.remove(self.kink_file_path)

    def test_load_base_personas(self):
        """Test that all 11 base personas are loaded correctly."""
        self.assertEqual(len(self.persona_manager.get_all_personas()), 11)

    def test_get_persona(self):
        """Test retrieving a specific persona."""
        maya = self.persona_manager.get_persona("Maya")
        self.assertIsNotNone(maya)
        self.assertEqual(maya.name, "Maya")

        # Test case-insensitivity
        eka = self.persona_manager.get_persona("eka")
        self.assertIsNotNone(eka)
        self.assertEqual(eka.name, "Eka")

    def test_load_kinks(self):
        """Test that kinks are loaded and merged correctly."""
        maya = self.persona_manager.get_persona("Maya")
        self.assertEqual(len(maya.kinks), 2)
        self.assertIn("test_kink_1", maya.kinks)

        eka = self.persona_manager.get_persona("Eka")
        self.assertEqual(eka.kinks, ["domination"])

        # Test that a character not in the file has no kinks
        dvi = self.persona_manager.get_persona("Dvi")
        self.assertEqual(dvi.kinks, [])

if __name__ == '__main__':
    unittest.main()