import logging
from datetime import datetime, timedelta

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
            return datetime.now()

    def record_current_time(self):
        """Writes the current timestamp to the last online file."""
        with open(self.last_online_file, 'w') as f:
            f.write(datetime.now().isoformat())

    async def run_offline_simulation(self):
        """
        Runs the simulation for the period the bot was offline.
        """
        last_online = self.get_last_online_time()
        now = datetime.now()
        time_offline = now - last_online

        if time_offline.total_seconds() < 120: # Don't run simulation for short downtimes
            self.logger.info("Bot was offline for a very short period. Skipping simulation.")
            self.record_current_time()
            return

        self.logger.info(f"Bot was offline for {time_offline}. Running simulation...")

        # Iterate through each minute the bot was offline
        current_sim_time = last_online
        while current_sim_time < now:
            for persona in self.bot.persona_manager.personas.values():
                # We reuse the scheduler's logic to check for events
                await self.bot.scheduler.check_and_trigger_action(persona, current_sim_time.time())

            current_sim_time += timedelta(minutes=1)

        self.logger.info("Offline simulation complete.")
        # Record the new "last online" time
        self.record_current_time()

        # Announce the simulation results
        channel = discord.utils.get(self.bot.get_all_channels(), name='announcements')
        if channel:
            await channel.send(f"**[SYSTEM]** The world has progressed. The time is now {now.strftime('%Y-%m-%d %H:%M:%S')}. The following events occurred while you were away...")
            # Here you could add a more detailed summary of simulated events if desired.