import unittest
import os
import json
import time
from src.core.personas import PersonaManager, Persona
from src.core.economic_system.economy_manager import EconomyManager

class TestNewFeatures(unittest.TestCase):

    def setUp(self):
        """Set up for testing new features."""
        self.persona_manager = PersonaManager(kink_file_path="non_existent_file.json")
        self.db_path = "tests/test_world.db"
        self.economy_manager = EconomyManager(db_path=self.db_path)

        # Get some personas for testing
        self.eka = self.persona_manager.get_persona("Eka")
        self.dvi = self.persona_manager.get_persona("Dvi")

    def tearDown(self):
        """Clean up the test database."""
        if os.path.exists(self.db_path):
            os.remove(self.db_path)

    def test_infinite_regeneration_system(self):
        """Test both scene-based injury and duel-based regeneration."""
        # Test scene-based injury and healing
        self.assertEqual(self.eka.status, "Healthy")
        self.eka.inflict_injury("right_wing", "torn")
        self.assertEqual(self.eka.status, "Injured")
        self.assertIn("right_wing", self.eka.injuries)
        self.eka.heal_all_injuries()
        self.assertEqual(self.eka.status, "Healthy")
        self.assertEqual(len(self.eka.injuries), 0)

        # Test duel-based regeneration timeout
        self.eka.set_regenerating(0.1)  # Use a very short duration for the test
        self.assertEqual(self.eka.status, "Regenerating")
        self.assertIsNotNone(self.eka.regeneration_end_time)

        # Wait for the regeneration timer to expire
        time.sleep(0.2)

        # Check if the status is updated correctly after checking
        self.assertTrue(self.eka.check_regeneration())
        self.assertEqual(self.eka.status, "Healthy")

    def test_corruption_system(self):
        """Test the sanity meter adjustment."""
        initial_sanity = self.dvi.emotions['sanity']
        self.assertEqual(initial_sanity, 100)

        # Simulate a traumatic event
        self.dvi.adjust_emotion('sanity', -30)
        self.assertEqual(self.dvi.emotions['sanity'], 70)

    def test_gilded_cage_system(self):
        """Test the servitude functionality."""
        # Initial state: Dvi should not be in servitude
        self.assertIsNone(self.economy_manager.is_in_servitude("Dvi"))

        # Put Dvi into servitude
        self.economy_manager.enter_servitude(character_name="Dvi", owner_name="Eka", debt_amount=5000)
        owner = self.economy_manager.is_in_servitude("Dvi")
        self.assertEqual(owner, "Eka")

        # Free Dvi
        self.economy_manager.free_from_servitude("Dvi")
        self.assertIsNone(self.economy_manager.is_in_servitude("Dvi"))

    def test_masters_cult_system(self):
        """Test the cult leader assignment."""
        self.assertIsNone(self.eka.faction)
        self.assertFalse(self.eka.is_cult_leader)

        self.eka.is_cult_leader = True
        self.eka.faction = "Eka's Embrace"

        self.assertTrue(self.eka.is_cult_leader)
        self.assertEqual(self.eka.faction, "Eka's Embrace")

if __name__ == '__main__':
    unittest.main()