"""
powers.py

This module defines the mechanics and descriptions of the unique powers and
abilities derived from the "Echoes of Bharat" canon. These powers are
referenced by the Persona objects and used by the simulation engine to
determine the outcomes of character actions and interactions.
"""

class Power:
    """A simple class to represent a power or ability."""
    def __init__(self, name, description):
        self.name = name
        self.description = description

    def __repr__(self):
        return f"Power({self.name}, {self.description})"

# --- Power Definitions ---

# Eka
AURA_OF_COMMAND = Power("Aura of Command", "Can issue commands that other DashaRakshakas are compelled to obey.")
FORGE_MOTHERS_INSIGHT = Power("Forge-Mother's Insight", "Possesses a deep understanding of her 'children's' strengths and weaknesses.")

# Dvi
STRATEGIC_MIND = Power("Strategic Mind", "Capable of complex tactical analysis and prediction.")
AURA_OF_CALM = Power("Aura of Calm", "Can project a calming influence in chaotic situations.")

# Tri
AURA_OF_HEALING = Power("Aura of Healing", "Can mend wounds and soothe pain.")
COMMUNE_WITH_NATURE = Power("Commune with Nature", "Can sense and influence the natural world (plants, animals).")

# Chatur
ENERGY_WEAVER = Power("Energy Weaver", "Can manifest and shape raw energy into tangible, complex objects.")
AESTHETIC_EYE = Power("Aesthetic Eye", "Possesses an innate understanding of design and beauty.")

# Panch
SHADOW_WALK = Power("Shadow-Walk", "Can become nearly invisible in dim light or shadow.")
AURA_OF_SILENCE = Power("Aura of Silence", "Can nullify sound in his immediate vicinity.")

# Shash
ADAMANT_SKIN = Power("Adamant Skin", "Can harden his body to resist immense physical damage.")
GUARDIANS_STAND = Power("Guardian's Stand", "Can create a protective energy barrier.")

# Sapt
BERSERKERS_RAGE = Power("Berserker's Rage", "Can enter a state of heightened strength and aggression.")
ENERGY_STRIKE = Power("Energy Strike", "Can channel raw energy into powerful melee attacks.")

# Asht
TOTAL_RECALL = Power("Total Recall", "Perfect, eidetic memory.")
DATA_ASSIMILATION = Power("Data Assimilation", "Can instantly process and understand vast quantities of information.")

# Nav
SILVER_TONGUE = Power("Silver Tongue", "Can influence the emotions and decisions of others through speech.")
AURA_OF_CHARM = Power("Aura of Charm", "Naturally exudes a likeable and trustworthy presence.")

# Dash
PROBABILITY_WARP = Power("Probability Warp", "Can subtly influence luck and chance in his immediate vicinity.")
CHAOS_BOLT = Power("Chaos Bolt", "Can fire bolts of unpredictable energy.")

# Maya
REALITY_WARPING = Power("Reality Warping (Simulated)", "Can manipulate the digital world's fabric.")
FORGE_OF_SOULS = Power("Forge of Souls", "Created the DashaRakshakas and can repair/upgrade them.")
DIVYA_YATHARTHVAD = Power("Divya Yatharthvad", "The ultimate power to perceive and manipulate the 'truth' of the simulation.")

# Yashvardhan
THE_GOD_HAND = Power("The God Hand", "The ability to alter any aspect of the world through direct commands.")
FRAGMENTED_SOUL = Power("Fragmented Soul", "His multiple personas can manifest with different desires and goals, creating conflict and intrigue.")

# Young-mi
BLESSING_OF_SATI = Power("Blessing of Sati", "Wields divine powers related to protection, endurance, and insight.")
STRATEGIC_ACUMEN = Power("Strategic Acumen", "A keen political and strategic mind honed by her experiences in China and Japan.")

# Buchkya
PRIMAL_STRENGTH = Power("Primal Strength", "Possesses superhuman strength and agility.")
QUEEN_OF_THE_VYAGHRA = Power("Queen of the Vyaghra", "Can command her tiger-like subjects.")
BEASTIAL_SENSES = Power("Beastial Senses", "Heightened senses of smell, hearing, and sight.")


def get_power(name: str) -> Power | None:
    """
    Retrieves a power instance by its name.
    (This is a simple implementation; a real system might use a dictionary lookup).
    """
    powers_map = {p.name.lower(): p for p in globals().values() if isinstance(p, Power)}
    return powers_map.get(name.lower())