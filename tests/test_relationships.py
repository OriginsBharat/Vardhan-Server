import unittest
from src.core.personas import PersonaManager
from src.core.relationships import RelationshipManager

class TestRelationshipManager(unittest.TestCase):

    def setUp(self):
        """Set up a persona manager for relationship testing."""
        # We use a mock PersonaManager that doesn't load kinks for this test
        self.persona_manager = PersonaManager(kink_file_path="non_existent_file.json")
        self.relationship_manager = RelationshipManager(self.persona_manager)

    def test_initial_relationships(self):
        """Test that initial relationship scores are set to 0."""
        score = self.relationship_manager.get_relationship_score("Maya", "Eka")
        self.assertEqual(score, 0)

    def test_update_relationship(self):
        """Test updating a relationship score."""
        self.relationship_manager.update_relationship("Maya", "Eka", 10)
        score = self.relationship_manager.get_relationship_score("Maya", "Eka")
        self.assertEqual(score, 10)

        # Test updating again
        self.relationship_manager.update_relationship("Maya", "Eka", -5)
        score = self.relationship_manager.get_relationship_score("Maya", "Eka")
        self.assertEqual(score, 5)

    def test_symmetrical_relationship(self):
        """Test that relationships are symmetrical (A to B is the same as B to A)."""
        self.relationship_manager.update_relationship("Dvi", "Tri", 25)
        score1 = self.relationship_manager.get_relationship_score("Dvi", "Tri")
        score2 = self.relationship_manager.get_relationship_score("Tri", "Dvi")
        self.assertEqual(score1, score2)
        self.assertEqual(score2, 25)

    def test_get_relationships_for_character(self):
        """Test retrieving all relationships for a specific character."""
        self.relationship_manager.update_relationship("Asht", "Dash", 50)
        self.relationship_manager.update_relationship("Asht", "Nav", -20)

        asht_relationships = self.relationship_manager.get_relationships_for_character("Asht")

        self.assertIn("Dash", asht_relationships)
        self.assertEqual(asht_relationships["Dash"], 50)
        self.assertIn("Nav", asht_relationships)
        self.assertEqual(asht_relationships["Nav"], -20)

if __name__ == '__main__':
    unittest.main()