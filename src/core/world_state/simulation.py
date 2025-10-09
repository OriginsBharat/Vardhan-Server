import logging
from datetime import datetime, timedelta
import asyncio
import discord

class SimulationManager:
    """
    Manages the offline progression simulation.
    When the bot starts, this class calculates what should have happened
    while it was offline to maintain the illusion of a 24/7 world.
    """
    def __init__(self, bot):
        self.bot = bot
        self.logger = logging.getLogger(__name__)
        self.last_online_file = "data/last_online.txt"

    def get_last_online_time(self) -> datetime:
        """Reads the last online timestamp from a file."""
        try:
            with open(self.last_online_file, 'r') as f:
                timestamp_str = f.read().strip()
                return datetime.fromisoformat(timestamp_str)
        except (FileNotFoundError, ValueError):
            self.logger.warning("Last online time not found, assuming this is the first run.")
            # On first run, we don't want to simulate anything.
            self.record_current_time()
            return datetime.now()

    def record_current_time(self):
        """Writes the current timestamp to the last online file."""
        try:
            with open(self.last_online_file, 'w') as f:
                f.write(datetime.now().isoformat())
        except Exception as e:
            self.logger.error(f"Failed to record current time: {e}")

    async def run_offline_simulation(self):
        """
        Runs the simulation for the period the bot was offline.
        """
        await self.bot.wait_until_ready()
        last_online = self.get_last_online_time()
        now = datetime.now()
        time_offline = now - last_online

        # Only run simulation for significant downtime (e.g., more than 5 minutes)
        if time_offline.total_seconds() < 300:
            self.logger.info("Bot was offline for a very short period. Skipping simulation.")
            # Still record the current time to mark the bot as having been online.
            self.record_current_time()
            return

        self.logger.info(f"Bot was offline for {time_offline}. Running simulation...")

        # Announce the start of the simulation
        announcement_channel = discord.utils.get(self.bot.get_all_channels(), name='announcements')
        if announcement_channel:
            await announcement_channel.send(
                f"**[SYSTEM]** The world awakens after a slumber of {str(time_offline).split('.')[0]}.\n"
                f"Simulating the lost time... The world is catching up."
            )

        # Iterate through each minute the bot was offline
        current_sim_time = last_online
        while current_sim_time < now:
            for persona in self.bot.persona_manager.personas.values():
                # We reuse the scheduler's logic to check for events
                await self.bot.scheduler.handle_scheduled_event(persona, current_sim_time.time())

            # Increment by one minute
            current_sim_time += timedelta(minutes=1)
            # Add a small sleep to prevent blocking the event loop entirely during a long simulation
            if current_sim_time.minute % 30 == 0: # Sleep every 30 simulated minutes
                 await asyncio.sleep(0.01)


        self.logger.info("Offline simulation complete.")

        if announcement_channel:
            await announcement_channel.send(
                f"**[SYSTEM]** The simulation is complete. The world has caught up to the present moment."
            )

        # IMPORTANT: Record the new "last online" time *after* the simulation is done.
        self.record_current_time()