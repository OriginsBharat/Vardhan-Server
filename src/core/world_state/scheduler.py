# src/core/world_state/scheduler.py
# Manages the daily schedules and online presence of all bots.

import asyncio
import logging
from datetime import datetime
from typing import List, Optional

import discord

from src.core.character_system.personas import Character
from src.core.economic_system.jobs import JobManager

class Scheduler:
    """
    Manages the timetables for all characters. It checks the current time
    and triggers scheduled events like 'wake_up', 'work', and 'sleep',
    and updates the bot's Discord presence accordingly.
    """
    def __init__(self, characters: List[Character], client: discord.Client, job_manager: JobManager):
        self.characters = characters
        self.client = client
        self.job_manager = job_manager
        self._loop_task: Optional[asyncio.Task] = None
        logging.info("Scheduler initialized.")

    def start_loop(self):
        """Starts the background loop to run the scheduler."""
        if self._loop_task is None or self._loop_task.done():
            self._loop_task = asyncio.create_task(self._run_schedule_loop())
            logging.info("Scheduler background loop started.")

    async def _run_schedule_loop(self):
        """The main loop that periodically checks and executes scheduled tasks."""
        await self.client.wait_until_ready()
        while not self.client.is_closed():
            now_str = datetime.now().strftime("%H:%M")

            for char in self.characters:
                if not char.discord_id: continue # Skip if bot is not fully loaded

                # Check the schedule for the current time
                scheduled_activity = char.schedule.get(now_str)
                if not scheduled_activity: continue

                logging.info(f"Scheduler: It's {now_str}, time for {char.name} to '{scheduled_activity}'.")

                # --- Execute Scheduled Activity ---
                if scheduled_activity == "wake_up":
                    char.status = "Online"
                    await self.update_presence(char, status=discord.Status.online)

                elif scheduled_activity == "sleep":
                    char.status = "Sleeping"
                    await self.update_presence(char, status=discord.Status.idle, activity_name="Dreaming...")

                elif scheduled_activity == "work":
                    job = self.job_manager.get_job_for_character(char)
                    if job:
                        char.status = f"Working ({job.name})"
                        self.job_manager.perform_job(char, job)
                        await self.update_presence(char, status=discord.Status.online, activity_name=f"Working: {job.name}")

                elif scheduled_activity == "leisure":
                    char.status = "Leisure"
                    await self.update_presence(char, status=discord.Status.online, activity_name="Enjoying some free time.")

                # Can add more activity types here

            # Check every 60 seconds
            await asyncio.sleep(60)

    async def update_presence(self, character: Character, status: discord.Status, activity_name: Optional[str] = None):
        """Updates a specific bot's presence on Discord."""
        # This is complex because we are running all bots under one client.
        # A true multi-bot application would have separate clients.
        # For this project, we'll update the main client's presence to reflect
        # the activity of the *last scheduled character* as a proxy.
        # A more advanced implementation would require one bot process per character.

        activity = discord.Game(name=activity_name) if activity_name else None
        await self.client.change_presence(status=status, activity=activity)
        logging.info(f"Updated presence for {character.name}: Status={status}, Activity='{activity_name}'")