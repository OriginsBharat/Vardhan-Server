class RelationshipManager:
    """
    Manages the social web of relationships between all characters.
    Relationships are stored as a symmetrical matrix.
    """
    def __init__(self, persona_manager):
        self.personas = persona_manager.get_all_personas()
        self.character_names = [p.name for p in self.personas]
        # Initialize an empty matrix (dictionary of dictionaries)
        self.matrix = {name: {other: 0 for other in self.character_names} for name in self.character_names}

    def get_relationship_score(self, char1_name, char2_name):
        """
        Gets the relationship score between two characters.
        The score is symmetrical, so char1 -> char2 is the same as char2 -> char1.
        """
        return self.matrix.get(char1_name, {}).get(char2_name, 0)

    def update_relationship(self, char1_name, char2_name, value_change):
        """
        Updates the relationship score between two characters by a certain value.
        """
        if char1_name not in self.matrix or char2_name not in self.matrix:
            print(f"[ERROR] Invalid character name provided to RelationshipManager.")
            return

        # Update both sides of the relationship to keep it symmetrical
        self.matrix[char1_name][char2_name] += value_change
        self.matrix[char2_name][char1_name] += value_change

        new_score = self.matrix[char1_name][char2_name]
        print(f"[Relationship] {char1_name} and {char2_name}'s relationship score changed by {value_change}. New score: {new_score}")

    def get_relationships_for_character(self, character_name):
        """
        Returns a dictionary of a character's relationships with all other characters.
        """
        return self.matrix.get(character_name, {})