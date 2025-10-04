# src/core/world_state/simulation.py
# Implements Codename "The Simulation" for offline world progression.

import logging
from datetime import datetime, timedelta
from typing import List
import os

from src.core.character_system.personas import Character
from src.core.economic_system.job_manager import JobManager

LAST_ONLINE_FILE = "data/last_online.txt"

class SimulationManager:
    """
    Manages the simulation of world events and character actions during the bot's downtime.
    """
    def __init__(self, characters: List[Character], job_manager: JobManager):
        self.characters = characters
        self.job_manager = job_manager
        logging.info("SimulationManager initialized.")

    def save_shutdown_time(self):
        """Saves the current timestamp to a file upon clean shutdown."""
        try:
            with open(LAST_ONLINE_FILE, "w") as f:
                f.write(datetime.utcnow().isoformat())
            logging.info(f"Saved shutdown time to {LAST_ONLINE_FILE}.")
        except Exception as e:
            logging.error(f"Failed to save shutdown time: {e}")

    def run_offline_simulation(self):
        """
        Calculates the downtime and simulates character progression for that period.
        This should be called once at startup.
        """
        if not os.path.exists(LAST_ONLINE_FILE):
            logging.info("No previous shutdown time found. Skipping offline simulation.")
            return

        try:
            with open(LAST_ONLINE_FILE, "r") as f:
                last_online_str = f.read()
            last_online_time = datetime.fromisoformat(last_online_str)
        except Exception as e:
            logging.error(f"Failed to read or parse last shutdown time: {e}")
            return

        downtime = datetime.utcnow() - last_online_time
        if downtime <= timedelta(minutes=1):
            logging.info("Downtime was less than a minute. Skipping simulation.")
            return

        logging.info(f"World has been offline for {downtime}. Starting high-speed simulation.")

        # Simulate in hourly increments
        simulated_hours = int(downtime.total_seconds() / 3600)
        if simulated_hours == 0:
            logging.info("Downtime less than an hour, no simulation steps to run.")
            return

        for hour_offset in range(simulated_hours):
            sim_time = last_online_time + timedelta(hours=hour_offset)
            sim_time_str = sim_time.strftime("%H:00") # Check schedule on the hour

            for char in self.characters:
                scheduled_activity = char.schedule.get(sim_time_str)
                if scheduled_activity == "work":
                    job = self.job_manager.get_job_for_character(char)
                    if job:
                        # In a simulation, we don't need to update presence, just process the economics.
                        logging.info(f"[SIM] Simulating work for {char.name} at hour {hour_offset+1}/{simulated_hours}.")
                        self.job_manager.perform_job(char, job)

        logging.info(f"Completed simulation of {simulated_hours} hours of offline activity.")