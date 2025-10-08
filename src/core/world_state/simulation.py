import time
from datetime import datetime, timedelta
import asyncio

class SimulationManager:
    """
    Manages the 'Illusion of 24/7' by simulating world events that occurred
    while the bot was offline.
    Codename: 'The Simulation'
    """
    def __init__(self, bot):
        self.bot = bot
        self.last_online_path = "data/last_online.txt"

    def run_offline_simulation(self):
        """Calculates offline time and simulates events for that duration."""
        last_online = self._get_last_online_timestamp()
        now = datetime.now()
        offline_duration = now - last_online

        print(f"Bot was offline for: {offline_duration}")

        if offline_duration > timedelta(minutes=1):
            print("Running offline simulation...")
            self._simulate_time(offline_duration)

        self._update_last_online_timestamp()

    def _get_last_online_timestamp(self):
        """Reads the last online timestamp from a file."""
        try:
            with open(self.last_online_path, 'r') as f:
                return datetime.fromisoformat(f.read().strip())
        except FileNotFoundError:
            return datetime.now()

    def _update_last_online_timestamp(self):
        """Writes the current timestamp to the last online file."""
        with open(self.last_online_path, 'w') as f:
            f.write(datetime.now().isoformat())

    def _simulate_time(self, duration):
        """
        Simulates the passage of time for all bots, affecting their economy and emotions.
        """
        num_hours = duration.total_seconds() / 3600
        if num_hours < 1:
            return # Don't run simulation for very short downtimes

        report_parts = [f"**Waking World Report**\n*The world has progressed by {int(num_hours)} hours while you were away...*\n"]

        for persona in self.bot.persona_manager.get_all_personas():
            # 1. Simulate Job Earnings
            job = self.bot.job_manager.get_character_job(persona.name)
            if job and persona.status != "InServitude":
                earnings = self.bot.job_manager.perform_work(persona.name, num_hours)
                if earnings > 0:
                    self.bot.economy_manager.adjust_balance(persona.name, earnings, f"Offline work ({int(num_hours)} hours)")
                    report_parts.append(f"💼 **{persona.name}** worked as a {job.name} and earned **{earnings:.2f} Rs**.")

            # 2. Simulate Emotional State Decay/Change
            # Loneliness increases over time if alone
            persona.adjust_emotion('loneliness', int(num_hours * 2))
            # Happiness slowly decays
            persona.adjust_emotion('happiness', -int(num_hours))

        # In a real implementation, we would send this to the announcements channel
        # For now, we'll just print it. The bot will be coded to send this.
        final_report = "\n".join(report_parts)
        print(final_report)

        # Schedule the report to be sent after the bot is fully ready
        async def send_report():
            await self.bot.wait_until_ready() # Ensure bot is connected and cache is ready
            await self.bot.send_to_event_channel(final_report)

        # We need to run this in the bot's event loop
        asyncio.run_coroutine_threadsafe(send_report(), self.bot.loop)