import logging
from core.character_system.personas import Persona
from .economy_manager import EconomyManager

class JobManager:
    """
    Manages the jobs available in the world, their requirements, and their payouts.
    """
    def __init__(self, economy_manager: EconomyManager):
        self.economy_manager = economy_manager
        self.logger = logging.getLogger(__name__)
        # Define a diverse set of jobs as per the blueprint
        self.jobs = {
            "Alchemist": {"payout": 150, "description": "Brew potions and elixirs in a bubbling lab."},
            "Blacksmith": {"payout": 120, "description": "Forge weapons and armor at a roaring hearth."},
            "Scribe": {"payout": 80, "description": "Copy ancient scrolls and write official documents."},
            "Bodyguard": {"payout": 200, "description": "Protect a client for a day with unwavering vigilance."},
            "Courtesan": {"payout": 500, "description": "Provide high-class companionship and entertainment in the Velvet District."},
            "Hunter": {"payout": 130, "description": "Track and hunt beasts in the wilderness for valuable parts."},
            "Enchanter": {"payout": 170, "description": "Imbue items with magical properties."},
            "Spy": {"payout": 400, "description": "Gather sensitive information for a high price."}
        }
        # Simple mapping of character to their primary job
        self.job_map = {
            "Maya": "Scribe",
            "Eka": "Courtesan",
            "Dvi": "Bodyguard",
            "Tri": "Scribe",
            "Chatur": "Blacksmith",
            "Panch": "Alchemist",
            "Shash": "Enchanter",
            "Sapt": "Spy",
            "Asht": "Courtesan",
            "Nav": "Alchemist",
            "Dash": "Spy"
        }


    async def perform_work(self, persona: Persona) -> str:
        """
        Determines a character's job based on their persona and processes the work action.

        Args:
            persona: The Persona object of the character working.

        Returns:
            A string describing the work action for announcement.
        """
        job_name = self.job_map.get(persona.name)

        if not job_name:
            self.logger.warning(f"{persona.name} has no assigned job.")
            return f"*{persona.name} spent the day pondering their career choices.*"

        job_info = self.jobs.get(job_name)
        if not job_info:
            self.logger.error(f"Job '{job_name}' not found for {persona.name}.")
            return f"*{persona.name} tried to work as a {job_name}, but the job doesn't seem to exist.*"

        income = job_info["payout"]

        # Update balance using the economy manager
        success = self.economy_manager.update_balance(persona.name, income)

        if success:
            self.logger.info(f"{persona.name} worked as a {job_name} and earned {income} Rs.")
            return f"*{persona.name}, the {job_name}, has finished their work for the day, earning {income} Rs.*"
        else:
            # This case should ideally not happen for earning money
            self.logger.error(f"Failed to credit {income} Rs to {persona.name} for their work.")
            return f"*{persona.name} worked hard as a {job_name}, but a clerical error prevented their payment.*"