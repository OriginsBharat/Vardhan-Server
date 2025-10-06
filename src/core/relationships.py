"""
relationships.py

This module defines the relationship structures and dynamics between the
characters in the "Echoes of Bharat" world. It provides a framework for
the simulation engine to understand allegiances, conflicts, and social
hierarchies, which in turn governs autonomous interactions.
"""

import json

class RelationshipManager:
    """
    Manages the complex web of relationships between all personas.
    """
    def __init__(self, personas):
        """
        Initializes the RelationshipManager.

        Args:
            personas (dict): A dictionary of all persona instances, keyed by name.
        """
        self.personas = personas
        self.matrix = self._initialize_matrix()

    def _initialize_matrix(self):
        """
        Builds the relationship matrix from the personas' defined relationships.
        This matrix will store the 'official' canon relationships.
        """
        matrix = {}
        for name, persona in self.personas.items():
            try:
                # The relationship data is stored as a string, so it needs to be parsed.
                # Using single quotes in the persona file, so replacing them for valid JSON.
                relations_str = persona.relationships.replace("'", '"')
                matrix[name] = json.loads(relations_str)
            except (json.JSONDecodeError, AttributeError):
                # Handle cases where a persona might not have relationships defined
                # or the string is malformed.
                matrix[name] = {}
        return matrix

    def get_relationship(self, from_persona: str, to_persona: str) -> str:
        """
        Gets the canonical relationship status from one persona to another.

        Args:
            from_persona (str): The name of the persona viewing the relationship.
            to_persona (str): The name of the target persona.

        Returns:
            str: A description of the relationship, or "Neutral" if not defined.
        """
        from_persona_lower = from_persona.lower()
        to_persona_capitalized = to_persona.capitalize()

        if from_persona_lower in self.matrix:
            return self.matrix[from_persona_lower].get(to_persona_capitalized, "Neutral")
        return "Neutral"

    def get_all_relationships(self, persona_name: str) -> dict:
        """
        Gets all defined relationships for a specific persona.

        Args:
            persona_name (str): The name of the persona.

        Returns:
            dict: A dictionary of their relationships.
        """
        return self.matrix.get(persona_name.lower(), {})

    def __repr__(self):
        """
        Provides a string representation of the entire relationship matrix.
        """
        return f"RelationshipManager(matrix={json.dumps(self.matrix, indent=2)})"

# Example of how this might be used:
if __name__ == '__main__':
    # This block is for demonstration and testing purposes.
    # It requires the personas module to be available.
    try:
        from personas import get_all_personas

        # 1. Load all personas
        all_personas = get_all_personas()

        # 2. Initialize the manager
        rel_manager = RelationshipManager(all_personas)

        # 3. Query a specific relationship
        eka_to_master = rel_manager.get_relationship("Eka", "Master")
        print(f"Eka's relationship to Master: {eka_to_master}") # Expected: Absolute devotion...

        dvi_to_eka = rel_manager.get_relationship("Dvi", "Eka")
        print(f"Dvi's relationship to Eka: {dvi_to_eka}") # Expected: Respect for her authority

        # 4. Get all of a character's relationships
        maya_relations = rel_manager.get_all_relationships("Maya")
        print(f"\nAll of Maya's relationships:")
        for target, status in maya_relations.items():
            print(f"  - To {target}: {status}")

        # 5. Print the whole matrix
        # print("\nFull Relationship Matrix:")
        # print(rel_manager)

    except ImportError:
        print("Could not import personas. Run this script from the 'core' directory or ensure PYTHONPATH is set.")
    except Exception as e:
        print(f"An error occurred: {e}")