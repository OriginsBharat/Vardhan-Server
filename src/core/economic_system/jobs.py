import logging
from core.personas import Persona

class JobManager:
    """
    Manages the jobs available in the world, their requirements, and their payouts.
    """
    def __init__(self, economy_manager):
        self.economy_manager = economy_manager
        self.logger = logging.getLogger(__name__)
        self.jobs = {
            "Alchemist": {"payout": 150, "description": "Brew potions and elixirs."},
            "Blacksmith": {"payout": 120, "description": "Forge weapons and armor."},
            "Scribe": {"payout": 80, "description": "Copy scrolls and write documents."},
            "Bodyguard": {"payout": 200, "description": "Protect a client for a day."},
            "Courtesan": {"payout": 500, "description": "Provide companionship and entertainment."}
        }

    async def perform_work(self, persona: Persona):
        """
        Determines a character's job based on their persona and processes the work action.

        Args:
            persona: The Persona object of the character working.
        """
        # This is a simple placeholder logic. A more complex system would have
        # characters choose jobs, have skill requirements, etc.
        job_name = self._get_job_for_persona(persona.name)

        if not job_name:
            self.logger.warning(f"{persona.name} has no assigned job.")
            return

        job_info = self.jobs.get(job_name)
        if not job_info:
            self.logger.error(f"Job '{job_name}' not found for {persona.name}.")
            return

        income = job_info["payout"]
        self.economy_manager.update_balance(persona.name, income)
        self.logger.info(f"{persona.name} worked as a {job_name} and earned {income} Rs.")
        # We can return a message to be sent to a channel
        return f"{persona.name}, the {job_name}, has finished their work for the day, earning {income} Rs."

    def _get_job_for_persona(self, character_name: str) -> str:
        """
        Assigns a job based on character name. This is a simple mapping.
        """
        job_map = {
            "Maya": "Scribe",
            "Eka": "Courtesan",
            "Dvi": "Bodyguard",
            "Tri": "Scribe",
            "Chatur": "Blacksmith",
            "Panch": "Alchemist",
            "Shash": "Scribe", # Could be a merchant/banker later
            "Sapt": "Bodyguard",
            "Asht": "Courtesan",
            "Nav": "Alchemist",
            "Dash": "Courtesan"
        }
        return job_map.get(character_name)