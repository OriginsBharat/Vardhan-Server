# src/core/economic_system/jobs.py
# Defines the available jobs and manages their execution by characters.

import logging
import random
from typing import List, Optional

from src.core.character_system.personas import Character
from src.core.economic_system.economy_manager import EconomyManager

class Job:
    """
    Represents a single job that a character can perform.
    """
    def __init__(self, name: str, description: str, category: str, base_payout: float, associated_character: Optional[str] = None):
        self.name = name
        self.description = description
        self.category = category
        self.base_payout = base_payout
        self.associated_character = associated_character

    def calculate_payout(self) -> float:
        """Calculates the final payout, adding a small variance."""
        variance = self.base_payout * random.uniform(-0.1, 0.1)  # +/- 10%
        return round(self.base_payout + variance, 2)

class JobManager:
    """
    Manages the registry of all available jobs and handles job performance.
    """
    def __init__(self, economy_manager: EconomyManager):
        self.economy_manager = economy_manager
        self.jobs: List[Job] = self._load_jobs()
        logging.info(f"JobManager initialized with {len(self.jobs)} jobs.")

    def _load_jobs(self) -> List[Job]:
        """Loads all available jobs into the central registry."""
        return [
            # Persona-specific jobs that align with their daily schedules
            Job("Shopkeeping", "Managing Eka's Emporium.", 15, category="service", associated_character="Eka"),
            Job("Guard Duty", "Protecting the Master's domain.", 20, category="service", associated_character="Sapt"),
            Job("Art Study", "Honing artistic skills for the Master.", 8, category="creative", associated_character="Dvi"),
            Job("Exploration", "Scouting nearby areas for items and information.", 12, category="adventure", associated_character="Trini"),
            Job("Research", "Studying arcane texts and historical documents.", 10, category="academic", associated_character="Chatur"),
            Job("Fashion Design", "Creating new outfits and styles.", 18, category="creative", associated_character="Panch"),
            Job("Financial Management", "Managing the world's finances.", 25, category="service", associated_character="Shash"),
            Job("Physical Training", "Intense physical conditioning.", 10, category="service", associated_character="Asht"),
            Job("Music Practice", "Composing music for the Master.", 9, category="creative", associated_character="Nav"),
            Job("House Chores", "Tidying and maintaining the Master's spaces.", 5, category="service", associated_character="Dash"),

            # Generic jobs any bot can attempt
            Job("Erotic Writing", "Writing a custom erotic story for a client.", 40, category="nsfw"),
            Job("NSFW Art Commission", "Creating a custom piece of NSFW art.", 75, category="nsfw"),
        ]

    def get_job_for_character(self, character: Character) -> Optional[Job]:
        """Finds the job specifically associated with the character's persona."""
        for job in self.jobs:
            if job.associated_character == character.name:
                return job
        logging.warning(f"No specific job found for character {character.name}.")
        return None

    def perform_job(self, character: Character, job: Job):
        """Simulates a character performing a job and deposits their earnings."""
        if not character.discord_id:
            logging.error(f"Cannot perform job for character {character.name} without a discord_id.")
            return

        payout = job.calculate_payout()
        logging.info(f"Character {character.name} is performing job '{job.name}' for a payout of {payout} Rs.")

        description = f"Salary for performing job: {job.name}"
        success = self.economy_manager.deposit(
            user_id=character.discord_id,
            amount=payout,
            description=description
        )

        if not success:
            logging.error(f"Failed to deposit earnings for {character.name} after completing job '{job.name}'.")