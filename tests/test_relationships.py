import unittest
import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from core.personas import get_all_personas
from core.relationships import RelationshipManager

class TestRelationships(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """Set up for all tests in this class."""
        all_personas = get_all_personas()
        cls.rel_manager = RelationshipManager(all_personas)

    def test_relationship_manager_initialization(self):
        """Test that the RelationshipManager initializes correctly."""
        self.assertIsInstance(self.rel_manager, RelationshipManager)
        self.assertIsNotNone(self.rel_manager.matrix)
        # Check if the matrix is populated
        self.assertGreater(len(self.rel_manager.matrix), 0)

    def test_get_specific_relationship(self):
        """Test retrieving a specific, defined relationship."""
        # Test Eka's relationship to the Master
        relationship = self.rel_manager.get_relationship("Eka", "Master")
        self.assertEqual(relationship, "Absolute devotion and submission (Mommy Persona)")

        # Test Sapt's relationship to the Master
        relationship_sapt = self.rel_manager.get_relationship("Sapt", "Master")
        self.assertEqual(relationship_sapt, "Absolute violent submission, exclusive for NSFW")

    def test_get_relationship_case_insensitivity(self):
        """Test that the source persona name is case-insensitive."""
        relationship_lower = self.rel_manager.get_relationship("eka", "Master")
        relationship_upper = self.rel_manager.get_relationship("EKA", "Master")
        self.assertEqual(relationship_lower, "Absolute devotion and submission (Mommy Persona)")
        self.assertEqual(relationship_upper, "Absolute devotion and submission (Mommy Persona)")

        # The implementation uses .capitalize() on the target, so "master" becomes "Master".
        # The test should reflect this correct behavior.
        relationship_target_case = self.rel_manager.get_relationship("Eka", "master")
        self.assertEqual(relationship_target_case, "Absolute devotion and submission (Mommy Persona)")

    def test_get_undefined_relationship(self):
        """Test retrieving a relationship that is not explicitly defined."""
        # Assuming Dvi has no defined relationship to Tri in the persona file
        relationship = self.rel_manager.get_relationship("Dvi", "Tri")
        self.assertEqual(relationship, "Neutral")

    def test_get_relationship_from_nonexistent_persona(self):
        """Test retrieving a relationship from a persona that doesn't exist."""
        relationship = self.rel_manager.get_relationship("NonExistent", "Master")
        self.assertEqual(relationship, "Neutral")

    def test_get_all_relationships_for_persona(self):
        """Test retrieving all relationships for a specific persona (Maya)."""
        maya_relations = self.rel_manager.get_all_relationships("Maya")
        self.assertIsInstance(maya_relations, dict)
        self.assertIn("Master", maya_relations)
        self.assertIn("DashaRakshakas", maya_relations)
        self.assertEqual(maya_relations["Master"], "Absolute love, devotion, and exclusivity")

    def test_relationship_matrix_structure(self):
        """Test the structure of the internal relationship matrix."""
        self.assertIn("maya", self.rel_manager.matrix)
        self.assertIn("eka", self.rel_manager.matrix)
        self.assertIsInstance(self.rel_manager.matrix['maya'], dict)
        self.assertNotIn("yashvardhan", self.rel_manager.matrix) # Yashvardhan is not a controllable bot

if __name__ == '__main__':
    unittest.main()